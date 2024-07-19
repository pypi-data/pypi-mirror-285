from typing import Any

import numpy as np
import torch
from pandas import DataFrame
from torch import Tensor
from transformers import AutoModelForPreTraining, AutoTokenizer, LogitsProcessor
from typing_extensions import deprecated

from orcalib._orca_utils import (
    bag_of_words_scores,
    extract_occurance_ranks,
    find_suffixes_in_sequence,
)
from orcalib.database import OrcaDatabase


class OrcaGroundingProcessor(LogitsProcessor):
    """
    Logits processor that adjusts the logits based on the memories in the database.
    """

    def __init__(
        self,
        memories: list[list[str]],
        tokenizer: Any,
        bag_weight: float = 0.05,
        sim_weight: float = 0.5,
        S_min: int = 3,
        S_max: int = 10,
    ):
        """
        Initialize the grounding processor.

        Args:
            memories: List of memories
            tokenizer: Tokenizer
            bag_weight: Bag of words weight
            sim_weight: Similarity weight
            S_min: Minimum suffix length
            S_max: Maximum suffix length
        """
        self.memories = memories
        self.bag_weight = bag_weight
        self.sim_weight = sim_weight

        self.tokenizer = tokenizer
        self.S_min = S_min
        self.S_max = S_max

    def _weighted_next_tokens_from_memory(
        self,
        q_tokens: list[int],  # query tokens
        candidates: list[list[int]],
        semantic_scores: list[float],
    ) -> tuple[
        dict[int, float], list[tuple[list[int], float]]
    ]:  # suffix max dict (token -> score), bag_of_words list (token list, score)
        tokens_and_weights: dict[int, float] = {}
        for candidate, semantic_score in zip(candidates, semantic_scores):
            suffixes = find_suffixes_in_sequence(q_tokens, candidate, self.S_min, self.S_max)
            scores = extract_occurance_ranks(suffixes, len(candidate))
            for token, score in scores.items():
                if token not in tokens_and_weights or score > tokens_and_weights[token]:
                    tokens_and_weights[token] = score * semantic_score
        bag_of_words_tokens: list[list[int]] = candidates
        return {token: score for token, score in tokens_and_weights.items()}, list(
            zip(
                bag_of_words_tokens,
                [x / len(candidates) for x in semantic_scores],
                strict=True,
            )
        )

    def __call__(  # type: ignore
        self,
        input_ids: Tensor,
        scores: Tensor,
    ) -> Tensor:
        """
        Adjusts the given scores based on memory and similarity weights

        This method processes each batch of input IDs and their corresponding scores to adjust the scores
        using memory-based and similarity-based adjustments. The final adjusted probabilities are then
        normalized and converted to log probabilities.

        * The similarity and bag-of-words weights (`self.sim_weight` and `self.bag_weight`) are used to
          scale the adjustments.
        * The semantic scores are currently based on exponential decay but can be modified to use scores
          from an approximate nearest neighbor (ANN) search in the future.

        Args:
            input_ids: A tensor of shape (`batch_size`, `sequence_length`) containing input token IDs.
            scores: A tensor of shape (`batch_size`, `vocab_size`) containing the initial scores for each token.

        Returns:
            A tensor of shape (`batch_size`, `vocab_size`) containing the log probabilities after adjustment.
        """
        bs = input_ids.shape[0]
        vocab_size = scores.shape[1]

        bag_adjust = torch.zeros(size=(bs, vocab_size)).to(scores.device)
        sim_adjust = torch.zeros(size=(bs, vocab_size)).to(scores.device)
        for i in range(bs):
            candidates: list[list[int]] = [
                self.tokenizer(self.memories[i][j], add_special_tokens=False).input_ids
                for j in range(len(self.memories[i]))
            ]

            # for now, just exponential decaying weights as memory is lower in position
            # TODO eventually should use the score from ANN
            semantic_scores: list[float] = np.exp(-1 * np.arange(len(self.memories[i]))).tolist()

            input_toks = input_ids[i].tolist()

            sub_candidates, bag_of_words = self._weighted_next_tokens_from_memory(
                q_tokens=input_toks,
                candidates=candidates,
                semantic_scores=semantic_scores,
            )

            bag_adjust_i = bag_of_words_scores(bag_of_words, vocab_size)
            bag_adjust[i] = bag_adjust_i

            for token, score in sub_candidates.items():
                sim_adjust[i, token] = score

        probs = torch.softmax(scores, dim=-1)

        # broadcast/unsqueeze along sequence dimension
        probs = probs + self.sim_weight * sim_adjust + self.bag_weight * bag_adjust

        # renormalize probabilities to sum to 1
        probs = probs / probs.sum(dim=-1, keepdim=True)

        return torch.log(probs)


@deprecated("this isn't used anymore and can probably be remove")
class HFAutoModelWrapper:
    def __init__(
        self,
        db: OrcaDatabase,
        index_name: str,
        model_name: str,
        hf_access_token: str | None = None,
    ):
        self.model_name = model_name
        self._db = db
        self._index_name = index_name
        self.override_memories: DataFrame | None = None
        try:
            self.model = AutoModelForPreTraining.from_pretrained(
                model_name,
                device_map="auto",
                torch_dtype=torch.float16,
            )
        except Exception as e:
            if model_name.startswith("meta-llama/Llama-2"):
                from transformers import LlamaForCausalLM

                self.model = LlamaForCausalLM.from_pretrained(
                    model_name,
                    device_map="auto",
                    torch_dtype=torch.float16,
                    token=hf_access_token,
                )
            else:
                print(e)
                raise NotImplementedError
        # Currently AutoTokenizer works for all models
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, token=hf_access_token)

    def _search_index(self, query: str) -> tuple[str, DataFrame]:
        if self.override_memories is None:
            self.latest_memories = (
                self._db.scan_index(index_name=self._index_name, query=query)
                .select("*", index_value="__segment")  # type: ignore
                .df(10, explode=True)
            )
            res = self.latest_memories.to_dict(orient="records")
            return "\n".join([r["__segment"] for r in res]) + "\n", self.latest_memories
        else:
            return (
                "\n".join([r["__segment"] for r in self.override_memories.to_dict(orient="records")]) + "\n",
                self.override_memories,
            )

    def __call__(self, query: str) -> str:
        context, _ = self._search_index(query)

        input_text = context + "\n\n =================== \n" + query
        input_ids = self.tokenizer(input_text, return_tensors="pt").input_ids.to(self.model.device)  # type: ignore

        outputs = self.model.generate(input_ids, max_new_tokens=50)  # type: ignore
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
