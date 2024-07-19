import itertools
from collections import defaultdict
from enum import Enum
from typing import Any, Dict

import torch
from datasets import Dataset

from orca_common.constants import EXACT_MATCH_THRESHOLD
from orcalib import orca_types
from orcalib.batched_scan_result import BatchedScanResult, BatchedScanResultBuilder
from orcalib.database import OrcaDatabase
from orcalib.index_handle import IndexHandle
from orcalib.orca_torch import OrcaLookupModule
from orcalib.orca_torch_mixins import LookupSettingsSummary
from orcalib.orca_types import NumericTypeHandle, OrcaTypeHandle, TextTypeHandle


class OrcaLookupCacheBuilder:
    """This class allows you to precache your lookup results into a HuggingFace Dataset for faster training.
    It also allows you to inject the pre-cached lookup results into your model during training and inference.

    In the future, we may extend this class to support additional dataset types and frameworks.

    Example:
        First, configure the lookup cache builder with the necessary information about your lookups.
        ```python
        lookup_cache_builder = OrcaLookupCacheBuilder(
            db=OrcaDatabase(DB_NAME),
            index_name=INDEX_NAME,
            num_memories=10,
            embedding_col_name="embeddings",
            memory_column_aliases={"$score": "memory_scores", "label": "memory_labels"},
        )

        train_data = load_dataset(DATASET_NAME)
        ```

        Next, add the lookup results to the HuggingFace Dataset.
        ```lookup_cache_builder.add_lookups_to_hf_dataset(train_data, "text")```

        Finally, inject the lookup results into your model during training and inference.
        ```python
        class MyModel(OrcaLookupModule):
            def __init__(self, cache_builder: OrcaLookupCacheBuilder):
                ...
                # Orca modules that use lookup layers don't need to know about the lookup cache builder.
                self.my_orca_layer = OrcaLookupLayer(...)
                self.cache_builder = cache_builder

            def forward(self, x, memory_scores, memory_labels):
                # Finally, inject the lookup results into the model. Downstream lookup layers will use these results.
                self.cache_builder.inject_lookup_results(self, memory_scores=memory_scores, memory_labels=memory_labels)
                ...
        ```

    """

    # This is the default type for the $score column in the lookup results.
    DEFAULT_SCORE_TYPE = orca_types.Float32T

    def __init__(
        self,
        db: OrcaDatabase,
        index_name: str,
        num_memories: int,
        embedding_col_name: str | None,
        memory_column_aliases: Dict[str, str],
        drop_exact_match: bool = False,
        exact_match_threshold: float = EXACT_MATCH_THRESHOLD,
        batch_size: int = 1000,
    ):
        """Initializes the OrcaLookupCacheBuilder with the necessary information to perform lookups and
        inject the results into a model.

        Args:
            db (OrcaDatabase): The `OrcaDatabase` instance that contains the memory table we'll use for lookups.
            index_name (str): The name of the memory index we'll use for lookups.
            num_memories (int): The number of memories to fetch for each element in the data set.
            embedding_col_name (str | None): The name of the feature that will be created to store the embedding of the query column.
                If None, the embedding will not be stored (for when embeddings are alredy processed).
            memory_column_aliases (Dict[str, str]): Maps the lookup column names to the feature name that
                will be added to the `Dataset`. For example, `{"$score": "memory_scores", "label": "memory_labels"}`
                will add a `memory_scores` column and a `memory_labels` column to the `Dataset` that contains
                the scores and labels of the memories, respectively. It's a good idea to align the aliases
                to match the inputs to your model's `forward()` method, e.g., `forward(x, memory_scores, memory_labels)`.
            drop_exact_match (bool): Whether to drop the highest match that's above the exact_match_threshold.
            exact_match_threshold (float): The similarity threshold for considering a memory an exact match.
            batch_size (int): The batch size to use for the vector scan. Defaults to 1000.
        """
        self.db = db
        self.index_name = index_name
        self.index = db.get_index(index_name)  # An IndexHandle for the memory index.
        self.column_type = self.index.column_type  # The type of the column in the memory index.
        self.table = db._get_index_table(index_name)  # A TableHandle for the memory table.
        # A mapping of the memory table's column names to their types.
        self.column_name_to_type = self.table.get_column_type_dict()
        self.num_memories = num_memories
        self.embedding_col_name = embedding_col_name
        self.embedding_col_type: OrcaTypeHandle = (
            self.index.embedding_type
        )  # The type of the embedding column, e.g., Float32T.
        self.memory_column_aliases = memory_column_aliases
        # Invert the memory_column_aliases so we can map the results back to the original column names
        self.alias_to_original_column = {v: k for k, v in memory_column_aliases.items()}
        self.drop_exact_match = drop_exact_match
        self.exact_match_threshold = exact_match_threshold
        self.batch_size = batch_size

    @staticmethod
    def _get_settings_summary(module: OrcaLookupModule) -> LookupSettingsSummary:
        """Gets the lookup settings summary for a model. This function also checks that the settings are consistent and complete.
        **This is an internal function that is not meant to be called from user code.** It could be removed or changed in the future
        without notice.

        Args:
            module (OrcaLookupModule): The summary will be made for the module and its children's lookup settings.

        Raises:
            ValueError: If the settings are inconsistent or incomplete.
        """
        summary_dict = module.get_lookup_setting_summary()

        if len(summary_dict) == 0:
            raise ValueError("The provided model does not have any lookup settings.")
        if len(summary_dict) > 1:
            raise ValueError(
                "The provided model is using multiple databases and/or indexes. You will need a separate cache builder"
                f" (and injection) for each model subtree using a different database–index pair: {list(summary_dict.keys())} "
            )

        summary = next(iter(summary_dict.values()))
        if summary.num_memories_range is None:
            raise ValueError(
                "None of your settings have a value for num_memories. Please set num_memories in your model."
            )
        if len(summary.lookup_column_names) == 0:
            raise ValueError(
                "None of your settings have a value for lookup_column_names. Please set lookup_column_names in your model."
            )
        if len(summary.drop_exact_match) > 1:
            raise ValueError(
                f"The provided model has inconsistent settings for drop_exact_match: {summary.drop_exact_match}. "
                "To inject lookup results, set drop_exact_match consistently in your model or perform the injection "
                "at multiple points in your model."
            )
        if len(summary.exact_match_thresholds) > 1:
            raise ValueError(
                f"The provided model has inconsistent settings for exact_match_threshold: {summary.exact_match_thresholds}. "
                "To inject lookup results, set exact_match_threshold consistently in your model or perform the injection "
                "at multiple points in your model."
            )

        return summary

    @classmethod
    def from_model(
        cls,
        model: OrcaLookupModule,
        embedding_col_name: str,
        memory_column_aliases: Dict[str, str] | None = None,
        memory_feature_prefix: str = "memory_",
    ) -> "OrcaLookupCacheBuilder":
        """This is a convenient way to create an [`OrcaLookupCacheBuilder`][orcalib.OrcaLookupCacheBuilder] that is configured with the same
        lookup settings as a model or module. It will create memory column aliases for each lookup column name in the model's settings by
        prepending the `memory_feature_prefix` to the column name. For example, if the model has a lookup column named `label`, the memory
        column alias will be `memory_label`, because `memory_feature_prefix` defaults to `"memory_"`.

        Args:
            model (OrcaLookupModule): The model whose settings will be used to create the `OrcaLookupCacheBuilder`.
            embedding_col_name (str): The name of the feature that will be created to store the embedding of the query column.
            memory_column_aliases (Dict[str, str], optional): A mapping of the lookup column names to the feature name that
                will be added to the `Dataset`. This can help when there are conflicts between the lookup column names and special
                columns. For example, if you're looking up both "score" and "$score", you can provide an alias for "$score", which
                would both map to "memory_score". This will help avoid conflicts. Defaults to `None`.
            memory_feature_prefix (str): The prefix to prepend to create the names of the features that will be added to the `Dataset`
                to hold the lookup results. Defaults to `"memory_"`. For example, if the model has a lookup column named `label`, the memory
                column alias will be `memory_label`. For special columns, e.g., `$score`, the $ will be removed: `memory_score`.

        Returns:
            An `OrcaLookupCacheBuilder` instance that is configured with the same settings as the model.
        """

        summary = OrcaLookupCacheBuilder._get_settings_summary(model)

        alias_to_columns = defaultdict(list)
        memory_aliases = dict()
        for col in summary.lookup_column_names:
            col_key = col
            col_alias = f"{memory_feature_prefix}{col.replace('$', '')}"
            if memory_column_aliases is not None:
                col_alias = memory_column_aliases.get(col, col_alias)
            alias_to_columns[col_alias].append(col_key)
            memory_aliases[col_key] = col_alias

        # Get a flattned list of the ambiguous columns
        ambiguous_columns = list(itertools.chain(v for k, v in alias_to_columns.items() if len(v) > 1))

        if len(ambiguous_columns) > 0:
            raise ValueError(
                "The model is looking up special columns that will conflict with the names of other columns "
                f"selected for lookup. These special columns are: {ambiguous_columns}. "
                "Please provide aliases using memory_column_aliases to avoid conflicts."
            )

        return OrcaLookupCacheBuilder(
            db=OrcaDatabase(summary.lookup_database_name),
            index_name=summary.memory_index_name,
            num_memories=summary.num_memories_range[1],  # Use the upper bound of the range
            embedding_col_name=embedding_col_name,
            memory_column_aliases=memory_aliases,
            drop_exact_match=None if len(summary.drop_exact_match) == 0 else summary.drop_exact_match[0],
            exact_match_threshold=None
            if len(summary.exact_match_thresholds) == 0
            else summary.exact_match_thresholds[0],
        )

    def _column_name_to_type(self, col_name: str) -> OrcaTypeHandle:
        """This converts a column, artifact, or alias string to the correct `OrcaTypeHandle`.

        Args:
            col_name (str): The column name, artifact name, or alias name.

        Returns:
            The `OrcaTypeHandle` for provided column, alias, or index artifact name.
        """
        if col_name == self.embedding_col_name:
            return self.embedding_col_type

        # If the column name is an alias, convert it to the original column/artifact name
        col_name = self.alias_to_original_column.get(col_name, col_name)

        if col_name == "$score":
            return self.DEFAULT_SCORE_TYPE
        elif col_name.startswith("$"):
            return self.index.artifact_columns[col_name[1:]]
        else:
            return self.column_name_to_type[col_name]

    def inject_lookup_results(self, model: OrcaLookupModule, **features: dict[str, list[list[Any]] | torch.Tensor]):
        """Sets (or clears) the lookup result override for an `OrcaLookupModule`, e.g., `OrcaLookupLayer`, `OrcaModel`.
        All downstream lookup layers will use these results instead of performing a lookup by contacting the database. When
        the feature values are `None`, the lookup result override will be cleared instead.

        Args:
            model (OrcaLookupModule): The `OrcaLookupModule` to inject the lookup results into.
            features (Dict[str, list[list[Any]] | torch.Tensor]): A mapping of the memory column aliases to their values. These
                values will be converted to the correct type to be used as the lookup results. **Important**: The feature values
                should all be `None` or all be non-`None`. If the feature values are `None`, the lookup result override will be
                cleared.

        Example:
            ```python
            class MyModel(OrcaLookupModule):
                ...

                def forward(self, x, memory_scores, memory_labels):
                    self.cache_builder.inject_lookup_results(self, memory_scores=memory_scores, memory_labels=memory_labels)
                    ...
            ```
        """

        empty_feature_count = sum(
            1 for feature_alias in self.memory_column_aliases.values() if feature_alias not in features
        )

        if empty_feature_count == len(features):
            model.lookup_result_override = None
        elif empty_feature_count == 0:
            model.lookup_result_override = self.get_lookup_result(**features)
        else:
            raise ValueError(f"All features should be None or all features should be non-None: {features}")

    def get_lookup_result(self, **features: dict[str, list[list[Any]] | torch.Tensor]) -> BatchedScanResult:
        """Returns a `BatchedScanResult` that contains lookup results that contain the provided features.

        Args:
            features (Dict[str, list[list[Any]] | torch.Tensor]): A mapping of the memory column aliases to their values. These
                values will be converted based on the column/artifact type to be used as the lookup results.

        Returns:
            The lookup results that contain the provided features for each memory.

        """

        if any(feature_value is None for feature_value in features.values()):
            raise ValueError(f"Some provided features are None: {[k for k, v in features.items() if v is None]}")

        unknown_features = [k for k in features.keys() if k not in self.alias_to_original_column]
        if unknown_features:
            raise ValueError(f"Some provided features are not in the memory_column_aliases: {unknown_features}")

        builder = BatchedScanResultBuilder()
        for feature_name, feature_value in features.items():
            feature_type = self._column_name_to_type(feature_name)
            original_feature_name = self.alias_to_original_column.get(feature_name, feature_name)
            builder.add_feature(original_feature_name, feature_type, feature_value)
        return builder.build()

    def add_lookups_to_hf_dataset(
        self,
        ds: Dataset,
        query_column_name: str,
        map_cache_file_name: str | None = None,
    ) -> Dataset:
        """Adds the lookup results as columns (i.e., features) to a HuggingFace Dataset. This function will perform a vector scan on the
        memory index to fetch the lookup results for each example in the dataset. The feature names for the memories will be the same as the
        `memory_column_aliases` provided in the constructor. The embedding of the query column will be stored in the `embedding_col_name` provided

        Args:
            ds (Dataset): The HuggingFace dataset to add the lookup results to.
            query_column_name (str): The name of the column that contains the query text to lookup in the memory index.
            column_type (DataSetContentType): The type of data stored in the dataset.  This can either be text or already computed embeddings. Defaults to `DataSetContentType.TEXT`.
            map_cache_file_name (str): The name of the cache file to use for the mapping of the dataset file. Defaults to None.

        Returns:
            The HuggingFace dataset with the lookup results added as features.

        Example:
            First, configure the lookup cache builder with the necessary information about your lookups.
            ```python
            lookup_cache_builder = OrcaLookupCacheBuilder(
                db=OrcaDatabase(DB_NAME),
                index_name=INDEX_NAME,
                num_memories=10,
                embedding_col_name="embeddings",
                memory_column_aliases={"$score": "memory_scores", "label": "memory_labels"},
            )
            ```

            Now, load the HuggingFace dataset and add the lookup results to it.
            ```python
            train_data = load_dataset(DATASET_NAME) # Load the HuggingFace dataset
            lookup_cache_builder.add_lookups_to_hf_dataset(train_data, "text")
            ```
        """

        index: IndexHandle = self.db.get_index(self.index_name)

        memory_col_names = list(self.memory_column_aliases.keys())

        def add_scan_results(examples):
            if isinstance(self.column_type, TextTypeHandle):
                embeddings = index.embed(examples[query_column_name], result_format="list")
            elif isinstance(self.column_type, NumericTypeHandle):  # Assume it's a tensor
                embeddings = examples[query_column_name]
            else:
                raise ValueError(f"Unknown column type: {type(self.column_type)}")
            if self.embedding_col_name:
                examples[self.embedding_col_name] = embeddings

            results: BatchedScanResult = (
                self.db.vector_scan_index(
                    self.index_name,
                    embeddings,
                    drop_exact_match=self.drop_exact_match,
                    exact_match_threshold=self.exact_match_threshold,
                )
                .select(*memory_col_names)
                .fetch(self.num_memories)
            )

            # Now we have the results, so we need to map the neighbor results to the examples
            for artifact_col, alias_col in self.memory_column_aliases.items():
                col_type = self._column_name_to_type(artifact_col)

                if isinstance(col_type, NumericTypeHandle):
                    examples[alias_col] = results.to_tensor(artifact_col, col_type.torch_dtype)
                else:
                    examples[alias_col] = results[:, :, artifact_col].to_list()

            return examples

        return ds.map(
            add_scan_results, batched=True, batch_size=self.batch_size, num_proc=1, cache_file_name=map_cache_file_name
        )
