from typing import Callable, Optional

import torch
from torch import Tensor, nn
from torch.nn import functional as F

from orcalib.orca_torch import (
    ClassificationMode,
    ColumnName,
    DropExactMatchOption,
    LabelColumnNameMixin,
    OrcaClassificationCrossAttentionLayer,
    OrcaClassificationMemoryGuideLayer,
    OrcaDatabase,
    OrcaLabelLookupLayer,
    OrcaLookupLayer,
    OrcaLookupModule,
    OrcaMemoryBindingLayer,
    ProjectionMode,
    _GatedMoeHead,
    _LinearClassificationHead,
)


class OrcaKnnClassifier(OrcaLookupModule):
    """A simple KNN layer that returns the average label of the K nearest memories to the input vector.

    Examples:
        ```python
        import torch
        from orcalib import OrcaModule, OrcaKnnClassifier

        class MyModule(OrcaModule):
            def __init__(self):
                super().__init__()
                self.knn_head = OrcaKnnClassifier(
                    memory_index_name="my_index",
                    label_column_name="my_label",
                    num_memories=10,
                    num_classes=5,
                )

            def forward(self, x):
                logits = self.knn_head(x)
                return logits
        ```
    """

    def __init__(
        self,
        num_classes: int,
        num_memories: int,
        label_column_name: ColumnName,
        weigh_memories: bool = True,
        # Shared Settings
        database: OrcaDatabase | str | None = None,
        # Curate Settings
        curate_enabled: bool = False,
        # Lookup Settings
        memory_index_name: str | None = None,
        drop_exact_match: DropExactMatchOption = DropExactMatchOption.TRAINING_ONLY,
        exact_match_threshold: float | None = None,
    ):
        """
        Initialize the classifier.

        Args:
            num_classes: The size of the output vector.
            num_memories: The number of memory vectors to be returned from the lookup.
            weigh_memories: Whether to weigh the memories by their scores.
            database: The OrcaDatabase instance to use for lookups and curate tracking.
            curate_enabled: Whether Curate tracking is enabled.
            memory_index_name: The name of the index to use for lookups.
            drop_exact_match: Choose to drop the exact match (if found) always, never, or only during training or inference.
            exact_match_threshold: Minimum similarity score for something to be considered the exact match
            label_column_name: The name of the label column to return from the index.
        """
        super().__init__(
            database=database,
            curate_enabled=curate_enabled,
            memory_index_name=memory_index_name,
            num_memories=num_memories,
            drop_exact_match=drop_exact_match,
            exact_match_threshold=exact_match_threshold,
            freeze_num_memories=True,
            propagate_lookup_settings=True,
        )

        self.num_classes = num_classes
        self.label_column_name = label_column_name
        self.weigh_memories = weigh_memories

        self.lookup = OrcaLookupLayer(
            lookup_column_names=["$score", label_column_name] if weigh_memories else [label_column_name],
            memory_index_name=memory_index_name,
        )

    def forward(
        self,
        x: Tensor | None = None,
        ctx_labels: Tensor | None = None,
        ctx_scores: Tensor | None = None,
    ) -> Tensor:
        """
        Generate logits based on the nearest neighbors of the input vector.

        Args:
            x: The input tensor of shape (`batch_size`, `embedding_dim`), can be omitted if labels and scores are provided directly.
            ctx_labels: The memory label tensor of shape (`batch_size`, `num_memories`) contains integer labels.
                If this is `None`, the labels will be looked up from the index based on the input tensor.
            ctx_scores: The memory score tensor of shape (`batch_size`, `num_memories`) contains float scores.
                If this is `None`, the scores will be looked up from the index based on the input tensor.

        Returns:
            The output tensor of shape (`batch_size`, `num_classes`), if neither x nor scores are
                provided the `dtype` will be `float32`, otherwise it will be the same as the scores or input tensor.
        """
        if ctx_labels is None or ctx_scores is None:
            assert (
                ctx_labels is None and ctx_scores is None
            ), "Both labels and scores must be None or neither should be None"
            if x is None:
                raise ValueError("Input tensor must be provided if labels abd scores are not")
            result = self.lookup(x)
            ctx_labels = result.to_tensor(self.label_column_name, dtype=torch.int64, device=x.device).squeeze(-1)
            assert isinstance(ctx_labels, Tensor)
            if self.weigh_memories:
                ctx_scores = result.to_tensor("$score", dtype=x.dtype, device=x.device).squeeze(-1)

        with torch.no_grad():
            if self.weigh_memories:
                if ctx_scores is None:
                    raise ValueError("Labels and scores must be provided when weighing memories")
                logits = torch.zeros(
                    ctx_scores.shape[0], self.num_classes, device=ctx_scores.device, dtype=ctx_scores.dtype
                )  # N x C
                logits.scatter_add_(1, ctx_labels, ctx_scores)
                logits /= logits.sum(dim=1, keepdim=True)
            else:
                one_hot_labels = (
                    F.one_hot(ctx_labels, num_classes=self.num_classes)
                    .to(x.dtype if x is not None else torch.float32)
                    .to(ctx_labels.device)
                )  # N x K x C
                logits = one_hot_labels.sum(dim=1) / torch.tensor(self.num_memories, device=ctx_labels.device)  # N x C
            return logits


class OrcaClassificationHead(
    OrcaLookupModule, LabelColumnNameMixin
):  # Input: single vector of size hidden_size, optional memory context (otherwise looked up), Output: single vector of size num_labels
    """A transformer decoder layer block that does cross attention with memory lookup

    Examples:
        ```py
        import torch
        from orcalib.orca_torch import OrcaModule, OrcaClassificationHead

        class MyModule(OrcaModule):
            def __init__(self):
                super().__init__()
                self.trunk = torch.nn.Linear(10, 10)
                self.classifier = OrcaClassificationHead(model_dim=10, num_classes=5, "my_index", "my_label", num_memories=10)

            def forward(self, x):
                x = self.trunk(x) # N x 10
                x = self.classifier(x)
                return x # N x 5, e.g., where each row may become logits for a softmax
        ```
    """

    def __init__(
        self,
        model_dim: int,
        num_classes: int,
        num_memories: int,
        num_layers: int = 1,
        num_heads: int = 8,
        classification_mode: ClassificationMode = ClassificationMode.DIRECT,
        activation: Callable[[Tensor], Tensor] = F.relu,
        dropout: float = 0.1,
        deep_residuals: bool = True,
        split_retrieval_path: bool = False,
        memory_guide_weight: float = 0.0,
        single_lookup: bool = True,
        # Shared Settings
        database: OrcaDatabase | str | None = None,
        # Curate Settings
        curate_enabled: bool = False,
        # Lookup Settings
        memory_index_name: str | None = None,
        drop_exact_match: DropExactMatchOption | None = None,
        exact_match_threshold: float | None = None,
        shuffle_memories: bool = False,
        label_column_name: ColumnName | None = None,
    ):
        """
        Initialize the classifier.

        Args:
            model_dim: The dimension of the input vector and hidden layers.
            num_classes: The size of the output vector.
            num_memories: The number of memory vectors to be returned from the lookup.
            num_layers: The number of attention blocks to be used, copies of [`OrcaClassificationCrossAttentionLayer`][orcalib.orca_classification.OrcaClassificationCrossAttentionLayer].
            num_heads: The number of heads to be used in the multi-head attention layer.
            classification_mode: The mode of classification to be used.
            activation: The activation function.
            dropout: The dropout rate.
            deep_residuals: Whether to use deep residuals.
            split_retrieval_path: Whether to split the retrieval path.
            memory_guide_weight: The weight of the memory guide.
            single_lookup: Whether to use a single lookup.
            database: The `OrcaDatabase` instance to use for lookups and curate tracking.
            curate_enabled: Whether Curate tracking is enabled.
            memory_index_name: The name of the index to use for lookups.
            drop_exact_match: Choose to drop the exact match (if found) always, never, or only during training or inference.
            exact_match_threshold: Minimum similarity score for something to be considered the exact match
            shuffle_memories: Whether to shuffle the memories before returning them.
            label_column_name: The name of the label column to return from the index.
        """
        super().__init__(
            database=database,
            curate_enabled=curate_enabled,
            memory_index_name=memory_index_name,
            lookup_column_names=None,
            num_memories=num_memories,
            drop_exact_match=drop_exact_match,
            exact_match_threshold=exact_match_threshold,
            shuffle_memories=shuffle_memories,
            freeze_num_memories=True,
            propagate_lookup_settings=True,
        )

        self.classification_mode = classification_mode
        self.model_dim = model_dim
        self.num_classes = num_classes
        self.activation = activation

        self.dropout = dropout
        self.deep_residuals = deep_residuals
        self.split_retrieval_path = split_retrieval_path
        self.memory_guide_weight = memory_guide_weight
        self.single_lookup = single_lookup
        self.label_column_name = label_column_name

        if classification_mode == ClassificationMode.MEMORY_BOUND:
            self.projection_mode = ProjectionMode.POSITIONAL
            # Lookup settings will be automatically propagated to the lookup layer
            self.memory_binding = OrcaMemoryBindingLayer(
                num_memories=num_memories,
                num_classes=num_classes,
            )
            if num_memories is None:
                raise ValueError("must provide num_memories for memory-bound classification mode")
            self.inner_classes = self.num_memories
        elif classification_mode == ClassificationMode.DIRECT:
            self.projection_mode = ProjectionMode.LABEL
            self.memory_binding = torch.nn.Identity()
            self.inner_classes = self.num_classes
        else:
            raise ValueError(f"Unrecognized classification mode: {self.classification_mode}")

        # Lookup settings will be automatically propagated to the lookup layer
        self.lookup = OrcaLabelLookupLayer()

        self.classification_mode = classification_mode

        self.memory_layers = nn.ModuleList(
            (
                # Lookup settings will be automatically propagated this layer
                OrcaClassificationCrossAttentionLayer(
                    model_dim=model_dim,
                    num_heads=num_heads,
                    num_classes=self.inner_classes,
                    num_memories=num_memories,
                    dropout=dropout,
                    activation=activation,
                    projection_mode=self.projection_mode,
                    split_retrieval_path=split_retrieval_path,
                    database=database,
                )
                for _ in range(num_layers)
            )
        )

        self.num_layers = num_layers
        self.classifier = _LinearClassificationHead(
            model_dim=model_dim, num_labels=self.inner_classes, activation=activation, dropout=dropout
        )

        self._memory_enabled = True
        # Lookup settings will be automatically propagated to the lookup layer
        self.guide = OrcaClassificationMemoryGuideLayer(
            num_classes=num_classes,
            num_memories=num_memories,
            guide_weight=memory_guide_weight,
            database=database,
        )

    def forward(
        self,
        x: Tensor,
        ctx: Tensor | None = None,
        labels: Tensor | None = None,
        memory_key: Tensor | None = None,
    ) -> Tensor:  # x is the input vector N x D, ctx is the memory context N x K x D
        """
        Generate logits based on the input vector and memory context.

        Args:
            x: The input tensor of shape (`batch_size`, `embedding_dim`)
            ctx: The memory context tensor of shape (`batch_size`, `num_memories`, `embedding_dim`).
                If `None`, the memory context will be looked up based on the `memory_key` or input tensor.
            labels: The memory label tensor of shape (`batch_size`, `num_memories`) containing integer labels.
                If `None`, the labels will be looked up from the index based on the `memory_key` or input tensor.
            memory_key: The memory key tensor of shape (`batch_size`, `embedding_dim`) to use for
                lookup. If `None`, the input tensor will be used.

        Returns:
            The logits tensor of shape (`batch_size`, `num_classes`)
        """
        if (ctx is None or labels is None) and self.single_lookup:
            assert labels is None and ctx is None, "Both labels and ctx must be None or neither"
            if memory_key is None:
                memory_key = x
            ctx, labels = self.lookup(memory_key)
        inpt = x
        if self._memory_enabled:
            for layer in self.memory_layers:
                y = layer(x, ctx, labels, memory_key)
                if self.deep_residuals:
                    x = y + x
                else:
                    x = y
        x = self.classifier(x)
        if self.classification_mode == ClassificationMode.MEMORY_BOUND:
            x = self.memory_binding(x, inpt, ctx, labels)
        if self.memory_guide_weight > 0.0:
            x = self.guide(x, memory_key or inpt, ctx, labels)
        return x

    def _orca_memory_toggle(self, enable: bool) -> None:
        """Toggles the memory guide layer on or off."""
        self._memory_enabled = enable


class OrcaMoeClassificationHead(OrcaLookupModule):
    """
    A mixture of experts classification head that combines a KNN classifier with a linear classifier.

    Examples:
        ```py
        import torch
        from orcalib import OrcaModel, OrcaMoeClassificationHead

        class MyModule(OrcaModel):
            def __init__(self):
                super().__init__()
                self.trunk = torch.nn.Linear(10, 10)
                self.classifier = OrcaMoeClassificationHead(model_dim=10, num_classes=5, num_memories=10)

            def forward(self, x):
                x = self.trunk(x)
                x = self.classifier(x)
                return x
        ```
    """

    def __init__(
        self,
        model_dim: int,
        num_classes: int,
        num_memories: int,
        label_column_name: ColumnName,
        gate_layers: int = 1,
        hidden_layers: int = 0,
        activation: Callable[[Tensor], Tensor] = F.relu,
        dropout: float = 0.1,
        # Shared Settings
        database: OrcaDatabase | str | None = None,
        # Curate Settings
        curate_enabled: bool = False,
        # Lookup Settings
        memory_index_name: str | None = None,
        drop_exact_match: DropExactMatchOption = DropExactMatchOption.TRAINING_ONLY,
        exact_match_threshold: float | None = None,
    ):
        """
        Initialize the classifier.

        Args:
            model_dim: The dimension of the input vector and hidden layers.
            num_classes: The size of the output vector.
            num_memories: The number of memory vectors to be returned from the lookup.
            label_column_name: The name of the label column to return from the index.
            gate_layers: The number of layers to use in the gating network.
            hidden_layers: The number of hidden layers to use in the linear classifier.
            activation: The activation function.
            dropout:The dropout rate.
            database: The OrcaDatabase instance to use for lookups and curate tracking.
            curate_enabled: Whether Curate tracking is enabled.
            memory_index_name: The name of the index to use for lookups.
            drop_exact_match: Choose to drop the exact match (if found) always, never, or only during training or inference.
            exact_match_threshold: Minimum similarity score for something to be considered the exact match
        """
        super().__init__(
            database=database,
            curate_enabled=curate_enabled,
            memory_index_name=memory_index_name,
            num_memories=num_memories,
            drop_exact_match=drop_exact_match,
            exact_match_threshold=exact_match_threshold,
            freeze_num_memories=True,
            propagate_lookup_settings=True,
        )
        self.gate = _GatedMoeHead(model_dim, gate_layers)

        self.knn_classifier = OrcaKnnClassifier(
            memory_index_name=memory_index_name,
            num_memories=num_memories,
            label_column_name=label_column_name,
            num_classes=num_classes,
            drop_exact_match=drop_exact_match,
        )

        self.ff_classifier = nn.Sequential(
            *[
                nn.Sequential(nn.Linear(model_dim, model_dim), nn.ReLU(), nn.LayerNorm(model_dim))
                for _ in range(hidden_layers)
            ],
            _LinearClassificationHead(
                model_dim=model_dim, num_labels=num_classes, activation=activation, dropout=dropout
            ),
        )

    def forward(self, x: Tensor, ctx_scores: Tensor | None = None, ctx_labels: Tensor | None = None) -> Tensor:
        """
        Generate logits based on the input vector and memory context.

        Args:
            x: The input tensor of shape (`batch_size`, `embedding_dim`).
            ctx_scores: The memory scores tensor of shape (`batch_size`, `num_memories`).
                If this is `None`, the scores will be looked up from the index based on the input tensor.
            ctx_labels: The memory labels tensor of shape (`batch_size`, `num_memories`).
                If this is `None`, the labels will be looked up from the index based on the input tensor

        Returns:
            The logits tensor of shape (`batch_size`, `num_classes`).
        """
        knn_logits = self.knn_classifier(x, ctx_labels, ctx_scores)
        ff_logits = self.ff_classifier(x)

        return self.gate(x, knn_logits, ff_logits)
