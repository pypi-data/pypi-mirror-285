import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from typing import Any, Callable, Iterable, Optional
from uuid import UUID

import torch

from orca_common import EXACT_MATCH_THRESHOLD, ColumnName
from orcalib.batched_scan_result import BatchedScanResult
from orcalib.client import OrcaMetadataDict
from orcalib.curate._tracking import RunId
from orcalib.database import OrcaDatabase

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ProjectionMode(str, Enum):
    """
    Determines how the values from the memory should be "projected" into the models embedding
    space (i.e. what's the V in the attention mechanism QKV).

    Attributes:
        LABEL: Project the memory's label into the model embedding space.
        POSITIONAL: Project the memory's position (0...num_memories-1) into the model embedding space.
    """

    LABEL = 0
    POSITIONAL = 1


class ClassificationMode(str, Enum):
    """Determined how the final classification is performed.

    Attributes:
        DIRECT: Predicts directly into `num_classes` like a conventional classification model.
        MEMORY_BOUND: which uses memory binding to make the prediction (i.e. pick from the classes
            in the memories).
    """

    DIRECT = 0
    MEMORY_BOUND = 1


class DropExactMatchOption(str, Enum):
    """
    Determines when to drop exact matches from the results.

    Attributes:
        ALWAYS: Always drop exact matches from the results.
        NEVER: Never drop exact matches from the results.
        TRAINING_ONLY: Drop exact matches from the results only during training.
        INFERENCE_ONLY: Drop exact matches from the results only during inference.
    """

    ALWAYS = "ALWAYS"
    NEVER = "NEVER"
    TRAINING_ONLY = "TRAINING_ONLY"
    INFERENCE_ONLY = "INFERENCE_ONLY"


class PostInitMixin(ABC):
    """
    Mixin class that adds an (abstract) post_init() and wraps descendent's __init__() to call it.

    **Note:**

    If PostInitMixin appears more than once in the inheritance chain, only the outermost class will
    run post_init(). In other words, the post_init method will only be called once, after all other
    init methods have been called, even if there are multiple PostInitMixin classes in the
    inheritance chain.
    """

    def __init_subclass__(cls) -> None:
        # This method is called when a subclass of the class is created. It modifies the class
        # directly by wrapping the __init__ method with custom logic.
        super().__init_subclass__()

        old_init = cls.__init__

        def wrapped_init(self, *args, **kwargs):
            # We only want to run post_init once after all other init methods have been called,
            # so only the outermost class will run post_init.
            skip_post_init = getattr(self, "_skip_post_init", False)
            self._skip_post_init = True

            old_init(self, *args, **kwargs)
            if not skip_post_init:
                self.post_init()

        # Modify the class directly
        cls.__init__ = wrapped_init

    @abstractmethod
    def post_init(self) -> None:
        """Override this function to execute code after the __init__ method."""
        ...


class PreForwardMixin(ABC):
    """Mixin class that adds an (abstract) pre_forward() and wraps descendent's forward() to call it before the
    original forward method.

    NOTE: This uses functools.wraps to wrap the forward method, so the original forward method's signature is preserved.
    """

    def __init_subclass__(cls) -> None:
        # This method is called when a subclass of OrcaModel is created. It modifies the class
        # directly by wrapping the forward method with custom logic.
        super().__init_subclass__()

        forward_method = cls.forward

        @wraps(forward_method)
        def wrapped_forward(self, *args, **kwargs):
            self.pre_forward(*args, **kwargs)
            output = forward_method(self, *args, **kwargs)
            self.post_forward(output)
            return output

        cls.forward = wrapped_forward

    @abstractmethod
    def pre_forward(self, *args, **kwargs):
        """Override this function to execute code before the forward method is called."""
        ...

    @abstractmethod
    def post_forward(self, output):
        """Override this function to execute code right after the forward method returned."""
        ...

    @abstractmethod
    def forward(self, *args, **kwargs):
        ...


@dataclass
class CurateModelRunSettings:
    tags: set[str]
    metadata: OrcaMetadataDict
    seq_id: UUID | None = None
    batch_size: int | None = None


@dataclass
class CurateSettings:
    curate_database_name: str | None = None
    curate_enabled: bool = False
    tags: set[str] = field(default_factory=set)
    metadata: OrcaMetadataDict = field(default_factory=dict)
    model_id: str | None = None
    model_version: str | None = None
    seq_id: UUID | None = None
    batch_size: int | None = None
    last_batch_size: int | None = None
    last_run_ids: list[int] | None = None
    next_run_settings: CurateModelRunSettings | None = None
    last_run_settings: CurateModelRunSettings | None = None


class CurateSettingsMixin:
    """Mixin that adds curate settings to a class as self.curate_settings, then
    provides properties to access the individual settings.

    Note:
        This class is intended to be used with OrcaModule classes, and should not be used directly.
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
        Initializes the CurateSettings object.

        Args:
            curate_database: The database to use for saving curate tracking data.
            model_id: The model id to associate with curated model runs.
            model_version: The model version to associate with curated model runs.
            metadata: The metadata to attach to curated model runs.
            curate_enabled: Whether the model should collect curate tracking data during eval runs.
            tags: The tags to attach to the curated model runs.
        """
        self._orca_curate_settings = CurateSettings(
            curate_database_name=curate_database.name if isinstance(curate_database, OrcaDatabase) else curate_database,
            model_id=model_id,
            model_version=model_version,
            metadata=metadata or {},
            tags=set(tags) if tags is not None else set(),
        )
        self.curate_layer_name: str | None = None
        self.curate_enabled = curate_enabled

    @property
    def curate_database(self) -> str | None:
        """The name of the database to use for saving curate tracking data."""
        return self._orca_curate_settings.curate_database_name

    @curate_database.setter
    def curate_database(self, value: OrcaDatabase | str | None) -> None:
        self._orca_curate_settings.curate_database_name = value.name if isinstance(value, OrcaDatabase) else value

    @property
    def curate_next_run_settings(self) -> CurateModelRunSettings | None:
        """The settings for the next curate model run."""
        return self._orca_curate_settings.next_run_settings

    @curate_next_run_settings.setter
    def curate_next_run_settings(self, value: CurateModelRunSettings | None) -> None:
        self._orca_curate_settings.next_run_settings = value

    @property
    def curate_model_id(self) -> str | None:
        """The model id to associate with curated model runs."""
        return self._orca_curate_settings.model_id

    @curate_model_id.setter
    def curate_model_id(self, value: str | None) -> None:
        self._orca_curate_settings.model_id = value

    @property
    def curate_model_version(self) -> str | None:
        """The model version to associate with curated model runs."""
        return self._orca_curate_settings.model_version

    @curate_model_version.setter
    def curate_model_version(self, value: str | None) -> None:
        self._orca_curate_settings.model_version = value

    @property
    def curate_metadata(self) -> OrcaMetadataDict:
        """The metadata to attach to curated model runs."""
        return self._orca_curate_settings.metadata

    @curate_metadata.setter
    def curate_metadata(self, value: OrcaMetadataDict) -> None:
        for _, v in value.items():
            assert isinstance(v, (str, int, float, bool, list)), f"Metadata value must be a simple type, not {type(v)}"
            if isinstance(v, list):
                assert all(
                    isinstance(x, (str, int, float, bool)) for x in v
                ), f"Metadata value must be a simple type, not {type(v)}"
        self._orca_curate_settings.metadata = value

    @property
    def curate_tags(self) -> set[str]:
        """The tags to attach to the curated model runs."""
        return self._orca_curate_settings.tags

    @curate_tags.setter
    def curate_tags(self, value: Iterable[str] | None) -> None:
        self._orca_curate_settings.tags = set(value) if value is not None else set()

    @property
    def curate_seq_id(self) -> UUID | None:
        """The sequence id to associate with curated model runs."""
        return self._orca_curate_settings.seq_id

    @curate_seq_id.setter
    def curate_seq_id(self, value: UUID | None) -> None:
        self._orca_curate_settings.seq_id = value

    @property
    def curate_batch_size(self) -> int | None:
        """The batch size of the model run to track curate data for, usually inferred automatically."""
        return self._orca_curate_settings.batch_size

    @curate_batch_size.setter
    def curate_batch_size(self, value: int | None) -> None:
        self._orca_curate_settings.batch_size = value

    @property
    def last_curate_run_ids(self) -> list[RunId] | None:
        """The run ids of the last model run for which curate tracking data was collected."""
        return self._orca_curate_settings.last_run_ids

    @last_curate_run_ids.setter
    def last_curate_run_ids(self, value: list[RunId] | None) -> None:
        self._orca_curate_settings.last_run_ids = value

    @property
    def last_curate_run_settings(self) -> CurateModelRunSettings | None:
        """The settings of the last model run for which curate tracking data was collected."""
        return self._orca_curate_settings.last_run_settings

    @last_curate_run_settings.setter
    def last_curate_run_settings(self, value: CurateModelRunSettings | None) -> None:
        self._orca_curate_settings.last_run_settings = value


LookupResultTransform = Callable[[BatchedScanResult], BatchedScanResult]


@dataclass
class LookupSettings:
    lookup_database_name: str | None = None
    lookup_database_instance: OrcaDatabase | None = None
    memory_index_name: str | None = None
    lookup_column_names: list[str] | None = None
    num_memories: int | None = None
    drop_exact_match: DropExactMatchOption | None = DropExactMatchOption.NEVER
    exact_match_threshold: float | None = None
    shuffle_memories: bool = False
    freeze_num_memories: bool = False  # If True, the number of memories will not be changed once set
    lookup_result_override: BatchedScanResult = None
    lookup_result_transforms: LookupResultTransform | list[LookupResultTransform] | None = None
    lookup_query_override: list[list[float]] | torch.Tensor | None = None
    extra_lookup_column_names: list[str] | None = None

    def __or__(self, other: "LookupSettings") -> "LookupSettings":
        # Merges two LookupSettings objects, preferring the values in self if they are set.
        return LookupSettings(
            lookup_database_name=(
                self.lookup_database_name if self.lookup_database_name is not None else other.lookup_database_name
            ),
            lookup_database_instance=(
                self.lookup_database_instance
                if self.lookup_database_instance is not None
                else other.lookup_database_instance
            ),
            memory_index_name=self.memory_index_name if self.memory_index_name is not None else other.memory_index_name,
            lookup_column_names=(
                self.lookup_column_names if self.lookup_column_names is not None else other.lookup_column_names
            ),
            num_memories=self.num_memories if self.num_memories is not None else other.num_memories,
            drop_exact_match=self.drop_exact_match if self.drop_exact_match is not None else other.drop_exact_match,
            exact_match_threshold=(
                self.exact_match_threshold if self.exact_match_threshold is not None else other.exact_match_threshold
            ),
            shuffle_memories=self.shuffle_memories if self.shuffle_memories is not None else other.shuffle_memories,
            lookup_result_override=self.lookup_result_override
            if self.lookup_result_override is not None
            else other.lookup_result_override,
            lookup_result_transforms=self.lookup_result_transforms
            if self.lookup_result_transforms is not None
            else other.lookup_result_transforms,
            lookup_query_override=self.lookup_query_override
            if self.lookup_query_override is not None
            else other.lookup_query_override,
            extra_lookup_column_names=self.extra_lookup_column_names
            if self.extra_lookup_column_names is not None
            else other.extra_lookup_column_names,
        )


@dataclass()
class DatabaseIndexName:
    """Holds the name of an index and its associated database.

    Attributes:
        database_name (str): The name of database for the index
        index_name (str): The name of the index
    """

    database_name: str
    index_name: str

    def __repr__(self) -> str:
        return f"DatabaseIndexName({self.database_name}, {self.index_name})"

    def __str__(self) -> str:
        return f"{self.database_name}.{self.index_name}"

    def __hash__(self) -> int:
        return hash((self.database_name, self.index_name))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, DatabaseIndexName):
            return False
        return self.database_name == other.database_name and self.index_name == other.index_name


@dataclass
class LookupSettingsSummary:
    """A summary of lookup settings for a collection of OrcaLookupModule instances that share the same
    database and index.

    Note:
        The summary doesn't actually summarize over all possible settings, but instead chooses to ignore
        the "override" settings (e.g., lookup_result_override, lookup_query_override).

    Attributes:
        lookup_database_name (str): The name of the database used for looking up memories. This is half
            of the key for the summary; the other half is the memory index name.
        memory_index_name (str): The name of the index used for looking up memories. This is half of the
            key for the summary; the other half is the lookup database name.
        lookup_column_names (list[str]): A list of lookup columns that were requested by any of the
            [`LookupSettings`] in this summary.
        num_memories_range (tuple[int, int] | None): The range of the number of memories to look up across
            all [`LookupSettings`] in this summary. This will be `None` if `num_memories` was not set in any
            of the [`LookupSettings`].
        drop_exact_match (list[DropExactMatchOption]): The options for dropping exact matches from the results
            for all [`LookupSettings`] in this summary. This will be `[]` if no drop-exact-match options were set.
        exact_match_thresholds (list[float]): The exact-match thresholds for all [`LookupSettings`] in this
            this summary. This will be `[]` if no exact-match thresholds were set.
        shuffle_memories (list[bool]): The shuffle-memories options for all [`LookupSettings`] in this summary.
            This will be `[]` if no shuffle-memories options were set.

    Example:
        ```python
        settings1 = LookupSettings(
            lookup_database_name="test_db",
            memory_index_name="test_index1",
            lookup_column_names=["col1", "col2", "$score"],
            num_memories=10,
            drop_exact_match=DropExactMatchOption.NEVER,
        )

        settings2 = LookupSettings(
            lookup_database_name="test_db",
            memory_index_name="test_index1",
            lookup_column_names=["col2", "col3"],
            num_memories=20,
            drop_exact_match=DropExactMatchOption.ALWAYS,
        )

        summary = LookupSettingsSummary.from_lookup_settings([settings1, settings2])
        ```
        Result:
        ```python
        {
            DatabaseIndexName("test_db", "test_index1"): LookupSettingsSummary(
                lookup_database_name="test_db",
                memory_index_name="test_index1",
                lookup_column_names=["col1", "col2", "col3", "$score"],
                num_memories_range=(10, 20),
                drop_exact_match=[DropExactMatchOption.NEVER, DropExactMatchOption.ALWAYS],
                exact_match_thresholds=[],
                shuffle_memories=[],
            )
        }
        ```


    """

    lookup_database_name: str
    memory_index_name: str
    lookup_column_names: list[str] = field(default_factory=list)
    num_memories_range: tuple[int, int] | None = None
    drop_exact_match: list[DropExactMatchOption] = field(default_factory=list)
    exact_match_thresholds: list[float] = field(default_factory=list)
    shuffle_memories: list[bool] = field(default_factory=list)

    def __or__(self, settings: LookupSettings) -> "LookupSettingsSummary":
        """Merges a LookupSettings object into the LookupSettingsSummary object.

        Args:
            settings (LookupSettings): The LookupSettings object to merge.

        Returns:
            LookupSettingsSummary: The merged LookupSettingsSummary object.
        """
        if (
            self.lookup_database_name != settings.lookup_database_name
            or self.memory_index_name != settings.memory_index_name
        ):
            raise ValueError(
                f"Cannot merge LookupSettings with different database or index names: {self} and {settings}"
            )

        def get_unique_union(a: list, b: Any) -> list:
            if isinstance(b, list):
                return list(set(a + b))
            if b is not None:
                return list(set(a + [b]))
            return list(a)

        new_range = self.num_memories_range
        if settings.num_memories is not None:
            if new_range is None:
                new_range = (settings.num_memories, settings.num_memories)
            else:
                new_range = (
                    min(new_range[0], settings.num_memories),
                    max(new_range[1], settings.num_memories),
                )

        return LookupSettingsSummary(
            lookup_database_name=self.lookup_database_name,
            memory_index_name=self.memory_index_name,
            lookup_column_names=get_unique_union(self.lookup_column_names, settings.lookup_column_names),
            num_memories_range=new_range,
            drop_exact_match=get_unique_union(self.drop_exact_match, settings.drop_exact_match),
            exact_match_thresholds=get_unique_union(self.exact_match_thresholds, settings.exact_match_threshold),
            shuffle_memories=get_unique_union(self.shuffle_memories, settings.shuffle_memories),
        )

    @classmethod
    def from_lookup_settings(
        cls, lookup_settings: Iterable[LookupSettings]
    ) -> dict[DatabaseIndexName, "LookupSettingsSummary"]:
        """Create a dictionary of LookupSettingsSummary objects from a collection of LookupSettings objects.
        This is useful for summarizing the lookup settings for a collection of [`OrcaLookupModule`][orcalib.orca_torch.OrcaLookupModule]
        instances. The keys of the dictionary are [`DatabaseIndexName`][orcalib.DatabaseIndexName] objects, so we have
        a separate summary object for each unique database–index combination.

        Args:
            lookup_settings): An iterable collection LookupSettings objects to summarize.

        Returns:
            A dictionary of [`DatabaseIndexName`][orcalib.DatabaseIndexName] objects to LookupSettingsSummary objects.
        """
        summary = {}
        for settings in lookup_settings:
            key = DatabaseIndexName(settings.lookup_database_name, settings.memory_index_name)
            if key not in summary:
                summary[key] = LookupSettingsSummary(
                    lookup_database_name=key.database_name, memory_index_name=key.index_name
                )
            summary[key] = summary[key] | settings
        return summary


class LookupSettingsMixin:
    """Mixin that adds lookup settings to a class as self.lookup_settings, then provides properties to
    access the individual settings.

    Note:
        This class is intended to be used with OrcaModule classes, and should not be used directly.
    """

    def __init__(
        self,
        lookup_database: OrcaDatabase | str | None = None,
        memory_index_name: str | None = None,
        lookup_column_names: list[str] | None = None,
        num_memories: int | None = None,
        drop_exact_match: DropExactMatchOption | None = None,
        exact_match_threshold: float | None = None,
        shuffle_memories: bool = False,
        lookup_result_override: BatchedScanResult | None = None,
        lookup_result_transforms: LookupResultTransform | list[LookupResultTransform] | None = None,
        lookup_query_override: list[list[float]] | torch.Tensor | None = None,
        extra_lookup_column_names: list[str] | None = None,
        freeze_num_memories: bool = False,
        propagate_lookup_settings: bool = True,
    ):
        """
        Initializes the mixin.

        Args:
            lookup_database: The database to use for looking up memories.
            memory_index_name: The name of the index to use for looking up memories.
            lookup_column_names: The names of the columns to retrieve for each memory.
            num_memories: The number of memories to look up.
            drop_exact_match: Whether to drop exact matches from the results.
            exact_match_threshold: The similarity threshold for exact matches.
            shuffle_memories: Whether to shuffle the looked up memories.
            freeze_num_memories: Whether to freeze the number of memories once set.
            propagate_lookup_settings: Whether to propagate lookup settings to child modules.
        """
        self._orca_lookup_settings = LookupSettings(
            lookup_database_name=lookup_database.name if isinstance(lookup_database, OrcaDatabase) else lookup_database,
            lookup_database_instance=lookup_database if isinstance(lookup_database, OrcaDatabase) else None,
            memory_index_name=memory_index_name,
            lookup_column_names=lookup_column_names,
            num_memories=num_memories,
            drop_exact_match=drop_exact_match,
            exact_match_threshold=exact_match_threshold,
            shuffle_memories=shuffle_memories,
            lookup_result_override=lookup_result_override,
            lookup_result_transforms=lookup_result_transforms,
            lookup_query_override=lookup_query_override,
            extra_lookup_column_names=extra_lookup_column_names,
            freeze_num_memories=freeze_num_memories,
        )
        self.propagate_lookup_settings = propagate_lookup_settings
        self._inherited_orca_lookup_settings = LookupSettings()

    def get_effective_lookup_settings(self) -> LookupSettings:
        """Returns the effective lookup settings for this module, with any inherited settings applied.

        Returns:
            The effective lookup settings for this module. Practically, this be the lookup settings
            set on this module. For any settings that are not set on this module, the inherited settings
            will be used instead.
        """
        return self._orca_lookup_settings | self._inherited_orca_lookup_settings

    def _propagate_lookup_settings(self) -> None:
        """Propagates lookup settings to the nearest OrcaLookupModules through each of its children."""
        from orcalib.orca_torch import OrcaLookupModule

        assert isinstance(
            self, OrcaLookupModule
        ), "_propagate_lookup_settings() should only be called from OrcaLookupModule"

        for module in self.get_orca_modules_recursively(max_depth=1, include_self=False, filter_type=OrcaLookupModule):
            if self.propagate_lookup_settings:
                module._inherited_orca_lookup_settings = (
                    self._orca_lookup_settings | self._inherited_orca_lookup_settings
                )
            module._propagate_lookup_settings()

    def update_lookup_settings(
        self,
        database: OrcaDatabase | str | None = None,
        memory_index_name: str | None = None,
        lookup_column_names: list[str] | None = None,
        num_memories: int | None = None,
        drop_exact_match: DropExactMatchOption | None = None,
        exact_match_threshold: float | None = None,
        shuffle_memories: bool = False,
        lookup_result_override: BatchedScanResult | None = None,
        lookup_result_transforms: LookupResultTransform | list[LookupResultTransform] | None = None,
        lookup_query_override: list[list[float]] | torch.Tensor | None = None,
        extra_lookup_column_names: list[str] | None = None,
    ):
        self._orca_lookup_settings |= LookupSettings(
            lookup_database_name=database.name if isinstance(database, OrcaDatabase) else database,
            lookup_database_instance=database if isinstance(database, OrcaDatabase) else None,
            memory_index_name=memory_index_name,
            lookup_column_names=lookup_column_names,
            num_memories=num_memories,
            drop_exact_match=drop_exact_match,
            exact_match_threshold=exact_match_threshold,
            shuffle_memories=shuffle_memories,
            lookup_result_override=lookup_result_override,
            lookup_result_transforms=lookup_result_transforms,
            lookup_query_override=lookup_query_override,
            extra_lookup_columns=extra_lookup_column_names,
        )
        self._propagate_lookup_settings()

    @property
    def lookup_result_transforms(self) -> LookupResultTransform | list[LookupResultTransform] | None:
        """A list of transforms to apply to the lookup result. NOTE: This will be applied even when lookup_result_override is set."""
        return (
            self._orca_lookup_settings.lookup_result_transforms
            or self._inherited_orca_lookup_settings.lookup_result_transforms
        )

    @lookup_result_transforms.setter
    def lookup_result_transforms(self, value: LookupResultTransform | list[LookupResultTransform] | None) -> None:
        self._orca_lookup_settings.lookup_result_transforms = value
        self._propagate_lookup_settings()

    @property
    def extra_lookup_column_names(self) -> list[str] | None:
        """While set, all lookups will include these additional columns. They may inclue
        columns on the indexed table as well as index-specific columns, e.g., $score, $embedding."""
        return (
            self._orca_lookup_settings.extra_lookup_column_names
            or self._inherited_orca_lookup_settings.extra_lookup_column_names
        )

    @extra_lookup_column_names.setter
    def extra_lookup_column_names(self, value: list[str] | None) -> None:
        self._orca_lookup_settings.extra_lookup_column_names = value
        self._propagate_lookup_settings()

    @property
    def lookup_query_override(self) -> list[list[float]] | torch.Tensor | None:
        """The query to use instead of performing a lookup. NOTE: This will be ignored if lookup_result_override is also set."""
        return (
            self._orca_lookup_settings.lookup_query_override
            if self._orca_lookup_settings.lookup_query_override is not None
            else self._inherited_orca_lookup_settings.lookup_query_override
        )

    @lookup_query_override.setter
    def lookup_query_override(self, value: list[list[float]] | torch.Tensor | None) -> None:
        self._orca_lookup_settings.lookup_query_override = value
        self._propagate_lookup_settings()

    @property
    def lookup_result_override(self) -> BatchedScanResult | None:
        """The lookup result to use instead of performing a lookup."""
        return (
            self._orca_lookup_settings.lookup_result_override
            or self._inherited_orca_lookup_settings.lookup_result_override
        )

    @lookup_result_override.setter
    def lookup_result_override(self, value: BatchedScanResult | None) -> None:
        self._orca_lookup_settings.lookup_result_override = value
        self._propagate_lookup_settings()

    @property
    def lookup_database(self) -> str | None:
        """The name of the database to use for looking up memories."""
        return (
            self._orca_lookup_settings.lookup_database_name or self._inherited_orca_lookup_settings.lookup_database_name
        )

    @lookup_database.setter
    def lookup_database(self, value: OrcaDatabase | str | None) -> None:
        if isinstance(value, OrcaDatabase):
            self._orca_lookup_settings.lookup_database_name = value.name
            self._orca_lookup_settings.lookup_database_instance = value
        elif isinstance(value, str):
            self._orca_lookup_settings.lookup_database_name = value
            self._orca_lookup_settings.lookup_database_instance = None
        elif value is None:
            self._orca_lookup_settings.lookup_database_name = None
            self._orca_lookup_settings.lookup_database_instance = None
        else:
            raise ValueError(f"Lookup Database is wrong type: {type(value)}. Expected str or OrcaDatabase")
        self._propagate_lookup_settings()

    def get_lookup_database_instance(self) -> OrcaDatabase:
        """Returns the OrcaDatabase instance to use for looking up memories."""
        if (
            self._orca_lookup_settings.lookup_database_instance is None
            and self._inherited_orca_lookup_settings.lookup_database_instance is None
        ):
            if self._orca_lookup_settings.lookup_database_name is None:
                if self._inherited_orca_lookup_settings.lookup_database_name is None:
                    raise ValueError("Lookup Database is not set.")
                # we do not want to overwrite self lookup settings with any inherited settings
                self._inherited_orca_lookup_settings.lookup_database_instance = OrcaDatabase(
                    self._inherited_orca_lookup_settings.lookup_database_name
                )
                self._propagate_lookup_settings()
            else:
                self._orca_lookup_settings.lookup_database_instance = OrcaDatabase(
                    self._orca_lookup_settings.lookup_database_name
                )
                self._propagate_lookup_settings()
        assert (
            self._orca_lookup_settings.lookup_database_instance is not None
            or self._inherited_orca_lookup_settings.lookup_database_instance is not None
        )
        return (
            self._orca_lookup_settings.lookup_database_instance
            or self._inherited_orca_lookup_settings.lookup_database_instance
        )

    @property
    def memory_index_name(self) -> str | None:
        """The name of the index to use for looking up memories."""
        return self._orca_lookup_settings.memory_index_name or self._inherited_orca_lookup_settings.memory_index_name

    @memory_index_name.setter
    def memory_index_name(self, value: str | None) -> None:
        self._orca_lookup_settings.memory_index_name = value
        self._propagate_lookup_settings()

    @property
    def lookup_column_names(self) -> list[str] | None:
        """The names of the columns to retrieve for each memory."""
        return (
            self._orca_lookup_settings.lookup_column_names or self._inherited_orca_lookup_settings.lookup_column_names
        )

    @lookup_column_names.setter
    def lookup_column_names(self, value: list[str] | None) -> None:
        self._orca_lookup_settings.lookup_column_names = value
        self._propagate_lookup_settings()

    @property
    def num_memories(self) -> int | None:
        """The number of memories to look up."""
        return self._orca_lookup_settings.num_memories or self._inherited_orca_lookup_settings.num_memories

    @num_memories.setter
    def num_memories(self, value: int | None) -> None:
        if self._orca_lookup_settings.freeze_num_memories and self._orca_lookup_settings.num_memories is not None:
            raise ValueError(
                "num_memories is frozen and cannot be changed. This is a safety feature to prevent accidental changes."
            )
        self._orca_lookup_settings.num_memories = value
        self._propagate_lookup_settings()

    @property
    def drop_exact_match(self) -> DropExactMatchOption:
        """Whether to drop exact matches from the results."""
        return (
            self._orca_lookup_settings.drop_exact_match
            or self._inherited_orca_lookup_settings.drop_exact_match
            or DropExactMatchOption.NEVER
        )

    @drop_exact_match.setter
    def drop_exact_match(self, value: DropExactMatchOption) -> None:
        self._orca_lookup_settings.drop_exact_match = value
        self._propagate_lookup_settings()

    @property
    def exact_match_threshold(self) -> float:
        """The similarity threshold for exact matches."""
        return (
            self._orca_lookup_settings.exact_match_threshold
            or self._inherited_orca_lookup_settings.exact_match_threshold
            or EXACT_MATCH_THRESHOLD
        )

    @exact_match_threshold.setter
    def exact_match_threshold(self, value: float) -> None:
        self._orca_lookup_settings.exact_match_threshold = value
        self._propagate_lookup_settings()

    @property
    def shuffle_memories(self) -> bool:
        """Whether to shuffle the looked up memories."""
        return (
            self._orca_lookup_settings.shuffle_memories
            or self._inherited_orca_lookup_settings.shuffle_memories
            or False
        )

    @shuffle_memories.setter
    def shuffle_memories(self, value: bool) -> None:
        self._orca_lookup_settings.shuffle_memories = value
        self._propagate_lookup_settings()


class LabelColumnNameMixin:
    """Mixin that lets the user set a label column for lookup instead of requiring them to set the lookup column names directly.
    It can be mixed with OrcaModel or OrcaLookupModule classes.

    This is useful when the user wants the lookup columns to be `["$embedding", label_column_name]`. The label_column_name
    property handles updates to lookup_column_names automatically.

    Note:
        Make sure to set `self.label_column_name` AFTER calling `super().__init__(...)` in derived modules/models.
    """

    def __init__(self):
        """
        Initialize the mixin

        Args:
            label_column_name: The name of the label column to use for lookup.
        """
        self._label_column_name = None

    @property
    def label_column_name(self) -> ColumnName | None:
        """The name of the label column to use for lookup."""
        if self.lookup_column_names and len(self.lookup_column_names) == 2:
            return self.lookup_column_names[1]
        return self._label_column_name

    @label_column_name.setter
    def label_column_name(self, value: ColumnName | None):
        self._label_column_name = value
        self.lookup_column_names = ["$embedding", value] if value else None
