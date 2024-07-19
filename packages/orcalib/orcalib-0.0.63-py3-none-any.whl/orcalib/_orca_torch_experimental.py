import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor


class ScoreWeightedLabels(nn.Module):
    """Layer that learns to weight the labels of the neighbors based on their scores and a learned threshold.
    The threshold effectively zeroes out the weights of the neighbors that are not similar enough to the input.

    NOTE: This layer doesn't have its own lookup layer; it expects the input to be the output of a lookup layer.
    NOTE: This layer DOES NOT have unit or integration tests. It is experimental and should be used with caution.

    Example usage:
    ```
    def __init__(self):
      super().__init__()
      self.lookup = OrcaLookupLayer(lookup_column_names=["label_column", "$score"], num_memories=NUM_MEMORIES)
      self.score_weighted_labels = ScoreWeightedLabels(num_labels=LABEL_COUNT, hidden_dim=HIDDEN_DIM)

    def forward(self, x):
      results: BatchedScanResult = self.lookup(x)
      neighbor_scores = results.to_tensor("$score").float()
      neighbor_labels = results.to_tensor("label_column")
      neighbor_labels = F.one_hot(neighbor_labels, num_classes=self.num_labels).float()

      knn = self.score_weighted_labels(x, neighbor_scores, neighbor_labels)
    ```
    """

    def __init__(
        self,
        num_labels,
        hidden_dim,
    ):
        """
        Args:
            num_labels: The number of labels that the neighbors can
                have.
            hidden_dim: The width of the inputs to the threshold layer.
        """
        super().__init__()

        self.num_labels = num_labels
        self.hidden_dim = hidden_dim

        self.threshold = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.BatchNorm1d(hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1),
        )
        self.threshold.apply(self._initialize_weights)

    @staticmethod
    def _initialize_weights(m):
        """Used to initialize the weights of the linear layers."""
        if isinstance(m, nn.Linear):
            nn.init.xavier_uniform_(m.weight)
            nn.init.constant_(m.bias, 0)

    def forward(
        self,
        x: Tensor,  # (batch_size, hidden_dim)
        neighbor_scores: Tensor,  # (batch_size, num_memories)
        neighbor_labels: Tensor,  # (batch_size, num_memories, num_labels)
    ):
        """
        Args:
            x: Tensor with shape (batch_size, hidden_dim). The threshold
                is computed based on this tensor.
            neighbor_scores: Tensor with shape (batch_size,
                num_memories). These are the similarity scores for each
                memory.
            neighbor_labels: Tensor with shape (batch_size,
                num_memories, num_labels). These are the 1-hot encoded
                labels of the neighbors. These labels will be combined
                based on the scores and a learned threshold.
        """
        threshold = self.threshold(x)  # (batch_size, 1)
        weights = torch.sigmoid(neighbor_scores - threshold)  # (batch_size, num_memories)
        weights = weights / (weights.sum(dim=1, keepdim=True) + 1e-8)  # (batch_size, num_memories)

        weighted_avg = torch.bmm(weights.unsqueeze(1), neighbor_labels)  # (batch_size, 1, num_labels)
        weighted_avg = weighted_avg.squeeze(1)  # (batch_size, num_labels)
        return weighted_avg


class OracleLayer(nn.Module):
    """Accepts multiple options and a label, and returns the option that is closest to the label.

    NOTE: This layer DOES NOT have unit or integration tests. It is experimental and should be used with caution.
    NOTE: This layer doesn't have its own lookup layer, although it's likely you'll want to use one before this layer.

    Example usage:
    ```

    def __init__(self):
        super().__init__()

        self.expert1 = ... # Some expert layer
        self.expert2 = ... # Another expert layer

        self.oracle = OracleLayer(num_labels=LABEL_COUNT, hidden_dim=HIDDEN_DIM)

    def forward(self, x, labels):
        neighbor_labels = self.lookup(x)

        expert1_logits = self.expert1(x)
        expert2_logits = self.expert2(x)

        oracle = self.oracle(labels, expert1_logits, expert2_logits)
    ```
    """

    def __init__(self, weights=None):
        """
        Args:
            weights: The weights to use for the cross entropy loss. If
                None, the loss will be unweighted.
        """
        super().__init__()
        self.ce_loss = nn.CrossEntropyLoss(weight=weights)

    def forward(self, labels: Tensor, *logits: Tensor):  # (batch_size)  # (batch_size, num_labels)
        """If there is a correct prediction, the expert that made the correct prediction is used. If there is no correct
        prediction, the expert with the highest confidence is used.

        Args:
            labels: Tensor with shape (batch_size). The ACTUAL integer
                label of the batch elements.
            *logits: Tensors with shape (batch_size, num_labels). These
                are the logits for each different prediction
        """

        batch_size = labels.size(0)
        num_labels = logits[0].size(1)

        stacked_logits = torch.stack(logits, dim=2)  # (batch_size, num_labels, num_logits)

        predictions = torch.argmax(stacked_logits, dim=1)  # (batch_size, num_logits)
        correct_predictions = (predictions == labels.unsqueeze(1)).float()  # (batch_size, num_logits)

        effective_logits = torch.zeroes((batch_size, num_labels), device=labels.device)  # (batch_size, num_labels)
        for i in range(batch_size):
            if correct_predictions[i].any():
                # If there is a correct prediction, use the expert that made the correct prediction.
                best_expert = correct_predictions[i].nonzero(as_tuple=True)[0][0].item()
            else:
                # If there is no correct prediction, use the expert with the highest confidence.
                best_expert = torch.argmax(stacked_logits[i, labels[i]]).item()
            effective_logits[i] = stacked_logits[i, :, best_expert]

        return effective_logits
