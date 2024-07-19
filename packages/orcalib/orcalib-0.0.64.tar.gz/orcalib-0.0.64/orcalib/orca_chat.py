from dataclasses import dataclass
from threading import Thread
from typing import Any, Optional

import torch
import torch.nn as nn
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    LogitsProcessorList,
    PreTrainedModel,
    PreTrainedTokenizerBase,
    TextIteratorStreamer,
)

from orcalib.database import OrcaDatabase
from orcalib.hf_utils import OrcaGroundingProcessor
from orcalib.orca_torch import OrcaLookupLayer, OrcaMetadataDict, OrcaModel, OrcaModule
from orcalib.orca_types import TextT

orca_llama_system_prompt = """You are a helpful and direct assistant.
You should try to be as direct and succinct as possible.
You will be provided with context to help answer user queries.
Some of the context may or may not be useful.
If it is, be as true to the context as possible, with priority in order of the context.
If it is not, say you cannot answer or do not know.
DO NOT MENTION THE CONTEXT OR TALK ABOUT UNRELATED ENTITIES IN THE CONTEXT.
Potentially useful context:"""


class OrcaChat(OrcaModel):
    """
    A basic wrapper for a chatbot model that uses Orca for memory retrieval,
    and a base model with a generate method for response generation.
    """

    def __init__(
        self,
        num_memories: int = 20,
        model: str | PreTrainedModel | torch.nn.Module = "facebook/opt-350m",
        mode: str = "chat",
        use_rag: bool = False,
        use_ground: bool = False,
        max_context_length: int = 4096,
        tokenizer=None,
        database: OrcaDatabase | str | None = None,
        # Curate Settings
        model_id: str = "orca_public_chatbot_v0",
        model_version: str | None = None,
        metadata: OrcaMetadataDict | None = None,
        curate_enabled: bool = False,
        tags: set[str] | None = None,
        # Memory Lookup Settings
        memory_index_name: str | None = None,
        lookup_column_names: list[str] | None = None,
        propagate_lookup_settings: bool = True,
        **kwargs,
    ):
        """
        Initialize the Orca augmented chat model

        Args:
            database: The database to use for memory retrieval
            memory_index_name: The name of the index to use for memory retrieval
            lookup_column_names: The names of the columns to retrieve for each memory
            num_memories: The number of memories to retrieve

            model: The model to use for response generation
            mode: The mode of the chatbot
            use_rag: Whether to use RAG for response generation
            use_ground: Whether to use grounding for response generation
            max_context_length: The maximum context length for response generation
            tokenizer: The tokenizer to use for response generation
            kwargs: Additional keyword arguments to pass to the model

            model_id: The name for the model for curate tracking of model runs
            model_version: The version of the model for curate tracking of model runs
            metadata: The metadata for the model for curate tracking of model runs
            curate_enabled: Whether to enable curate tracking of model runs
            tags: The tags for the model for curate tracking of model runs
        """
        super().__init__(
            database=database,
            model_id=model_id,
            model_version=model_version,
            metadata=metadata,
            curate_enabled=curate_enabled,
            tags=tags,
            memory_index_name=memory_index_name,
            lookup_column_names=lookup_column_names,
            num_memories=num_memories,
            propagate_lookup_settings=propagate_lookup_settings,
        )

        self.use_rag = use_rag
        self.use_ground = use_ground

        if use_rag:
            # Lookup settings will be automatically propagated to this layer
            self.lookup = OrcaLookupLayer()
        else:
            self.lookup = None

        if isinstance(model, str):
            self.model = AutoModelForCausalLM.from_pretrained(model, **kwargs)
            self.tokenizer = AutoTokenizer.from_pretrained(
                model,
                use_default_system_prompt=True if not use_rag else False,
                **kwargs,
            )

        elif isinstance(model, PreTrainedModel) or isinstance(model, torch.nn.Module):
            assert hasattr(model, "generate")
            assert isinstance(tokenizer, PreTrainedTokenizerBase)
            self.tokenizer = tokenizer
            self.model = model

        self.streamer = TextIteratorStreamer(
            tokenizer=self.tokenizer,  # type: ignore
            skip_special_tokens=True,
            skip_prompt=True,
            timeout=120.0,
        )

        self.model_id = model_id
        self.mode = mode
        if self.use_rag:
            self.chat_history = [
                {
                    "role": "system",
                    "content": orca_llama_system_prompt,
                }
            ]
        else:
            self.chat_history = []
        self.ui_history = []
        self.lookup_history = []
        self.last_user_input = None
        self.max_context_length = max_context_length
        self.last_retrieval_query = None
        self.last_model_input = None
        self.last_accessed_memories: list[list[Any]] | None = None
        self.text_memories: list[list[str]] = []
        self.sim_weight = 0.0
        self.bag_weight = 0.0

    def _determine_retrieval_query(self) -> str:
        """
        Determine the retrieval query based on the last user input and other context.
        Currently, this just combines all user inputs into a single query.
        """
        if self.mode == "StatelessQA":
            return " ".join([msgs["content"] if msgs["role"] == "user" else "" for msgs in [self.chat_history[-1]]])
        else:
            return " ".join([obj["content"] if obj["role"] == "user" else "" for obj in self.chat_history])

    def prep_next_gen(self, last_user_input: str) -> tuple[str, list[list[str]], list[list[Any]] | None]:
        """
        Prepares the next generation by updating the chat history and last user input.

        Args:
            last_user_input: The last user input

        Returns:
            input: The last user input
            ui_history: The list of user input and system responses
            last_accessed_memories: The last accessed memories
        """
        if self.mode == "StatelessQA":
            self.clear_chat()

        self.last_user_input = last_user_input
        self.chat_history.append({"role": "user", "content": last_user_input})
        self.ui_history.append([last_user_input, None])

        retrieval_query = self._determine_retrieval_query()
        if self.use_rag:
            context = self.retrieve(retrieval_query)

            # modify the system prompt with new memories
            self.chat_history[0] = {
                "role": "system",
                "content": orca_llama_system_prompt + self.format_context(context) + "\n",
            }

        self.last_retrieval_query = retrieval_query

        return "", self.ui_history, self.last_accessed_memories

    def retrieve(self, query: str) -> list[str]:
        """
        Retrieve memories from the database based on the query.

        Args:
            query: The query to retrieve memories for

        Returns:
            list of retrieved memories
        """

        if self.lookup is None:
            return []

        # Because we're not doing the lookup as part of a forward() call from the
        # model, we need to manually setup the curate details.
        self.lookup.curate_batch_size = 1
        self.curate_layer_name = "OrcaLookupLayer"
        self.record_next_model_memory_lookups()

        payload = self.lookup([query])[0]
        memory_texts = []
        for doc in payload:
            # the first element is the vector, the second is the meta
            memory_texts.append(doc[1])

        self.last_accessed_memories = payload.df()
        self.text_memories = memory_texts
        self.lookup_history.append(memory_texts)

        return memory_texts

    def gen_response(self, ui_history) -> None:
        """
        Generate a response based on the last user input and the current context.

        Args:
            ui_history: The list of user input and system responses
        """
        if self.mode == "chat" or self.mode == "StatelessQA":
            formatted_query = self.tokenizer.apply_chat_template(self.chat_history, tokenize=False)
            # Ensure formatted_query is a string to satisfy the type checker and for runtime safety.
            if not isinstance(formatted_query, str):
                raise ValueError("Expected formatted_query to be a string when tokenize=False.")
        else:
            raise NotImplementedError(f"Mode {self.mode} not supported by OrcaChat.gen_response()")

        self.last_model_input = formatted_query
        input_ids = self.tokenizer(formatted_query, return_tensors="pt", max_length=self.max_context_length).to(
            self.model.device
        )

        if self.use_ground:
            grounding_processor = OrcaGroundingProcessor(
                memories=self.text_memories,
                tokenizer=self.tokenizer,
                sim_weight=self.sim_weight,
                bag_weight=self.bag_weight,
            )

            postproc_list = LogitsProcessorList([grounding_processor])
        else:
            postproc_list = LogitsProcessorList([])

        def gen_then_ack() -> None:
            """
            Generate then acknowledge.
            """
            self.model.generate(
                **input_ids,  # type: ignore
                max_length=self.max_context_length,
                num_return_sequences=1,
                streamer=self.streamer,
                logits_processor=postproc_list,
            )

        t1 = Thread(target=gen_then_ack)
        t1.start()

        gen_text_stream = ""
        for next_tok in self.streamer:
            gen_text_stream += next_tok
            self.ui_history[-1][1] = gen_text_stream
            yield self.ui_history

        self.chat_history.append(
            {
                "role": "assistant",
                "content": gen_text_stream,
            }
        )

        if self.lookup is not None:
            self.record_model_input_output(*self.ui_history[-1])

    def clear_chat(self) -> None:
        """
        Reset the `ui_history`, `chat_history`, and `lookup_history` attributes.
        """
        self.lookup_history = []
        if self.use_rag:
            self.chat_history = [
                {
                    "role": "system",
                    "content": None,
                }
            ]
        else:
            self.chat_history = []
        self.ui_history = []

    def format_context(self, memories: list[str]) -> str:
        """
        String format memories for prompt injection to model

        Args:
            memories: The memories to format

        Returns:
            The formatted context
        """
        context = ""
        for i, memory in enumerate(memories):
            context += f"\n\n{i + 1}. {memory}"

        return context

    def update_grounding_params(self, sim_weight: float, bag_weight: float) -> None:
        """
        Update the grounding parameters for the OrcaGroundingProcessor.

        Args:
            sim_weight: The similarity weight
            bag_weight: The bag weight
        """
        self.sim_weight = sim_weight
        self.bag_weight = bag_weight

    def switch_config(
        self,
        database_name: str | None,
        index_name: str | None,
        lookup_column_names: list[str] | None,
        num_memories: int | None,
    ) -> None:
        """
        Switch the OrcaLookupConfig for the OrcaChat instance, clearing the chat history.

        Note:
            The settings will be propagated to the OrcaLookupLayer, if it exists.

        Args:
            database_name: The name of the database to use for memory retrieval
            index_name: The name of the index to use for memory retrieval
            lookup_column_names: The names of the columns to retrieve for each memory
            num_memories: The number of memories to retrieve
        """

        if database_name is not None:
            self.lookup_database = database_name
        if index_name is not None:
            self.memory_index_name = index_name
        if lookup_column_names is not None:
            self.lookup_column_names = lookup_column_names
        if num_memories is not None:
            self.num_memories = num_memories

        self.clear_chat()

    def print_chat_log(self) -> None:
        """
        Print the chat log
        """
        print("*" * 80)
        print("*" * 30 + "Last Input to Model:" + "*" * 30)
        print(self.last_model_input)
        print("*" * 30 + "I/O to GR Interface:" + "*" * 30)
        print(self.ui_history)
        print("*" * 80)
        print("*" * 30 + "Last Query for Orca:" + "*" * 30)
        print(self.last_retrieval_query)
        print("*" * 80)
        print("*" * 30 + "Most Recent Memories:" + "*" * 29)
        print(self.last_accessed_memories)
        print("*" * 80)
