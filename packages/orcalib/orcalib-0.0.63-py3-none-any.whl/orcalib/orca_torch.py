import itertools
import logging
import os
import pickle
import time
from collections import defaultdict, deque
from dataclasses import asdict
from typing import Any, Callable, Iterable, Iterator, Literal, TypeVar, cast, final
from uuid import UUID

import torch
import torch.nn as nn
import torch.nn.functional as F
from pandas import DataFrame
from torch import Tensor
from torch.utils.data import DataLoader, Dataset
from tqdm.auto import tqdm
from typing_extensions import deprecated

from orca_common import EXACT_MATCH_THRESHOLD, ColumnName, EmbeddingModel
from orcalib.batched_scan_result import BatchedScanResult
from orcalib.client import OrcaClient, PagedResponse
from orcalib.curate._tracking import (
    FeedbackKind,
    generate_run_ids,
    record_model_feedback,
    record_model_input_output,
)
from orcalib.database import OrcaDatabase
from orcalib.orca_expr import ColumnHandle
from orcalib.orca_torch_mixins import (
    ClassificationMode,
    CurateModelRunSettings,
    CurateSettingsMixin,
    DatabaseIndexName,
    DropExactMatchOption,
    LabelColumnNameMixin,
    LookupSettingsMixin,
    LookupSettingsSummary,
    OrcaMetadataDict,
    PostInitMixin,
    PreForwardMixin,
    ProjectionMode,
)
from orcalib.table import TableHandle

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ORCA_MODULE_TYPE = TypeVar("ORCA_MODULE_TYPE", bound="OrcaModule")

########################
### Orca PyTorch Layers
########################


class OrcaModule(nn.Module, CurateSettingsMixin):
    """
    OrcaModule is a special [PyTorch Module][torch.nn.Module] that support tracking curate data
    during forward passes. It is the base class for all Orca PyTorch layers.

    Note:
        Curate setting propagation is handled by the [`OrcaModel`][orcalib.orca_torch.OrcaModel]
        (model, not module) class, which recursively sets the curate settings for all children of
        the model to use the same instance of the curate settings object.
    """

    def __init__(
        self,
        curate_database: OrcaDatabase | str | None = None,
        model_id: str | None = None,
        model_version: str | None = None,
        metadata: OrcaMetadataDict | None = None,
        curate_enabled: bool = False,
        tags: Iterable[str] | None = None,
    ):
        """
        Initializes the module with the specified Curate settings.

        Args:
            curate_database: The OrcaDatabase instance to use for Curate tracking.
            model_id: The ID of the model.
            model_version: The version of the model.
            metadata: The metadata to be stored with Curate runs.
            curate_enabled: Whether Curate tracking is enabled.
            tags: The tags to be included in Curate runs.
        """
        nn.Module.__init__(self)
        CurateSettingsMixin.__init__(
            self,
            curate_database=curate_database,
            model_id=model_id,
            model_version=model_version,
            metadata=metadata,
            curate_enabled=curate_enabled,
            tags=tags,
        )

    def __hash__(self):
        return id(self)

    def get_orca_modules_recursively(
        self,
        max_depth: int | None = None,
        include_self: bool = True,
        filter_type: type[ORCA_MODULE_TYPE] | None = None,
    ) -> Iterator[ORCA_MODULE_TYPE]:
        """
        Recursively yields all children of this module that are instances of the specified filter type.

        * All parent nodes will be processed before their children
        * This will search through all children ---even those that are not a subclass of
        the `filter_type`--- but it only returns children that are a subclass of `filter_type`.

        Args:
            max_depth: The maximum depth to search.

                * Setting this to `0` will only include this module.
                * Setting this to `1` will include only this module and its children.
                * Setting it to `None` (the default) will search through all modules.
                * Modules that are not of `filter_type or OrcaModule` do not increment the depth.

            include_self: Whether to include the current OrcaModule in the results.
            filter_type: The subtype of `OrcaModule` to filter for. If `None`, any subtypes of
                `OrcaModule` will be returned.

        Yields:
            modules of type `filter_type` that are used in the children of this module.
        """
        unvisited = deque([self])
        node_depth: dict[nn.Module, int] = dict({self: 0})

        filter_type = filter_type or OrcaModule

        while unvisited:
            parent = unvisited.popleft()
            if isinstance(parent, filter_type) and (include_self or parent != self):
                yield parent

            # We only want to increment the depth if there is no parent or it's an instance of the filter type
            if parent is None or isinstance(parent, filter_type):
                next_depth = node_depth[parent] + 1
            else:
                next_depth = node_depth[parent]

            if max_depth is not None and next_depth > max_depth:
                continue
            for child in parent.children():
                node_depth[child] = next_depth
                unvisited.append(child)  # type: ignore

    def enable_curate(self, recursive: bool = True):
        """
        Enable Curate tracking for the model and (if recursive is True) for all its descendants.

        Args:
            recursive: Whether to enable Curate tracking recursively.
        """
        if not recursive:
            self.curate_enabled = True
            return
        for child in self.get_orca_modules_recursively():
            child.curate_enabled = True

    def disable_curate(self, recursive: bool = True):
        """
        Disable Curate tracking for this module and (if recursive is True) for all its descendants.

        Args:
            recursive: Whether to disable Curate tracking recursively.
        """
        if not recursive:
            self.curate_enabled = False
            return
        for child in self.get_orca_modules_recursively():
            child.curate_enabled = False

    def update_curate_settings(
        self,
        model_id: str | None = None,
        model_version: str | None = None,
        tags: Iterable[str] | None = None,
        extra_tags: Iterable[str] | None = None,
        metadata: OrcaMetadataDict | None = None,
        extra_metadata: OrcaMetadataDict | None = None,
        batch_size: int | None = None,
        seq_id: UUID | None = None,
        enabled: bool | None = None,
        enable_recursive: bool = True,
    ) -> None:
        """
        Update curate tracking settings for the module and all its children.

        Args:
            model_id: The ID of the model.
            model_version: The version of the model.
            tags: The new tags to be added to the model.
            extra_tags: The extra tags to be added to the model.
            metadata: The new metadata to be added to the model.
            extra_metadata: The extra metadata to be added to the model.
            batch_size: The batch size to be used for the model.
            seq_id: The sequence ID to be used for the model.
        """

        self.curate_model_id = model_id or self.curate_model_id
        self.curate_model_version = model_version or self.curate_model_version
        self.curate_tags = tags if tags is not None else self.curate_tags
        if extra_tags:
            self.curate_tags |= set(extra_tags)
        self.curate_metadata = metadata if metadata is not None else self.curate_metadata
        if extra_metadata:
            self.curate_metadata.update(extra_metadata)
        self.curate_batch_size = batch_size or self.curate_batch_size
        self.curate_seq_id = seq_id or self.curate_seq_id
        if enabled is not None:
            self.curate_enabled = enabled
            if enable_recursive:
                for child in self.get_orca_modules_recursively(include_self=False):
                    child.curate_enabled = enabled

    def record_next_model_memory_lookups(
        self,
        tags: Iterable[str] | None = None,
        metadata: OrcaMetadataDict | None = None,
        batch_size: int | None = None,
        seq_id: UUID | None = None,
    ) -> None:
        """
        Sets up curate tracking for the memory lookups during the next forward pass only.

        Args:
            tags: Additional tags to be recorded on the next model run.
            metadata: Additional metadata to be recorded on the next model run.
            batch_size: The batch size to be used for the next model run.
            seq_id: The sequence ID to be used for the next model run.
        """
        if self.training:
            raise ValueError("Memory lookups can only be recorded during evaluation")
        self.curate_next_run_settings = CurateModelRunSettings(
            tags=set(tags) if tags else set(),
            metadata=metadata if metadata else {},
            batch_size=batch_size,
            seq_id=seq_id,
        )

    def _infer_batch_size(*args: Any, **kwargs: Any) -> int:
        """
        Attempts to infer the batch size from the model's input arguments.

        Args:
            args: The positional arguments.
            kwargs: The keyword arguments.

        Returns:
            The inferred batch size.
        """
        for arg in itertools.chain(args, kwargs.values()):
            if isinstance(arg, Tensor) and len(arg.shape) > 1:
                return arg.shape[0]
        raise ValueError("Curate batch size could not be inferred. Please set it manually.")

    def _is_curate_enabled_anywhere(self) -> bool:
        """Checks if curate tracking is enabled anywhere in the model or its children."""
        return self.curate_next_run_settings is not None or any(
            child.curate_enabled for child in self.get_orca_modules_recursively()
        )

    def _curate_forward_pass(self, *args, **kwargs) -> list[int]:
        """Sets up curate tracking for the memory lookups in the next forward pass."""
        if self.curate_model_id is None:
            raise AttributeError("A model id must be set before recording memory lookups")
        if self.curate_database is None:
            raise AttributeError("A database must be set before recording memory lookups")

        if self.curate_next_run_settings:
            self.last_curate_run_settings = CurateModelRunSettings(
                tags=self.curate_tags | self.curate_next_run_settings.tags,
                metadata={**self.curate_metadata, **self.curate_next_run_settings.metadata},
                seq_id=(self.curate_next_run_settings.seq_id or self.curate_seq_id),
                batch_size=self.curate_next_run_settings.batch_size
                or self.curate_batch_size
                or self._infer_batch_size(*args, **kwargs),
            )
        else:
            self.last_curate_run_settings = CurateModelRunSettings(
                tags=self.curate_tags,
                metadata=self.curate_metadata,
                seq_id=self.curate_seq_id,
                batch_size=self.curate_batch_size or self._infer_batch_size(*args, **kwargs),
            )
        self.last_curate_run_ids = generate_run_ids(
            db_name=self.curate_database,
            model_id=self.curate_model_id,
            model_version=self.curate_model_version,
            **asdict(self.last_curate_run_settings),
        )
        return self.last_curate_run_ids

    @deprecated("use record_model_feedback instead")
    def record_curate_scores(self, scores: list[float] | float) -> None:
        # Do not document this function since we do not want it in the docs.
        self.record_model_feedback(scores)

    def record_model_feedback(
        self,
        feedback: list[float] | float | int | list[int],
        name: str = "default",
        kind: FeedbackKind = FeedbackKind.CONTINUOUS,
    ) -> None:
        """
        Records feedback for the last model runs for which memory lookups were recorded by curate.

        Args:
            feedback: The feedback to be recorded.
            name: The name of the feedback.
            kind: The kind of feedback.
        """
        if self.last_curate_run_ids is None:
            raise AttributeError("Feedback can only be recorded if the last model run was tracked by curate")
        assert self.curate_database is not None  # database must be set if last run was tracked
        record_model_feedback(self.curate_database, self.last_curate_run_ids, feedback, name, kind)

    def record_model_input_output(self, inputs: list[Any] | Any, outputs: list[Any] | Any) -> None:
        """
        Records the inputs and outputs of the last model runs for which memory lookups were recorded by curate.

        Args:
            inputs: The inputs to be recorded.
            outputs: The outputs to be recorded.
        """
        if self.last_curate_run_ids is None:
            raise AttributeError("Input and outputs can only be recorded if the last model run was tracked by curate")
        assert self.curate_database is not None  # database must be set if last run was tracked
        record_model_input_output(self.curate_database, self.last_curate_run_ids, inputs, outputs)

    def get_last_curate_memory_lookups(self) -> DataFrame:
        # TODO: implement this method
        if self.last_curate_run_ids is None:
            raise AttributeError("Input and outputs can only be recorded if the last model run was tracked by curate")
        assert self.curate_database is not None  # database must be set if last run was tracked
        raise NotImplementedError("This method is not implemented yet.")


class OrcaLookupModule(OrcaModule, LookupSettingsMixin, PostInitMixin):
    """
    OrcaLookupModule is the base class for all Orca PyTorch layers that support memory lookups
    —--either directly or through their children--- in addition to curate tracking.

    Note:
        Lookup settings are propagated to all children of this module, by recursively setting the
        same lookup settings instance for all its children.
    """

    def __init__(
        self,
        database: OrcaDatabase | str | None = None,
        # Curate Settings
        model_id: str | None = None,
        model_version: str | None = None,
        metadata: OrcaMetadataDict | None = None,
        curate_enabled: bool = False,
        tags: Iterable[str] | None = None,
        # Memory Lookup Settings
        memory_index_name: str | None = None,
        lookup_column_names: list[str] | None = None,
        num_memories: int | None = None,
        drop_exact_match: DropExactMatchOption | None = None,
        exact_match_threshold: float | None = None,
        shuffle_memories: bool = False,
        freeze_num_memories: bool = False,
        propagate_lookup_settings: bool = True,
    ):
        """
        Initializes the module with the specified Curate and memory lookup settings.

        Args:
            database: The OrcaDatabase instance to use for Curate and memory lookups.
            model_id: The ID of the model.
            model_version: The version of the model.
            metadata: The metadata to be stored with Curate runs.
            curate_enabled: Whether Curate tracking is enabled.
            tags: The tags to be included in Curate runs.
            memory_index_name: The name of the index to use for lookups.
            lookup_column_names: The names of the columns to return from the index during a lookup.
            num_memories: The number of memories to return from the index during a lookup.
            freeze_num_memories: Whether the number of memories should be frozen. If set to True,
                an error will be raised if an attempt is made to change the number of memories.
            drop_exact_match: Choose to drop the exact match (if found) always, never, or only
                during training or inference.
            exact_match_threshold: Minimum similarity score for something to be considered the exact match
            shuffle_memories: Whether to shuffle the memories before returning them.
            propagate_lookup_settings: Whether to propagate lookup settings to all children.

        """
        OrcaModule.__init__(
            self,
            model_id=model_id,
            model_version=model_version,
            metadata=metadata,
            curate_enabled=curate_enabled,
            tags=tags,
            curate_database=database,
        )
        LookupSettingsMixin.__init__(
            self,
            lookup_database=database,
            memory_index_name=memory_index_name,
            lookup_column_names=lookup_column_names,
            num_memories=num_memories,
            freeze_num_memories=freeze_num_memories,
            propagate_lookup_settings=propagate_lookup_settings,
            drop_exact_match=drop_exact_match,
            exact_match_threshold=exact_match_threshold,
            shuffle_memories=shuffle_memories,
        )

    def get_lookup_setting_summary(self) -> dict[DatabaseIndexName, LookupSettingsSummary]:
        """Returns a summary of the lookup settings for each [`OrcaLookupLayer`][orcalib.torch.OrcaLookupLayer] in
        this module and its descendants."""

        return LookupSettingsSummary.from_lookup_settings(
            m.get_effective_lookup_settings() for m in self.get_orca_modules_recursively(filter_type=OrcaLookupLayer)
        )

    def post_init(self):
        super().post_init()
        self._propagate_lookup_settings()


class OrcaModel(OrcaLookupModule, PostInitMixin, PreForwardMixin):
    """
    OrcaModel should be the base class for all PyTorch models that include Orca layers.

    **This class is responsible for:**

    * Propagating Curate and memory lookup settings to all children of the model.
    * Getting curate run ids and preparing tracking before the forward pass.
    * Building layer names for all children of the model.

    **This class provides functions to let you:**

    * Enable and disable Curate tracking for the model and all its children.
    * Record Curate scores for the last run.
    * Record model input and output for the last run.
    * Enable and disable memory access for the model and all its children.
    * Update Curate tracking settings for the model and all its children.

    When using OrcaModel, you can set global settings for Curate tracking and memory lookups that will be propagated
    to all children of the model. This allows you to set these settings once for the entire model and have them
    automatically applied to all layers.
    """

    def __init__(
        self,
        database: OrcaDatabase | str | None = None,
        # Curate Settings
        model_id: str | None = None,
        model_version: str | None = None,
        metadata: OrcaMetadataDict | None = None,
        curate_enabled: bool = False,
        tags: Iterable[str] | None = None,
        # Memory Lookup Settings
        memory_index_name: str | None = None,
        lookup_column_names: list[str] | None = None,
        num_memories: int | None = None,
        drop_exact_match: DropExactMatchOption | None = None,
        exact_match_threshold: float | None = None,
        shuffle_memories: bool = False,
        freeze_num_memories: bool = False,
        propagate_lookup_settings: bool = True,
    ):
        """
        Initializes the model with global settings.

        Args:
            database: The OrcaDatabase instance to use for Curate and memory lookups.
            model_id: model_id will be included in all runs tracked with curate.
            model_version: model_version will be included in all runs tracked with curate.
            metadata: metadata is a dictionary of additional information to be stored with Curate runs.
            curate_enabled: Whether curate tracking is enabled.
            tags: tags is a set of strings to be included in all runs tracked with curate.
            memory_index_name: The name of the index to use for lookups.
            lookup_column_names: The names of the columns to return from the index during a lookup.
            num_memories: The number of memories to return from the index during a lookup.
            drop_exact_match: Choose to drop the exact match (if found) always, never, or only during training
            exact_match_threshold: Minimum similarity score for something to be considered the exact match
            shuffle_memories: Whether to shuffle the memories before
                returning them. (default: False)
            freeze_num_memories: Whether the number of memories should
                be frozen after initialization. (default: False) When
            propagate_lookup_settings: Whether to propagate lookup
                settings to all children. (default: False)
        or inference. (default: NEVER)
        set to True, an error will be raised if an attempt is made to change the number of memories.
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
            drop_exact_match=drop_exact_match,
            exact_match_threshold=exact_match_threshold,
            shuffle_memories=shuffle_memories,
            freeze_num_memories=freeze_num_memories,
            propagate_lookup_settings=propagate_lookup_settings,
        )

    def pre_forward(self, *args, **kwargs):
        # Do not document this function since we do not want it in the docs.
        self.last_curate_run_ids = None
        self.last_curate_run_settings = None
        if self._is_curate_enabled_anywhere() and not self.training:
            self._curate_forward_pass(*args, **kwargs)

    def post_forward(self, output):
        # Do not document this function since we do not want it in the docs.
        self.curate_next_run_settings = None

    def post_init(self) -> None:
        # Do not document this function since we do not want it in the docs.
        super().post_init()
        OrcaModel._build_layer_names(self)
        # Build layer names and propagate curate settings to all children (overriding their settings)
        for child in self.get_orca_modules_recursively(include_self=False):
            child._orca_curate_settings = self._orca_curate_settings
            child.curate_enabled = self.curate_enabled

    @deprecated("use update_curate_settings instead")
    def init_curate(self, *args, **kwargs) -> None:
        # Do not document this function since we do not want it in the docs.
        self.update_curate_settings(*args, **kwargs)

    @staticmethod
    def _build_layer_names(inst: nn.Module, root_name: str | None = None) -> None:
        """Builds layer names for the model and all its children.

        Args:
            inst: A PyTorch model instance.
            root_name: The name of the root layer. (default: None)
        """
        if isinstance(inst, OrcaModule) and getattr(inst, "curate_layer_name", None) is None:
            inst.curate_layer_name = root_name
        for name, child in inst.named_children():
            OrcaModel._build_layer_names(
                child,
                f"{root_name + '.' if root_name is not None else ''}{name}",
            )

    def enable_memory(self) -> None:
        """Enables memory access for the model and all its children."""
        for child in self.get_orca_modules_recursively():
            if hasattr(child, "_memory_enabled"):
                child._memory_enabled = True

    def disable_memory(self) -> None:
        """Disables memory access for the model and all its children."""
        for child in self.get_orca_modules_recursively():
            if hasattr(child, "_memory_enabled"):
                child._memory_enabled = False


@final
class _LinearClassificationHead(OrcaModule):
    """A 2-Layer linear classification head generally used for a transformer model.

    Examples:
        ```py
        import torch
        from orcalib import OrcaModule, _LinearClassificationHead

        class MyModule(OrcaModule):
            def __init__(self):
                super().__init__()
                self.linear = torch.nn.Linear(10, 10)
                self.classifier = _LinearClassificationHead(10, 5)

            def forward(self, x):
                x = self.linear(x)
                x = self.classifier(x)
                return x

        model = MyModel()
        ```
    """

    def __init__(
        self,
        model_dim: int,
        num_labels: int,
        activation: Callable[[Tensor], Tensor] = F.relu,
        dropout: float = 0.1,
    ):
        """
        Initializes the linear classification head.

        Args:
            model_dim: The dimension of the input tensor.
            num_labels: The number of labels.
            activation: The activation function. (default: F.relu)
            dropout: The dropout rate. (default: 0.1)
        """
        super().__init__()

        self.model_dim = model_dim
        self.num_labels = num_labels
        self.activation = activation
        self.dropout = dropout

        self.linear1 = nn.Linear(model_dim, model_dim)
        self.dropout_layer = nn.Dropout(self.dropout)
        self.linear2 = nn.Linear(model_dim, num_labels)

    def forward(self, x) -> Tensor:
        """
        Performs a forward pass through the linear classification head.

        Args:
            x: The input tensor of shape (`batch_size`, `model_dim`)

        Returns:
            The output tensor of shape (`batch_size`, `num_labels`)
        """
        x = self.linear1(x)
        x = self.activation(x)
        x = self.dropout_layer(x)
        x = self.linear2(x)
        return x


class OrcaLookupLayer(OrcaLookupModule):
    """
    A layer to perform memory lookups from a database index.

    Note:
        This requires a database to be attached to the model, with the index already created.

    Examples:
        ```py
        import torch
        from orcalib import OrcaModule, OrcaLookupLayer

        class MyLookupModule(OrcaModule):
            def __init__(self):
                super().__init__()
                self.lookup = OrcaLookupLayer(
                    memory_index_name="text_index",
                    lookup_column_names=["label, "$embedding"],
                    num_memories=10
                )

            def forward(self, x: Tensor) -> Tuple[Tensor, Tensor]:
                res = self.lookup(x)
                # ctx is a float tensor of shape (batch_size, num_memories, embedding_dim)
                ctx = res.to_tensor("$embedding", dtype=x.dtype, device=x.device)
                # ctx_labels is an integer tensor of shape (batch_size, num_memories)
                ctx_labels = res.to_tensor("label", dtype=torch.int64, device=x.device).squeeze(-1)
                return ctx, ctx_labels
        ```
    """

    _cache: dict[tuple, Any] = {}

    def __init__(
        self,
        database: OrcaDatabase | str | None = None,
        # Curate Settings
        curate_enabled: bool = False,
        # Memory Lookup Settings
        memory_index_name: str | None = None,
        lookup_column_names: list[str] | None = None,
        num_memories: int | None = None,
        drop_exact_match: DropExactMatchOption | None = None,
        exact_match_threshold: float | None = None,
        shuffle_memories: bool = False,
        freeze_num_memories: bool = False,
        cache_ttl: int | None = None,
        layer_name: str | None = None,
    ):
        """
        Initialize the layer with the specified Curate and memory lookup settings.

        Args:
            database: The OrcaDatabase instance to use for lookups and curate tracking.
            curate_enabled: Whether Curate tracking is enabled.
            memory_index_name: The name of the index to use for lookups.
            lookup_column_names: The names of the columns to return from the index during a lookup.
            num_memories: The number of memories to return from the index during a lookup.
            drop_exact_match: Choose to drop the exact match (if found) always, never, or only during training or inference.
            exact_match_threshold: Minimum similarity score for something to be considered the exact match
            shuffle_memories: Whether to shuffle the memories before returning them.
            freeze_num_memories: Whether the number of memories should be frozen.
            cache_ttl: The time-to-live for the lookup cache.
        """

        super().__init__(
            database=database,
            curate_enabled=curate_enabled,
            memory_index_name=memory_index_name,
            lookup_column_names=lookup_column_names,
            num_memories=num_memories,
            freeze_num_memories=freeze_num_memories,
            drop_exact_match=drop_exact_match,
            exact_match_threshold=exact_match_threshold,
            shuffle_memories=shuffle_memories,
            propagate_lookup_settings=False,
        )
        self.curate_layer_name = layer_name
        self.cache_ttl = cache_ttl
        self.use_lookup_cache = self.cache_ttl is not None
        if self.use_lookup_cache and self.curate_enabled:
            # TODO: rethink how to best allow using lookup cache in train mode where curate is disabled
            raise ValueError("Curate tracking cannot be enabled when using the lookup cache")

    def _get_index_info_with_overrides(
        self,
        orca_db_instance: OrcaDatabase | None = None,
        index_name: str | None = None,
        lookup_column_names: list[str] | None = None,
        num_memories: int | None = None,
    ) -> tuple[OrcaDatabase, str, list[str], int]:
        """
        Returns the index-lookup info, with overrides applied where provided

        Args:
            orca_db_instance: The OrcaDatabase instance to use.
            index_name: The name of the index to use.
            lookup_column_names: The names of the columns to return from the index.
            num_memories: The number of memories to return from the index.

        Returns:
            orca_db_instance: The OrcaDatabase instance to use.
            index_name: The name of the index to use.
            lookup_column_names: The names of the columns to return from the index.
            num_memories: The number of memories to return from the index.
        """
        orca_db_instance = orca_db_instance or self.get_lookup_database_instance()
        index_name = index_name or self.memory_index_name
        if index_name is None:
            raise ValueError("Index name must be set before lookup or passed to forward()")
        lookup_column_names = lookup_column_names or self.lookup_column_names
        if lookup_column_names is None:
            raise ValueError("Lookup column names must be set before lookup or passed to forward()")
        num_memories = num_memories or self.num_memories
        if num_memories is None or num_memories <= 0:
            raise ValueError("num_memories must be set > 0 before lookup or passed to forward()")
        return orca_db_instance, index_name, lookup_column_names, num_memories

    def __apply_result_transforms(self, result: BatchedScanResult) -> BatchedScanResult:
        # Applies the lookup result transforms to the result, if there are any
        if self.lookup_result_transforms is None:
            return result

        if isinstance(self.lookup_result_transforms, list):
            for transform in self.lookup_result_transforms:
                result = transform(result)
        else:
            result = self.lookup_result_transforms(result)
        return result

    def _db_lookup(
        self,
        x: Tensor | str | list[str],
        orca_db_instance: OrcaDatabase,
        index_name: str,
        lookup_column_names: list[str],
        num_memories: int,
    ) -> BatchedScanResult:
        """
        Performs the lookup in the OrcaDatabase index.

        Args:
            x: The input tensor of shape (`batch_size`, `embedding_dim`)
            orca_db_instance: The database instance to use.
            index_name: The name of the index to use.
            lookup_column_names: The names of the columns to return from the index.
            num_memories: The number of memories to return from the index.

        Returns:
            The result of the lookup.
        """

        if self.lookup_result_override is not None:
            result = self.__apply_result_transforms(self.lookup_result_override)
            return result

        if self.lookup_query_override is not None:
            x = self.lookup_query_override

        if self.extra_lookup_column_names is not None:
            # Add all the extra columns we're not already looking up
            lookup_column_names = lookup_column_names + [
                col for col in self.extra_lookup_column_names if col not in lookup_column_names
            ]

        cache_key = None
        if self.use_lookup_cache:
            cache_key = (
                x,
                orca_db_instance.name,
                index_name,
                lookup_column_names,
                num_memories,
            )
            mem = OrcaLookupLayer._cache.get(cache_key, None)
            if mem is not None:
                result, timestamp = mem
                if timestamp + self.cache_ttl > time.time():
                    return result

        if isinstance(x, str):
            query = [x]
            query_len = 1
        elif isinstance(x, list):
            query = x
            query_len = len(x)
        elif isinstance(x, Tensor):
            query = x.detach().cpu().to(torch.float32).numpy().tolist()
            query_len = x.shape[0]
        else:
            raise ValueError(f"Unsupported input type: {type(x)}")

        do_dropout = (
            self.drop_exact_match == DropExactMatchOption.ALWAYS
            or (self.drop_exact_match == DropExactMatchOption.TRAINING_ONLY and self.training)
            or (self.drop_exact_match == DropExactMatchOption.INFERENCE_ONLY and not self.training)
        )

        if do_dropout:
            req = orca_db_instance.vector_scan_index(
                index_name,
                query,
                drop_exact_match=True,
                exact_match_threshold=self.exact_match_threshold,
            )
        else:
            req = orca_db_instance.vector_scan_index(index_name, query)

        # track this particular lookup using Curate
        if self.last_curate_run_ids:
            if query_len != len(self.last_curate_run_ids):
                raise ValueError(
                    f"The inferred or manually set curate batch size ({len(self.last_curate_run_ids)}) did not match the actual query length ({query_len})."
                )
            assert self.curate_layer_name is not None  # we fill in the layer name in post_init
            req = req.track_with_curate(self.last_curate_run_ids, self.curate_layer_name)

        # execute the lookup (fetch), where meta is a list of additional columns to be returned
        # aside from the index vector matches
        res = req.select(*lookup_column_names).fetch(num_memories)  # type: ignore

        if self.shuffle_memories:
            res.shuffle()

        if self.use_lookup_cache:
            OrcaLookupLayer._cache[cache_key] = (res, time.time())  # type: ignore

        # Apply transforms, if any. Note that the transforms are applied AFTER the cache check,
        # because the transforms can change between calls.
        res = self.__apply_result_transforms(res)

        return res

    def forward(
        self,
        x: Tensor | str | list[str],
        orca_db_instance: OrcaDatabase | None = None,
        index_name: str | None = None,
        lookup_column_names: list[str] | None = None,
        num_memories: int | None = None,
    ) -> BatchedScanResult:
        """
        Perform a vector index scan and return the top `num_memories` results.

        Args:
            x: The input tensor of shape (`batch_size`, `embedding_dim`)
            orca_db_instance: Override for the database to use.
            index_name: Override for the name of the index to use.
            lookup_column_names: Override for the names of the columns to return.
            num_memories: Override for the number of memories to return.

        Returns:
            The batch of lookup results, use [`to_tensor`][orcalib.BatchedScanResult.to_tensor] to
                convert columns from the result to tensors.
        """
        if num_memories is not None and num_memories <= 0:
            raise ValueError(f"num_memories must be > 0, but is {num_memories}")

        orca_db_instance, index_name, lookup_column_names, num_memories = self._get_index_info_with_overrides(
            orca_db_instance, index_name, lookup_column_names, num_memories
        )

        lookup_column_names = cast(list[str], lookup_column_names)

        res = self._db_lookup(x, orca_db_instance, index_name, lookup_column_names, num_memories)
        # res "shape" is (batch_size, num_memories, num_meta_columns)
        # res[i][j] is a dict, with a `vec` attribute and an `extra` attribute

        assert isinstance(res, BatchedScanResult)
        return res


class OrcaLabelLookupLayer(OrcaLookupLayer, LabelColumnNameMixin):
    """
    A layer to lookup embeddings and label from a database index.

    This is a convenience layer around [`OrcaLookupLayer`][orcalib.orca_torch.OrcaLookupLayer] that
    does not just perform the lookups but also converts the results to tensors.

    Note:
        This requires a database to be attached to the model, with the index already created.

    Examples:
        ```py
        import torch
        from orcalib import OrcaModule, OrcaLabelLookupLayer

        class MyModule(OrcaModule):
            def __init__(self):
                super().__init__()
                self.lookup = OrcaLabelLookupLayer(
                    index_name="my_index",
                    label_column_name="my_label",
                    num_memories=10
                )

            def forward(self, x):
                embeddings, labels = self.lookup(x)
                # embeddings is a float tensor of shape (batch_size, num_memories, embedding_dim)
                # labels is an int tensor of shape (batch_size, num_memories)
        ```
    """

    def __init__(
        self,
        database: OrcaDatabase | str | None = None,
        # Curate Settings
        curate_enabled: bool = False,
        # Lookup Settings
        memory_index_name: str | None = None,
        label_column_name: ColumnName | None = None,
        num_memories: int | None = None,
        drop_exact_match: DropExactMatchOption | None = None,
        exact_match_threshold: float | None = None,
        shuffle_memories: bool = False,
        freeze_num_memories: bool = False,
    ):
        """
        Initializes the layer with the specified Curate and memory lookup settings.

        Args:
            database: The OrcaDatabase instance to use for lookups and curate tracking.
            curate_enabled: Whether Curate tracking is enabled.
            memory_index_name: The name of the index to use for lookups.
            label_column_name: The name of the label column to return from the index.
            num_memories: The number of memories to return from the index during a lookup.
            drop_exact_match: Choose to drop the exact match (if found) always, never, or only during training or inference.
            exact_match_threshold: Minimum similarity score for something to be considered the exact match.
            shuffle_memories: Whether to shuffle the memories before returning them.
            freeze_num_memories: Whether the number of memories should be frozen. When set to True,
                an error will be raised if an attempt is made to change the number of memories.
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
            freeze_num_memories=freeze_num_memories,
            cache_ttl=None,
        )
        self.label_column_name = label_column_name

    def forward(
        self,
        x: Tensor,
        orca_db_instance: OrcaDatabase | None = None,
        index_name: str | None = None,
        label_column_name: ColumnName | None = None,
        num_memories: int | None = None,
    ) -> tuple[Tensor, Tensor]:
        """
        Look up embeddings and labels

        Args:
            x: The input tensor of shape (`batch_size`, `embedding_dim`)
            orca_db_instance: Optional override for the OrcaDatabase instance to use.
            index_name: Optional override for the name of the index to use.
            label_column_name: Optional override for the name of the label column to return from the index.
            num_memories: Optional override for the number of memories to return from the index.

        Returns:
            embeddings: A tensor with the same type as the input x of shape (`batch_size`, `num_memories`, `embedding_dim`)
            labels: An `int64` tensor of shape (`batch_size`, `num_memories`)
        """
        label_override = None
        if label_column_name:
            label_override = ["$embedding", label_column_name]

        label_column_name = label_column_name or self.label_column_name
        if label_column_name is None:
            raise ValueError("Label column name must be set before lookup or passed to forward()")
        result = super().forward(x, orca_db_instance, index_name, label_override, num_memories)
        embeddings = result.to_tensor("$embedding", dtype=x.dtype, device=x.device)
        # labels must be int64 because F.one_hot does not support other integer types
        labels = result.to_tensor(label_column_name, dtype=torch.int64, device=x.device).squeeze(-1)
        return embeddings, labels


class OrcaClassificationMemoryGuideLayer(OrcaLookupModule, LabelColumnNameMixin):
    """
    A PyTorch module that implements a memory-guided classification layer.

    This layer biases the output of a classification model towards a set of memories. The bias is
    controlled by a weight parameter, which determines how strongly the model should be biased
    towards the memories.
    """

    def __init__(
        self,
        num_classes: int,
        num_memories: int,
        enable_in_training: bool = False,
        guide_weight: float = 0.1,
        # Shared settings
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
        Initializes the memory-guided classification layer.

        Args:
            num_classes: The number of classes in the classification task.
            num_memories: The number of memories the layer should use.
            enable_in_training: Whether to enable the layer during training.
            guide_weight: The weight of the memory guide.
            database: The OrcaDatabase instance to use for lookups and curate tracking.
            curate_enabled: Whether Curate tracking is enabled.
            memory_index_name: The name of the index to use for lookups.
            drop_exact_match: Choose to drop the exact match (if found) always, never, or only during training or inference.
            exact_match_threshold: Minimum similarity score for something to be considered the exact match.
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

        self.num_classes = num_classes
        self.enable_in_training = enable_in_training
        self.guide_weight = guide_weight
        self.label_column_name = label_column_name

        # Lookup settings will be propagated to the lookup layer
        self.lookup = OrcaLabelLookupLayer(database=database)

    def forward(
        self,
        logits: Tensor,
        memory_key: Tensor,
        ctx: Tensor | None = None,
        labels: Tensor | None = None,
    ) -> Tensor:
        """
        Ground the logits based on the memory context.

        Args:
            logits: Input tensor of shape (`batch_size`, `num_classes`)
            memory_key: Memory key tensor of shape (`batch_size`, `embedding_dim`)
            ctx: Memory embeddings tensor of shape (`batch_size`, `num_memories`, `embedding_dim`).
                If None, the memory context is looked up based on the memory key.
            labels: Memory label tensor of shape (`batch_size`, `num_memories`). If None, the
                labels are looked up along with the memory context.

        Returns:
            Output tensor of shape (`batch_size`, `num_classes`).
        """
        if self.training and not self.enable_in_training:
            return logits

        if ctx is None or labels is None:
            assert labels is None and ctx is None, "Both labels and ctx must be None or neither should be None"
            ctx, labels = self.lookup(memory_key)

        probs = F.softmax(logits, dim=1)
        lhat = F.one_hot(labels, num_classes=self.num_classes).to(logits.dtype)
        weights = torch.bmm(ctx, memory_key.unsqueeze(2)).squeeze(2)
        bias = weights.unsqueeze(-1) * lhat
        bias = torch.sum(bias, dim=1)
        bias = torch.nn.functional.softmax(bias, dim=1)
        logits = probs + self.guide_weight * bias

        return logits


class OrcaClassificationCrossAttentionLayer(OrcaLookupModule, LabelColumnNameMixin):
    """
    A transformer decoder layer block that does cross attention

    Note that this is Classification-specific, and the labels returned by the lookup layer are used
    as the value-weights for the cross attention.

    The block contains the typical transformer components: multi-head attention, feed forward, and
    layer norm. The block also contains a lookup layer that looks up a vector in an OrcaDatabase
    index and returns the top k results. These results are used as the memory context for the cross
    attention.
    """

    def __init__(
        self,
        model_dim: int,
        num_heads: int,
        num_classes: int,
        num_memories: int,
        dropout: float = 0.1,
        activation: Callable[[Tensor], Tensor] = F.relu,
        projection_mode: ProjectionMode = ProjectionMode.LABEL,
        split_retrieval_path: bool = False,
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
        Initializes the cross attention layer.

        Args:
            model_dim: The dimension of the input vector and hidden layers.
            num_heads: The number of heads to be used in the multi-head attention layer.
            num_classes: The number of classes for the output classification and weights for cross attention.
            num_memories: The number of memory vectors to be returned from the lookup.
            dropout: The dropout rate.
            activation: The activation function.
            projection_mode: The projection mode to use for the memory labels.
            split_retrieval_path: Whether to split the retrieval path.
            database: The OrcaDatabase instance to use for lookups and curate tracking.
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

        self.model_dim = model_dim
        self.num_heads = num_heads
        self.num_classes = num_classes
        self.dropout = dropout
        self.activation = activation
        self.projection_mode = projection_mode
        self.split_retrieval_path = split_retrieval_path
        self.label_column_name = label_column_name

        # Lookup settings will be automatically propagated to the lookup layer
        self.lookup = OrcaLabelLookupLayer(database=database, num_memories=num_memories)

        self.cross_attention = nn.MultiheadAttention(
            self.model_dim,
            self.num_heads,
            dropout=self.dropout,
            batch_first=True,
            vdim=self.num_classes,
        )
        self.attn_norm = nn.LayerNorm(self.model_dim)

        self.linear1 = nn.Linear(self.model_dim, self.model_dim * 4)
        self.dropout1 = nn.Dropout(self.dropout)
        self.linear2 = nn.Linear(self.model_dim * 4, self.model_dim)
        self.dropout2 = nn.Dropout(self.dropout)
        self.ff_norm = nn.LayerNorm(self.model_dim)

    def forward(
        self,
        x: Tensor,  # Shape (batch_size, embedding_dim)
        ctx: Tensor | None = None,  # Shape (batch_size, num_memories, embedding_dim)
        labels: Tensor | None = None,  # Shape (batch_size, num_memories, meta_column_count)
        memory_key: Tensor | None = None,  # Shape (batch_size, embedding_dim)
    ) -> Tensor:  # x is the input vector N x D, ctx is the memory context N x K x D
        """
        Performs cross attention on the input tensor and memory context.

        Info: Cross Attention Mechanism:
            `x`, `ctx`, `labels` act as `Q`, `K`, `V` for the cross attention layer.

            When `ctx` is `None`:

            * If `split_retrieval_path` is `False`, `x` is used as both `Q` and `K`.
            * If `split_retrieval_path` is True, `memory_key` is used as `K` (instead of `x`)

            The `labels` are used as `V` and projected into the embedding space.

        Args:
            x: The input tensor of shape (`batch_size`, `embedding_dim`)
            ctx: The memory embeddings tensor of shape (`batch_size`, `num_memories`, `embedding_dim`).
            labels: The memory label tensor of shape (`batch_size`, `num_memories`).
            memory_key: The memory lookup tensor of shape (`batch_size`, `embedding_dim`).

        Returns:
            The output tensor of shape (`batch_size`, `embedding_dim`).
        """
        if ctx is None or labels is None:
            if self.split_retrieval_path and memory_key is None:
                raise ValueError("Split retrieval path requires either a memory key or context to be passed in")
            assert labels is None and ctx is None, "Both labels and ctx must be None or neither should be None"
            # Shape of ctx: (batch_size, num_memories, embedding_dim)
            # Shape of labels: (batch_size, num_memories)
            ctx, labels = self.lookup(memory_key) if self.split_retrieval_path else self.lookup(x)

        x = x.unsqueeze(1)  # N x 1 x D

        if self.projection_mode == ProjectionMode.POSITIONAL:
            labels = torch.arange(self.num_memories).repeat(x.shape[0], 1)

        """
        K = num memories; C = num classes (for positional projection mode C == K); D = embedding dimension

        The attention layer (across all its heads) projects the one-hot encoded labels (these can be
        either class labels or positional labels depending on the projection mode) into the
        embedding space (K x C -> D). Then it compares the input embedding with the K neighbors'
        embeddings, to derive something like a similarity score for each neighbor. These similarity
        scores are then used to combine the projected labels into a single vector in the model dimension
        space, which is returned. This is akin to a weighted average, but with learned weights.

        The return value of the cross-attention layer is a representation of the positional or class
        **labels** of similar memories in the **embedding space**. These are then fed into a feedforward
        network before they are returned to the outer model. If the outer classification head uses
        `deep_residuals` (default), the output of this layer will thus be used to alter the input
        embedding based on the positional or class **labels** of similar memories.
        """
        values = F.one_hot(labels, self.num_classes).to(x.dtype).to(x.device)  # N x K x C
        x, _ = self.cross_attention(x, ctx, values)  # N x 1 x D
        x = x.squeeze(1)  # N x D
        x = self.attn_norm(x)  # N x D

        y = self.linear1(x)  # N x D*4
        y = self.activation(y)
        y = self.dropout1(y)
        y = self.linear2(y)  # N x D
        y = self.dropout2(y)
        x = self.ff_norm(y + x)  # N x D

        return x


class OrcaMemoryBindingLayer(OrcaLookupModule, LabelColumnNameMixin):
    """
    Memory binding layer that transforms positional logits (which describe the memories that the
    model predicted to be relevant) into regular logits, which describe the class the model
    predicts.
    """

    def __init__(
        self,
        num_memories: int,
        num_classes: int,
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
        Initializes the memory binding layer.

        Args:
            num_memories: The number of memory vectors to be returned from the lookup.
            num_classes: The number of classes for the output classification and weights for cross attention.
            database: The OrcaDatabase instance to use for lookups and curate tracking.
            curate_enabled: Whether Curate tracking is enabled.
            memory_index_name: The name of the index to use for lookups.
            drop_exact_match: Choose to drop the exact match (if found) always, never, or only during training or inference.
            exact_match_threshold: Minimum similarity score for something to be considered the exact match.
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

        self.num_classes = num_classes
        self.label_column_name = label_column_name

        # Lookup settings will be automatically propagated to the lookup layer
        self.lookup = OrcaLabelLookupLayer(
            database=database,
            num_memories=num_memories,
            freeze_num_memories=True,
        )

    def forward(
        self,
        logits: Tensor,
        memory_key: Tensor | None = None,
        ctx: Tensor | None = None,
        labels: Tensor | None = None,
    ) -> Tensor:
        """
        Args:
            logits: Input tensor with positional logits of shape (`batch_size`, `num_memories`).
            memory_key: Memory key tensor of shape (`batch_size`, `embedding_dim`).
            ctx: Memory context tensor of shape (`batch_size`, `num_memories`, `embedding_dim`).
                If `None`, the memory context is looked up based on the memory key.
            labels: Memory Label tensor of shape (`batch_size`, `num_memories`).
                If `None`, the labels are looked up along with the memory context.

        Returns:
            Output tensor of shape (`batch_size`, `num_classes`).
        """
        if ctx is None or labels is None:
            assert labels is None and ctx is None, "Both labels and ctx must be None or neither should be None"
            if memory_key is None:
                raise ValueError("Memory key must be provided if ctx and labels are not")
            _, labels = self.lookup(memory_key)

        mem_labels = F.one_hot(labels, num_classes=self.num_classes).to(logits.dtype).to(logits.device)  # N x K x C
        return torch.bmm(logits.unsqueeze(1), mem_labels).squeeze()  # N x C


class _GatedMoeHead(OrcaModule):
    """
    A gated mixture of experts head.

    This head takes two expert logits and a gate tensor and returns a weighted sum of the expert logits.

    Examples:
        ```py
        import torch
        from orcalib import OrcaModel, _GatedMoeHead

        class MyModule(OrcaModel):
            def __init__(self):
                super().__init__()
                self.gate = _GatedMoeHead(10, 5)

            def forward(self, x, expert1, expert2):
                return self.gate(x, (expert1, expert2))
        ```
    """

    def __init__(self, input_dim: int, num_layers: int = 1):
        """
        Args:
            input_dim: The input dimension.
            num_layers: The number of layers. (default: 1)
        """
        super().__init__()
        self.gate = nn.Sequential(
            *[layer for _ in range(num_layers - 1) for layer in (nn.Linear(input_dim, input_dim), nn.ReLU())],
            nn.Linear(input_dim, 2),
            nn.LayerNorm(2),
        )

    def forward(self, x: Tensor, memory_expert_logits: Tensor, direct_classification_expert_logits: Tensor) -> Tensor:
        """Forward method for the _GatedMoeHead

        Args:
            x: The input tensor.
            experts_logits: Tuple of two expert logits.

        Returns:
            The output tensor.
        """
        weights = self.gate(x)

        return (
            weights[:, 0].view(-1, 1) * memory_expert_logits
            + weights[:, 1].view(-1, 1) * direct_classification_expert_logits
        )


class OrcaLLMMemoryGuideLayer(OrcaLookupModule, LabelColumnNameMixin):
    """
    A PyTorch module that implements a memory-guided generation layer for Language Models.

    This layer biases the output distribution of the model towards a set of memories.
    """

    def __init__(
        self,
        num_memories: int,
        alpha: float,
        beta: float,
        vocab_size: int,
        tokenizer: Callable[[str | list[str]], list[int] | list[list[int]]],
        S_min: int = 3,
        S_max: int = 10,
        enable_in_training: bool = False,
        # Shared Settings
        database: OrcaDatabase | str | None = None,
        # Curate Settings
        curate_enabled: bool = False,
        # Lookup Settings
        memory_index_name: str | None = None,
        drop_exact_match: DropExactMatchOption | None = None,
        exact_match_threshold: float | None = None,
        shuffle_memories: bool = False,
        label_column_name: str | None = None,
    ):
        """
        Initializes the memory-guided generation layer.

        Args:
            num_memories: The number of memories.
            alpha: The alpha parameter for the memory guide.
            beta: The beta parameter for the memory guide.
            vocab_size: The size of the vocabulary.
            tokenizer: The tokenizer function.
            S_min: The minimum length of the suffixes to search for.
            S_max: The maximum length of the suffixes to search for.
            enable_in_training: Whether to enable the memory guide layer during training.
            database: The OrcaDatabase instance to use for lookups and curate tracking.
            curate_enabled: Whether Curate tracking is enabled.
            memory_index_name: The name of the index to use for lookups.
            drop_exact_match: Choose to drop the exact match (if found) always, never, or only during training or inference.
            exact_match_threshold: Minimum similarity score for something to be considered the exact match.
            shuffle_memories: Whether to shuffle the memories before returning them.
            label_column_name: The name of the label column to return from the index.
        """

        super().__init__(
            database=database,
            curate_enabled=curate_enabled,
            memory_index_name=memory_index_name,
            num_memories=num_memories,
            drop_exact_match=drop_exact_match,
            exact_match_threshold=exact_match_threshold,
            shuffle_memories=shuffle_memories,
            freeze_num_memories=True,
            propagate_lookup_settings=True,
        )

        self.alpha = alpha
        self.beta = beta
        self.vocab_size = vocab_size
        self.tokenizer = tokenizer
        self.S_min = S_min
        self.S_max = S_max
        self.enable_in_training = enable_in_training
        self.label_column_name = label_column_name

        # Lookup settings will be automatically propagated to the lookup layer
        self.lookup = OrcaLookupLayer()

    def _compute_lps_array(self, pattern) -> list[int]:
        """Compute the longest prefix that is also a suffix (lps) array used in KMP algorithm."""
        lps = [0] * len(pattern)
        length = 0  # length of the previous longest prefix suffix

        # Loop calculates lps[i] for i = 1 to M-1
        i = 1
        while i < len(pattern):
            if pattern[i] == pattern[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    length = lps[length - 1]
                    # Note that we do not increment i here
                else:
                    lps[i] = 0
                    i += 1

        return lps

    def _find_suffixes_in_sequence(self, S, M, S_min, S_max) -> list[tuple[int, int, str]]:
        """
        Find the starting indexes where the suffixes of `S` of lengths between `S_min` and `S_max`
            are contained in `M`.

        Args:
            S: The sequence to search for suffixes in `M`.
            M: The sequence to search for suffixes of `S`.
            S_min: The minimum length of the suffixes to search for.
            S_max: The maximum length of the suffixes to search for.

        Returns:
            A list of tuples containing the starting index of the suffix in `M`, the length of the
                suffix, and the next token in `M` after the suffix.
        """
        occurrences = []

        # Iterate through the range of lengths for suffixes of S
        for suffix_length in range(S_min, S_max + 1):
            # Get the suffix of S of length suffix_length
            suffix = S[-suffix_length:]

            # Preprocess the suffix to get the lps array
            lps = self._compute_lps_array(suffix)

            # Start searching for the suffix in M
            i = j = 0  # i is index for M, j is index for suffix
            while i < len(M):
                if suffix[j] == M[i]:
                    i += 1
                    j += 1

                if j == len(suffix):
                    # If we found a complete match, record the index where it starts in M
                    if i < len(M):
                        occurrences.append((i - j, len(suffix), M[i]))
                    else:
                        occurrences.append((i - j, len(suffix), None))
                    j = lps[j - 1]

                # Mismatch after j matches
                elif i < len(M) and suffix[j] != M[i]:
                    # Do not match lps[0..lps[j-1]] characters, they will match anyway
                    if j != 0:
                        j = lps[j - 1]
                    else:
                        i += 1

        return occurrences

    def _extract_occurance_ranks(self, occurrences, ref_length) -> dict[int, float]:
        """Extract the occurance ranks from the occurrences.

        Args:
            occurrences: The occurrences to extract the ranks from.
            ref_length: The length of the reference sequence.

        Returns:
            A dictionary of token to occurrence rank.
        """
        scores = defaultdict(int)
        for _, length, next_token in occurrences:
            if next_token is None:
                continue
            if length > scores[next_token]:
                scores[next_token] = length / ref_length
        return dict(scores)

    def _bag_of_words_probs(self, bag_of_words: list[tuple[list[int], float]]) -> Tensor:
        """
        Compute the bag of words probabilities.

        Args:
            bag_of_words: The bag of words to compute the probabilities for.

        Returns:
            The bag of words probabilities.
        """
        res = torch.zeros(self.vocab_size)
        for bag, score in bag_of_words:
            for token in bag:
                res[token] += score
        return Tensor(res).softmax(dim=-1)

    def _weighted_next_tokens_from_memory(
        self, memory_key: Tensor, q_tokens: list[int]
    ) -> tuple[
        dict[int, float], list[tuple[list[int], float]]
    ]:  # suffix max dict (token -> score), bag_of_words list (token list, score)
        """
        Compute the weighted next tokens from memory.

        Args:
            memory_key: The memory key to use for memory lookup.
            q_tokens: The input tokens.

        Returns:
            A tuple containing the weighted next tokens from the memory and the bag of words.
        """
        result = self.lookup(memory_key)
        ctx = result.to_tensor("$embedding", dtype=memory_key.dtype, device=memory_key.device)
        candidates: list[str] = result[0, :, self.label_column_name].to_list()
        semantic_scores: list[float] = (ctx.squeeze() @ memory_key.squeeze()).tolist()
        tokens_and_weights: dict[int, float] = {}
        for candidate, semantic_score in zip(candidates, semantic_scores):
            tokens = self.tokenizer(candidate)
            suffixes = self._find_suffixes_in_sequence(q_tokens[0], tokens, self.S_min, self.S_max)
            scores = self._extract_occurance_ranks(suffixes, len(tokens))
            for token, score in scores.items():
                if token not in tokens_and_weights or score > tokens_and_weights[token]:
                    tokens_and_weights[token] = score * semantic_score
        bag_of_words_tokens: list[list[int]] = cast(list[list[int]], self.tokenizer(candidates))
        return {token: score for token, score in tokens_and_weights.items()}, list(
            zip(
                bag_of_words_tokens,
                [x / len(candidates) for x in semantic_scores],
                strict=True,
            )
        )

    def forward(self, memory_key: Tensor, logits: Tensor, inpt_tokens: list[int]) -> Tensor:
        """
        Applies memory guidance to the model logits.

        Args:
            memory_key: The memory key to use for memory lookup.
            logits: The original model logits.
            inpt_tokens: The input tokens.

        Returns:
            The updated logits.
        """
        if self.training and not self.enable_in_training:
            return logits

        probs = torch.softmax(logits, dim=-1)
        candidates, bag_of_words = self._weighted_next_tokens_from_memory(memory_key, inpt_tokens)

        if self.alpha > 0.0:
            for token, score in candidates.items():
                probs[0][token] += self.alpha * score

        if self.beta > 0.0:
            probs[0] += self.beta * self._bag_of_words_probs(bag_of_words).to(probs.device)
        return probs


class OrcaRankingCrossAttentionLayer(OrcaLookupModule, LabelColumnNameMixin):
    """
    A transformer decoder layer block that does cross attention for rankings.

    Note that this is Ranking-specific, and the rankings returned by the lookup layer are used as
    the value-weights for the cross attention.

    The module contains the typical transformer components: multi-head attention, feed forward, and
    layer norm. The module also contains a lookup layer that looks up a vector in an Orca index and
    returns the top k results. These results are used as the memory context for the cross attention.
    """

    def __init__(
        self,
        model_dim: int,
        num_heads: int,
        num_memories: int,
        num_ranks: int,
        activation: Callable[[Tensor], Tensor] = F.relu,
        dropout: float = 0.1,
        split_retrieval_path: bool = False,
        projection_mode: ProjectionMode = ProjectionMode.LABEL,
        # Shared Settings
        database: OrcaDatabase | str | None = None,
        # Curate Settings
        curate_enabled: bool = False,
        # Lookup Settings
        memory_index_name: str | None = None,
        drop_exact_match: DropExactMatchOption | None = None,
        exact_match_threshold: float | None = None,
        shuffle_memories: bool = False,
        label_column_name: str | None = None,
    ):
        """
        Initializes the cross attention layer.

        Args:
            model_dim: The dimension of the input vector and hidden layers.
            num_heads: The number of heads to be used in the multi-head attention layer.
            num_memories: The number of memory vectors to be returned from the lookup.
            num_ranks: The number of ranks to be used for the memory context.
            activation: The activation function.
            dropout: The dropout rate.
            split_retrieval_path: Whether to split the retrieval path. This is used when the memory key is different from the input vector.
            projection_mode: The mode of projection to be used.
            database: The database instance to use for lookups and curate tracking.
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

        self.model_dim = model_dim
        self.num_heads = num_heads
        self.num_ranks = num_ranks
        self.activation = activation
        self.dropout = dropout
        self.split_retrieval_path = split_retrieval_path
        self.projection_mode = projection_mode
        self.label_column_name = label_column_name

        # Lookup settings will be automatically propagated to the lookup layer
        self.lookup = OrcaLabelLookupLayer()

        self.cross_attention = nn.MultiheadAttention(
            self.model_dim,
            self.num_heads,
            dropout=self.dropout,
            batch_first=True,
        )
        self.attn_norm = nn.LayerNorm(self.model_dim)

        self.linear1 = nn.Linear(self.model_dim, self.model_dim * 4)
        self.dropout1 = nn.Dropout(self.dropout)
        self.linear2 = nn.Linear(self.model_dim * 4, self.model_dim)
        self.dropout2 = nn.Dropout(self.dropout)
        self.ff_norm = nn.LayerNorm(self.model_dim)

    def forward(
        self,
        x: Tensor,  # Shape (batch_size, embedding_dim)
        ctx: Tensor | None = None,  # Shape (batch_size, num_memories, embedding_dim)
        ranks: Tensor | None = None,  # Shape (batch_size, num_memories, meta_column_count)
        memory_key: Tensor | None = None,  # Shape (batch_size, embedding_dim)
    ) -> Tensor:  # x is the input vector N x D, ctx is the memory context N x K x D
        """
        Performs cross attention on the input tensor and memory context.

        `x`, `ctx`, `ranks` act as `Q`, `K`, `V` for the cross attention layer.

        When `ctx` is `None`:

        * If `split_retrieval_path` is `False`, `x` is used as both `Q` and `K`.
        * If `split_retrieval_path` is `True`, `memory_key` is used as `K` (instead of `x`)

        Args:
            x: The input tensor of shape (`batch_size`, `embedding_dim`)
            ctx: The memory context tensor of shape (`batch_size`, `num_memories`, `embedding_dim`).
            ranks: The memory rank tensor of shape (`batch_size`, `num_memories`).
            memory_key: The memory key tensor of shape (`batch_size`, `embedding_dim`).

        Returns:
            The output tensor of shape (`batch_size`, `embedding_dim`).
        """
        if ctx is None or ranks is None:
            if self.split_retrieval_path and memory_key is None:
                raise ValueError("Split retrieval path requires either a memory key or context to be passed in")
            assert ranks is None and ctx is None, "Both ctx and ranks must be None or neither"
            # Shape of ctx: (batch_size, num_memories, embedding_dim)
            ctx, ranks = self.lookup(memory_key) if self.split_retrieval_path else self.lookup(x)

        x = x.unsqueeze(1)  # x goes from N x D --> N x 1 x D

        # setup the values for the cross attention based on normalizing the ranks from the memory contexts
        # higher rank means higher value
        normalized_ranks = ranks / self.num_ranks  # type: ignore

        values = normalized_ranks.unsqueeze(-1).expand(-1, -1, x.shape[-1])

        x, _ = self.cross_attention(x, ctx, values)  # N x 1 x D
        # x, _ = self.cross_attention(x, ctx, ctx)  # N x 1 x D

        x = x.squeeze(1)  # N x D
        x = self.attn_norm(x)  # N x D

        y = self.linear1(x)  # N x D*4
        y = self.activation(y)
        y = self.dropout1(y)
        y = self.linear2(y)  # N x D
        y = self.dropout2(y)
        x = self.ff_norm(y + x)  # N x D

        return x


class OrcaRankingHead(OrcaLookupModule, LabelColumnNameMixin):
    """
    A transformer decoder layer block that does cross attention with memory lookup for ranking problems
    """

    def __init__(
        self,
        model_dim: int,
        num_memories: int,
        num_ranks: int,
        num_layers: int = 1,
        num_heads: int = 8,
        activation: Callable[[Tensor], Tensor] = F.relu,
        dropout: float = 0.1,
        split_retrieval_path: bool = False,
        projection_mode: ProjectionMode = ProjectionMode.LABEL,
        memory_guide_weight: float = 0.0,
        single_lookup: bool = True,
        deep_residuals: bool = False,
        # Shared Settings
        database: OrcaDatabase | str | None = None,
        # Curate Settings
        curate_enabled: bool = False,
        # Lookup Settings
        memory_index_name: str | None = None,
        drop_exact_match: DropExactMatchOption | None = None,
        exact_match_threshold: float | None = None,
        shuffle_memories: bool = False,
        label_column_name: str | None = None,
    ):
        """
        Initializes the cross attention layer.

        Args:
            model_dim: The dimension of the input vector and hidden layers.
            num_memories: The number of memory vectors to be returned from the lookup.
            num_ranks: The number of ranks to be used for the memory context.
            num_layers: The number of attention blocks to be used, copies of OrcaClassificationCrossAttentionLayer.
            num_heads: The number of heads to be used in the multi-head attention layer.
            activation: The activation function.
            dropout: The dropout rate.
            split_retrieval_path: Whether to split the retrieval path.
            projection_mode: The mode of projection to be used.
            memory_guide_weight: The weight of the memory guide.
            single_lookup: Whether to use a single lookup.
            deep_residuals: Whether to use deep residuals.
            database: The OrcaDatabase instance to use for lookups and curate tracking.
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

        self.model_dim = model_dim
        self.num_heads = num_heads
        self.activation = activation
        self.dropout = dropout
        self.split_retrieval_path = split_retrieval_path
        self.projection_mode = projection_mode
        self.num_layers = num_layers
        self.memory_guide_weight = memory_guide_weight
        self.single_lookup = single_lookup
        self.deep_residuals = deep_residuals
        self.label_column_name = label_column_name

        self._memory_enabled = True

        # Lookup settings will be automatically propagated to the lookup layer
        self.lookup = OrcaLabelLookupLayer()

        self.memory_layers = nn.ModuleList(
            [
                # Lookup settings will be automatically propagated to this layer
                OrcaRankingCrossAttentionLayer(
                    model_dim=model_dim,
                    num_heads=num_heads,
                    num_memories=num_memories,
                    num_ranks=num_ranks,
                    activation=activation,
                    dropout=dropout,
                    split_retrieval_path=split_retrieval_path,
                    projection_mode=projection_mode,
                    database=database,
                )
                for _ in range(self.num_layers)
            ]
        )

        self.classifier = _LinearClassificationHead(
            model_dim=model_dim, num_labels=1, activation=activation, dropout=dropout
        )

    def forward(
        self,
        x: Tensor,
        ctx: Tensor | None = None,
        ctx_ranks: Tensor | None = None,
        memory_key: Tensor | None = None,
    ) -> Tensor:  # x is the input vector N x D, ctx is the memory context N x K x D
        """
        Performs cross attention on the input tensor and memory context.

        Args:
            x: The input tensor of shape (`batch_size`, `embedding_dim`).
            ctx: The memory context tensor of shape (`batch_size`, `num_memories`, `embedding_dim`).
                If `None`, the memory context is looked up based on the `memory_key` or input tensor.
            ctx_ranks: The memory rank tensor of shape (`batch_size`, `num_memories`).
                If `None`, the ranks are looked up along with the memory context.
            memory_key: The memory key tensor of shape (`batch_size`, `embedding_dim`).
                If `None`, the memory key is the input tensor.

        Returns:
            The output tensor of shape (`batch_size`, 1). The output is the rank of the input vector.
        """
        if (ctx is None or ctx_ranks is None) and self.single_lookup:
            assert ctx_ranks is None and ctx is None, "Both ctx and ranks must be None or neither"
            if memory_key is None:
                memory_key = x
            ctx, ctx_ranks = self.lookup(memory_key)
        if self._memory_enabled:
            for layer in self.memory_layers:
                y = layer(x, ctx, ctx_ranks, memory_key)
                if self.deep_residuals:
                    x = y + x
                else:
                    x = y
        x = self.classifier(x)
        return x

    def _orca_memory_toggle(self, enable: bool) -> None:
        """Toggles the memory layer on or off."""
        self._memory_enabled = enable


###################
### Training Utils
###################


# TODO: move this into a separate module
class OrcaMemoryDataset(Dataset):
    """
    A PyTorch Dataset that allows loading all data needed in a model run from the Orca database
    upfront which is more efficient. The dataset is generated by joining an index that contains
    the embeddings for the training data with an index that contains the embeddings for the memories
    (those might be the same). The join operation happens in large pages which speeds up the
    calculation over doing individual lookups for each batch.

    The dataset returns a tuple that contains:

    * The embedding for the training data: a Tensor of shape (`embedding_dim`, 1)
    * Any other columns that are specified to be retrieved from the training data table
    * The embeddings for the memories: a Tensor of shape (`num_memories`, `embedding_dim`)
    * Any other columns that are specified to be retrieved from the memory data table
    * The scores for the memories: a Tensor of shape (`num_memories`, 1)

    Examples:
        ```py
        import torch
        from torch.utils.data import DataLoader
        from orcalib.orca_torch import OrcaMemoryDataset

        dataset = OrcaMemoryDataset(
            db,
            index="train_index",
            columns="label",
            memory_index="memories_index",
            mem_columns="label",
            num_memories=10,
        )
        dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

        # training loop assuming we have a `model`
        optimizer = torch.optim.Adam(model.parameters())
        for x, x_labels, ctx, ctx_labels, ctx_scores in dataloader:
            optimizer.zero_grad()
            logits = model(x, ctx, torch.stack(ctx_labels).T, ctx_scores)
            loss = torch.nn.functional.cross_entropy(logits, x_labels)
            loss.backward()
            optimizer.step()
        ```
    """

    def __init__(
        self,
        db: OrcaDatabase,
        index: str,
        columns: list[str | ColumnHandle] | str | ColumnHandle,
        memory_index: str,
        mem_columns: list[str | ColumnHandle] | str | ColumnHandle,
        num_memories: int,
        *,
        page_size: int = 1000,
        verbose: bool = False,
        drop_exact_match: bool = False,
        exact_match_threshold: float = EXACT_MATCH_THRESHOLD,
        shuffle_memories: bool = False,
        cache_file_path: str | None = None,
    ):
        """
        Initializes the OrcaMemoryDataset.

        Args:
            db: The OrcaDatabase to fetch the index data from.
            index: The name of the index to fetch the data from.
            columns: The columns to fetch from the index. Can be a single column name, or a list of column names.
            memory_index: The name of the memory index to fetch the data from. (Generally the same as the index)
            mem_columns: The columns to fetch from the memory index. Can be a single column name, or a list of column names.
            num_memories: The number of memory vectors to fetch for each item vector.
            page_size: The page size to use when fetching the data from the database.
            verbose: Whether to print verbose logging information.
            drop_exact_match: Whether to drop the exact match (if found) always, never, or only during training or inference.
            exact_match_threshold: The minimum similarity score for something to be considered the exact match.
            shuffle_memories: Whether to shuffle the memories before returning them.
            cache_file_path: The path for the [pickle][pickle] file to use for caching the dataset. If `None`, caching is disabled.
        """
        self.db = db
        self.index = index
        self.memory_index = memory_index
        self.num_memories = num_memories
        self.columns = columns
        self.mem_columns = mem_columns
        self.num_memories = num_memories
        self.verbose = verbose
        self.drop_exact_match = drop_exact_match
        self.exact_match_threshold = exact_match_threshold
        self.shuffle_memories = shuffle_memories
        self.cache_file_path = cache_file_path

        if cache_file_path and os.path.exists(cache_file_path):
            with open(cache_file_path, "rb") as f:
                cached_data = pickle.load(f)
                self.length = cached_data["length"]
                self.num_pages = cached_data["num_pages"]
                self.page_size = cached_data["page_size"]
                self.pages = cached_data["pages"]
                self.memory_vectors = cached_data["memory_vectors"]
                self.mem_data = cached_data["mem_data"]
            return

        print(f"Fetching index-join page 0 for index {index}")

        first_page = self.db.full_vector_memory_join(
            index_name=index,
            memory_index_name=memory_index,
            num_memories=num_memories,
            query_columns=columns,  # type: ignore
            page_size=page_size,
            page_index=0,
            drop_exact_match=drop_exact_match,
            exact_match_threshold=exact_match_threshold,
            shuffle_memories=shuffle_memories,
        )

        print(f"Fetching vectors for memory index {memory_index}")

        self.memory_vectors = self.db._get_index_values_paginated(memory_index, page_size=page_size)

        print(f"Fetching memory data for memory index {memory_index} with columns {mem_columns}")

        mem_table: TableHandle = cast(TableHandle, db._get_index_table(memory_index))

        self.mem_data = dict(
            cast(
                list[tuple[int, dict[str, Any]]],
                mem_table.select(*self._ensure_list(mem_columns)).fetch(include_ids=True),
            )
        )

        self.length: int = first_page["total_size"]
        self.num_pages: int = first_page["num_pages"]
        self.page_size: int = first_page["page_size"]

        assert first_page["page_index"] == 0

        self.pages = {0: first_page}

        if cache_file_path:
            with open(cache_file_path, "wb") as f:
                pickle.dump(
                    {
                        "length": self.length,
                        "num_pages": self.num_pages,
                        "page_size": self.page_size,
                        "pages": self.pages,
                        "memory_vectors": self.memory_vectors,
                        "mem_data": self.mem_data,
                    },
                    f,
                )

    def _get_page_for_index(self, i: int) -> PagedResponse:
        """Get the page for a given location `i` in the dataset."""
        page_index = i // self.page_size  # type: ignore

        if page_index in self.pages:
            return self.pages[page_index]

        if self.verbose:
            print(
                f"Fetching index-join page {page_index} of {self.num_pages} for index {i} of {self.length} (query index: {self.index}, memory_index: {self.memory_index})"
            )

        page = self.db.full_vector_memory_join(
            index_name=self.index,
            memory_index_name=self.memory_index,
            num_memories=self.num_memories,
            query_columns=self.columns,  # type: ignore
            page_size=self.page_size,  # type: ignore
            page_index=page_index,
            drop_exact_match=self.drop_exact_match,
            exact_match_threshold=self.exact_match_threshold,
            shuffle_memories=self.shuffle_memories,
        )
        self.pages[page_index] = page
        return page

    def _ensure_list(self, x: Any) -> list[Any]:
        """Ensure that the given value is a list."""
        if isinstance(x, list):
            return x
        return [x]

    def _get_column_name(self, column: str | ColumnHandle) -> str:
        """Get the column name from the given column handle."""
        if isinstance(column, ColumnHandle):
            return column.column_name
        return column

    def _get_dict_values(
        self,
        d: dict[str, Any],
        keys: list[str | ColumnHandle] | str | ColumnHandle,
    ) -> list[Any]:
        """Get the values from the given dictionary for the given keys.

        Args:
            d: The dictionary to get the values from.
            keys: The keys to get the values for.

        Returns:
            The values from the dictionary for the given keys.
        """
        if isinstance(keys, list):
            col_names = [self._get_column_name(column) for column in keys]
            return [d[col_name] for col_name in col_names]
        else:
            col_name = self._get_column_name(keys)
            return d[col_name]

    def __getitem__(self, i: int) -> tuple[Tensor, list[Any] | Any, Tensor, list[list[Any] | Any], Tensor]:
        """
        Get the item at the given location `i` in the dataset.

        If the item is on a page that has not been loaded yet, the page is fetched from the database.

        Args:
            i: The index of the item to get.

        Returns:
            x: The embedding for the item of shape (`embedding_dim`, 1).
            x_columns: The value for the column or columns for the item that were fetched.
            ctx: The memory embeddings of shape (`num_memories`, `embedding_dim`).
            ctx_columns: The values for the column or columns for the memory embeddings that were fetched.
            ctx_scores: The scores between the memory embeddings and the item embedding of shape (`num_memories`).
        """

        if i >= cast(int, self.length):
            raise IndexError(f"Index {i} out of range for dataset of size {self.length}")
        page = self._get_page_for_index(i)
        sub_index = i % self.page_size  # type: ignore
        item = page["items"][sub_index]
        item_vector = Tensor(item["query_vector"])
        item_metadata = item["query_payload"]
        scores = Tensor(item["scores"])

        if not isinstance(self.columns, list) or (isinstance(self.columns, list) and len(self.columns) == 1):
            item_metadata = item_metadata[0]

        mem_vectors = Tensor([self.memory_vectors[mem] for mem in item["top_memories"]])

        mem_metadata = [self._get_dict_values(self.mem_data[mem], self.mem_columns) for mem in item["top_memories"]]

        return item_vector, item_metadata, mem_vectors, mem_metadata, scores

    def __len__(self) -> int:
        """Returns the length of the dataset"""
        return self.length

    def get_dict(self, i: int) -> dict:
        """
        Returns the dictionary for the items at the given location

        Args:
            i: The location of the item to get.

        Returns:
            A dictionary containing the item and memory data.
        """
        # TODO: Add an example to the docstring to document the output type
        page = self._get_page_for_index(i)
        sub_index = i % self.page_size
        return page["items"][sub_index]

    @deprecated("replicate this in the curator in the future")
    def get_score(self) -> float:
        # Do not document this function since we do not want it in the docs.
        total = 0
        contains_correct = 0
        count_correct = 0
        count_wrong = 0
        total_mems = 0
        for record in tqdm(self):  # type: ignore
            columns = record[1]
            if not isinstance(columns, list):
                label = columns
            else:
                # TODO: This is brittle, because it assumes the position of the label in the columns
                label = columns[1]
            # label = record[1][1]
            mem_labels = record[3]
            total += 1
            if label in mem_labels:
                contains_correct += 1
            for mem_label in mem_labels:  # type: ignore
                total_mems += 1
                if mem_label == label:
                    count_correct += 1
                else:
                    count_wrong += 1

        correct_rate = count_correct / total_mems
        hit_rate = contains_correct / total
        return correct_rate * hit_rate  # classification score

    def set_cache_file_path(self, path: str) -> None:
        """
        Set the cache file path for the dataset.

        Args:
            path: The path where the cache file will be stored.
        """
        self.cache_file_path = path

    def save(self) -> None:
        """
        Save the dataset to a file.
        """

        if self.cache_file_path is None:
            raise ValueError("No cache file path was provided")

        with open(self.cache_file_path, "wb") as f:
            pickle.dump(
                {
                    "length": self.length,
                    "num_pages": self.num_pages,
                    "page_size": self.page_size,
                    "pages": self.pages,
                    "memory_vectors": self.memory_vectors,
                    "mem_data": self.mem_data,
                },
                f,
            )

    def load(self, path: str) -> None:
        """
        Load the dataset from a file.

        Args:
            path: The path to the [pickle][pickle] file on disk to load the dataset from.
        """

        self.set_cache_file_path(path)

        with open(self.cache_file_path, "rb") as f:
            cached_data = pickle.load(f)
            self.length = cached_data["length"]
            self.num_pages = cached_data["num_pages"]
            self.page_size = cached_data["page_size"]
            self.pages = cached_data["pages"]
            self.memory_vectors = cached_data["memory_vectors"]
            self.mem_data = cached_data["mem_data"]


@deprecated("This is not the recommended way to train models anymore")
class OrcaTextClassificationTrainer:
    """
    A simple trainer class for Text Classification Problems with Orca. Intended for quick
    prototyping, not to outperform a custom training loop.

    Warning: Deprecated:
        This class is not the recommended way to train models anymore.
    """

    def __init__(
        self,
        model,
        tokenizer,
        trainloader: DataLoader,
        testloader: DataLoader,
        use_memory: bool = True,
        memory_dropout: float = 0.0,
        device_override: str | None = None,
        param_groups: None | list[dict[str, Any]] = None,
        verbosity: int = 0,
    ):
        """
        Initializes the trainer

        Args:
            model: The model to train.
            tokenizer: The tokenizer to use for encoding the input data.
            trainloader: The DataLoader for the training data.
            testloader: The DataLoader for the test data.
            use_memory: Whether to use memory for the model.
            memory_dropout: The dropout rate to use for the memory.
            device_override: The device to use for training. If None, the device will be automatically selected based on the availability of CUDA.
            param_groups: The parameter groups to use for training. If None, the model parameters will be used.
            verbosity: The verbosity level to use for training.
        """
        self.model = model
        self.tokenizer = tokenizer
        self.trainloader = trainloader
        self.testloader = testloader
        self.use_memory = use_memory
        self.verbosity = verbosity
        if memory_dropout < 0.0 or memory_dropout > 1.0:
            raise ValueError("memory_dropout must be between 0.0 and 1.0")
        self.memory_dropout = memory_dropout
        if device_override is not None:
            self.device = torch.device(device_override)
            self.dtype = torch.float32
        elif torch.cuda.is_available():
            self.device = torch.device("cuda")
            self.dtype = torch.bfloat16
        elif torch.backends.mps.is_available():  # type: ignore
            self.device = torch.device("mps")
            self.dtype = torch.float32
        else:
            self.device = torch.device("cpu")
            self.dtype = torch.float32
        self.param_groups = param_groups
        self.model = self.model.to(self.device, dtype=self.dtype)
        self.criterion = torch.nn.CrossEntropyLoss()
        if param_groups is None:
            param_groups = model.parameters()
        self.optimizer = torch.optim.Adam(param_groups, lr=0.001)  # type: ignore

    def _get_accuracy(self, logits, labels) -> float:
        """Computes and returns the accuracy of the model.

        Args:
            logits: The logits from the model.
            labels: The labels for the data.

        Returns:
            The accuracy of the model.
        """
        _, preds = torch.max(logits, 1)
        return (preds == labels).float().mean().item()

    def get_test_accuracy(self, testloader_override: DataLoader | None = None) -> float:
        """Computes and returns the average accuray of the model either on the main testset (from the constructor) or on the provided testloader_override.

        Args:
            testloader_override: The DataLoader to use for the testset. If None, the main testset will be used.

        Returns:
            The average accuracy of the model on the testset.
        """
        self.model.eval()
        if testloader_override is not None:
            testloader = testloader_override
        else:
            testloader = self.testloader
        with torch.no_grad():
            test_acc = 0.0
            test_steps = 0
            for _, keys_and_labels, ctxs, ctx_labels, scores in tqdm(testloader, desc="Processing Testset"):
                keys = keys_and_labels[0]
                labels = keys_and_labels[1]
                ctx_labels = torch.stack(ctx_labels).T
                encoding = self.tokenizer(
                    keys,
                    add_special_tokens=True,
                    padding="max_length",
                    return_tensors="pt",
                )
                inputs = encoding["input_ids"]
                mask = encoding["attention_mask"]
                inputs, mask, labels, ctxs, ctx_labels = (
                    inputs.to(self.device),
                    mask.to(self.device),
                    labels.to(self.device),
                    ctxs.to(self.device).to(self.dtype),
                    ctx_labels.to(self.device),
                )
                if self.use_memory:
                    outputs = self.model(inputs, mask, ctxs, ctx_labels)
                else:
                    outputs = self.model(inputs, mask)
                test_acc += self._get_accuracy(outputs, labels)
                test_steps += 1
            avg_test_acc = test_acc / test_steps
        self.model.train()
        return avg_test_acc

    def _train_one_epoch(self, epoch: int, num_epochs: int) -> None:
        """Trains the model for one epoch."""
        self.model.train()
        running_loss = 0.0
        running_acc = 0.0
        steps = 0
        for _, keys_and_labels, ctxs, ctx_labels, scores in tqdm(self.trainloader, desc="Processing Trainset"):
            keys = keys_and_labels[0]
            labels = keys_and_labels[1]
            ctx_labels = torch.stack(ctx_labels).T
            encoding = self.tokenizer(keys, add_special_tokens=True, padding="max_length", return_tensors="pt")
            inputs = encoding["input_ids"]
            mask = encoding["attention_mask"]
            if self.memory_dropout > 0.0:
                num_mems_max = 20  # TODO: factor out memory size as global a constant
                cutoff = int(num_mems_max * (1.0 - self.memory_dropout))
                filter = torch.randperm(num_mems_max)[:cutoff]
                ctxs = ctxs[:, filter, :]
                ctx_labels = ctx_labels[:, filter]
            inputs, mask, labels, ctxs, ctx_labels = (
                inputs.to(self.device),
                mask.to(self.device),
                labels.to(self.device),
                ctxs.to(self.device).to(self.dtype),
                ctx_labels.to(self.device),
            )
            self.optimizer.zero_grad()
            if self.use_memory:
                outputs = self.model(inputs, mask, ctxs, ctx_labels)
            else:
                outputs = self.model(inputs, mask)
            loss = self.criterion(outputs, labels)
            loss.backward()
            self.optimizer.step()

            running_loss += loss.item()
            running_acc += self._get_accuracy(outputs, labels)
            steps += 1
            if self.verbosity > 0 and steps % self.verbosity == 0:
                avg_loss = running_loss / steps
                avg_acc = running_acc / steps
                print(f"Epoch [{epoch}/{num_epochs}], Step [{steps}], Loss: {avg_loss:.4f}, Accuracy: {avg_acc:.4f}")

        avg_loss = running_loss / steps
        avg_acc = running_acc / steps
        print(
            f"Epoch [{epoch}/{num_epochs}], Loss: {avg_loss:.4f}, Accuracy: {avg_acc:.4f}, Test Accuracy: {self.get_test_accuracy():.4f}"
        )

    def train(self, num_epochs=10) -> None:
        """Trains the model for the given number of epochs.

        Args:
            num_epochs: The number of epochs to train for.
        """
        for epoch in range(num_epochs):
            self._train_one_epoch(epoch + 1, num_epochs)


def embed(strings: list[str], model: EmbeddingModel = EmbeddingModel.SENTENCE_TRANSFORMER) -> Tensor:
    """
    Generate embeddings for a list of strings.

    Args:
        strings: The list of strings to generate embeddings for.
        model: The embedding model to use.

    Returns:
        the embeddings of shape (`len(strings)`, `embedding_dim`)

    Examples:
        >>> embed(["hello", "world"]).shape
        torch.Size([2, 768])
    """
    return torch.tensor(OrcaClient.encode_text(strings, model=model))
