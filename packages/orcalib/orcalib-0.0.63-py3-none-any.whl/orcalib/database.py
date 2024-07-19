from typing import Any, Literal, Optional

import requests
import torch
from pandas import DataFrame
from tqdm.auto import trange
from transformers import AutoModel, AutoTokenizer
from typing_extensions import deprecated

from orca_common import (
    EXACT_MATCH_THRESHOLD,
    CatchupStatus,
    EmbeddingModel,
    TableCreateMode,
)
from orcalib.client import ColumnSpec, OrcaClient, PagedResponse
from orcalib.exceptions import OrcaException
from orcalib.index_handle import IndexHandle
from orcalib.index_query import DefaultIndexQuery, VectorIndexQuery
from orcalib.orca_types import OrcaTypeHandle
from orcalib.table import TableHandle


class OrcaDatabase:
    name: str
    _default_instance = None

    def __init__(self, name: str):
        """
        Create a new OrcaDatabase object

        Args:
            name: name of the database
        """
        self.name = name
        OrcaClient.create_database(name)
        self.tables = OrcaClient.list_tables(name)
        self.tokenizer = None
        self.model = None

    def _load_model_and_tokenizer(self) -> tuple[AutoTokenizer, AutoModel]:
        """
        Load the default model and tokenizer

        Returns:
            tokenizer: tokenizer for the model
            model: model to use for vectorization

        NOTE: This method should not be called directly. It is used internally by the library to load the default model and tokenizer.
        """
        if self.tokenizer is None or self.model is None:
            self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/multi-qa-mpnet-base-dot-v1")
            self.model = AutoModel.from_pretrained("sentence-transformers/multi-qa-mpnet-base-dot-v1")  # .to("cuda")
        return self.tokenizer, self.model

    def __contains__(self, table_name: str) -> bool:
        """
        Check if a table exists in the database

        Args:
            table_name: name of the table
        """
        return table_name in self.tables

    def __getitem__(self, table_name: str) -> TableHandle:
        """
        Get a handle to a table by name

        Args:
            table_name: name of the table

        Returns:
            TableHandle object
        """
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} not found in database {self.name}")
        return TableHandle(self.name, table_name)

    def get_table(self, table_name: str) -> TableHandle:
        """
        Get a handle to a table by name

        Args:
            table_name: name of the table

        Returns:
            TableHandle object
        """
        return self.__getitem__(table_name)

    @classmethod
    def get_default_instance(cls) -> "OrcaDatabase":
        """
        Get the default instance of OrcaDatabase

        Returns:
            OrcaDatabase object
        """
        if cls._default_instance is None:
            cls._default_instance = cls("default")
        return cls._default_instance

    @staticmethod
    def list_databases() -> list[str]:
        """
        List all databases on the server

        Returns:
            list of database names
        """
        return OrcaClient.list_databases()

    @classmethod
    def is_server_up(cls) -> bool:
        """
        Check if the server is up and running

        Returns:
            True if server is up, False otherwise
        """
        try:
            cls.list_databases()
            return True
        except Exception:
            return False

    @classmethod
    def drop_database(cls, db: "str | OrcaDatabase", ignore_db_not_found: bool = False) -> None:
        """
        Drops a database by name or using the OrcaDatabase object

        Args:
            db: name of the database or OrcaDatabase object to drop
            ignore_db_not_found: if True, ignore error if database doesn't exist and continue with
                the operation anyway
        """
        db_name = db.name if isinstance(db, OrcaDatabase) else db
        OrcaClient.drop_database(db_name, ignore_db_not_found)

    @classmethod
    def exists(cls, db: "str | OrcaDatabase") -> bool:
        """
        Checks if a database exists by name or using the OrcaDatabase object

        Args:
            db: name of the database or OrcaDatabase object

        Returns:
            True if database exists, False otherwise
        """
        db_name = db.name if isinstance(db, OrcaDatabase) else db
        return OrcaClient.database_exists(db_name)

    @staticmethod
    def restore(target_db_name: str, backup_name: str, checksum: str | None = None) -> "OrcaDatabase":
        """Restore a backup into a target database

        Danger: Careful:
            This will overwrite the target database if it already exists.

        Args:
            target_db_name: name of database that backup will be restored into (will be created if
                it doesn't exist)
            backup_name: name of the backup to restore
            checksum: optionally the checksum for the backup

        Returns:
            restored database
        """
        OrcaClient.restore_backup(target_db_name, backup_name, checksum=checksum)
        return OrcaDatabase(target_db_name)

    def list_tables(self) -> list[str]:
        """
        List all tables in the database

        Returns:
            list of table names
        """
        return OrcaClient.list_tables(self.name)

    def backup(self) -> tuple[str, str]:
        """
        Create a backup of the database

        Returns:
            backup_name: name of the backup
            checksum: checksum for the backup
        """
        res = OrcaClient.create_backup(self.name)
        return res["backup_name"], res["checksum"]

    @staticmethod
    def download_backup(backup_file_name: str) -> requests.Response:
        """
        Downloads the backup of the database

        Args:
            backup_file_name: name of the backup file

        Returns:
            backed up file
        """
        return OrcaClient.download_backup(backup_file_name)

    @staticmethod
    def upload_backup(file_path: str) -> requests.Response:
        """
        Uploads tar file of the database

        Args:
            file_path: path to the tar file

        Returns:
            Upload response
        """
        return OrcaClient.upload_backup(file_path)

    @staticmethod
    def delete_backup(backup_file_name: str) -> requests.Response:
        """
        Delete backup file

        Args:
            backup_file_name: name of the backup file

        Returns:
            delete response
        """
        return OrcaClient.delete_backup(backup_file_name)

    @deprecated("use orcalib.orca_torch.embed instead")
    def default_vectorize(self, text: str) -> list[float]:
        tokenizer, model = self._load_model_and_tokenizer()
        encoded_input = tokenizer(text, return_tensors="pt", padding="max_length", truncation=True)  # .to("cuda")
        output = model(**encoded_input)
        return output.pooler_output.tolist()[0]

    def create_table(
        self,
        table_name: str,
        if_table_exists: TableCreateMode = TableCreateMode.ERROR_IF_TABLE_EXISTS,
        **columns: OrcaTypeHandle,
    ) -> TableHandle:
        """
        Create a table in the database

        Args:
            table_name: name of the table
            if_table_exists: what to do if the table already exists
            **columns: column names and types

        Returns:
            TableHandle object
        """
        # We will deal with the case where the table already exists in server.
        self._create_table(table_name, if_table_exists, **columns)
        return self.get_table(table_name)

    def _create_table(
        self,
        table_name: str,
        if_table_exists: TableCreateMode,
        **columns: OrcaTypeHandle,
    ) -> TableHandle:
        """Create a table in the database"""
        table_schema: list[ColumnSpec] = []
        for column_name, column_type in columns.items():
            table_schema.append(
                ColumnSpec(
                    name=column_name,
                    dtype=column_type.full_name,
                    notnull=column_type._notnull,
                    unique=column_type._unique,
                )
            )
        OrcaClient.create_table(self.name, table_name, table_schema, if_table_exists)
        self.tables.append(table_name)
        return TableHandle(self.name, table_name)

    def _create_index(
        self,
        index_name: str,
        table_name: str,
        column: str,
        index_type: str,
        ann_index_type: str = "hnswlib",
        error_if_exists: bool = True,
        _api_version: str | None = None,
        embedding_model: EmbeddingModel | None = EmbeddingModel.SENTENCE_TRANSFORMER,
    ) -> IndexHandle:
        """Create an index on a table

        Args:
            index_name: name of the index
            table_name: name of the table
            column: name of the column
            index_type: type of the index
            error_if_exists: if True, raise an error if the index already exists
            embedding_model: embedding model to use
        """
        try:
            print(f"Creating index {index_name} of type {index_type} on table {table_name} with column {column}")
            return OrcaClient.create_index(
                self.name,
                index_name,
                table_name,
                column,
                index_type,
                ann_index_type,
                _api_version=_api_version,
                embedding_model=embedding_model,
            )
        except OrcaException as e:
            if error_if_exists:
                raise e

    def get_index_status(self, index_name: str) -> CatchupStatus:
        """
        Get the status of an index

        Args:
            index_name: name of the index

        Returns:
            status of the index
        """
        return OrcaClient.get_index_status(db_name=self.name, index_name=index_name)

    def get_index(self, index_name: str) -> IndexHandle:
        """
        Get a handle to an index by name

        Args:
            index_name: name of the index

        Returns:
            the index handle
        """
        return OrcaClient.get_index(self.name, index_name)

    def create_vector_index(
        self,
        index_name: str,
        table_name: str,
        column: str,
        ann_index_type: str = "hnswlib",
        error_if_exists: bool = True,
        _api_version: str | None = None,
    ) -> IndexHandle:
        """
        Create a vector index on a table

        Args:
            index_name: name of the index
            table_name: name of the table
            column: name of the column
            error_if_exists: if True, raise an error if the index already exists

        Returns:
            The handle for the created index
        """
        return self._create_index(
            index_name, table_name, column, "vector", ann_index_type, error_if_exists, _api_version=_api_version
        )

    def create_document_index(
        self,
        index_name: str,
        table_name: str,
        column: str,
        ann_index_type: str = "hnswlib",
        error_if_exists: bool = True,
        embedding_model: EmbeddingModel | None = EmbeddingModel.SENTENCE_TRANSFORMER,
        _api_version: str | None = None,
    ) -> IndexHandle:
        """
        Create a document index on a table

        Args:
            index_name: name of the index
            table_name: name of the table
            column: name of the column
            error_if_exists: if True, raise an error if the index already exists
            embedding_model: embedding model to use

        Returns:
            The handle for the created index
        """
        return self._create_index(
            index_name,
            table_name,
            column,
            "document",
            ann_index_type,
            error_if_exists,
            embedding_model=embedding_model,
            _api_version=_api_version,
        )

    def create_text_index(
        self,
        index_name: str,
        table_name: str,
        column: str,
        ann_index_type: str = "hnswlib",
        error_if_exists: bool = True,
        embedding_model: EmbeddingModel | None = EmbeddingModel.SENTENCE_TRANSFORMER,
        _api_version: str | None = None,
    ) -> IndexHandle:
        """
        Create a text index on a table

        Args:
            index_name: name of the index
            table_name: name of the table
            column: name of the column
            error_if_exists: if True, raise an error if the index already exists
            embedding_model: embedding model to use

        Returns:
            The handle for the created index
        """
        return self._create_index(
            index_name,
            table_name,
            column,
            "text",
            ann_index_type,
            error_if_exists,
            embedding_model=embedding_model,
            _api_version=_api_version,
        )

    def create_btree_index(
        self,
        index_name: str,
        table_name: str,
        column: str,
        ann_index_type: str = "hnswlib",
        error_if_exists: bool = True,
        _api_version: str | None = None,
    ) -> IndexHandle:
        """
        Create a btree index on a table

        Args:
            index_name: name of the index
            table_name: name of the table
            column: name of the column
            error_if_exists: if True, raise an error if the index already exists

        Returns:
            The handle for the created index
        """
        return self._create_index(
            index_name, table_name, column, "btree", ann_index_type, error_if_exists, _api_version=_api_version
        )

    def drop_index(self, index_name: str, error_if_not_exists: bool = True) -> None:
        """
        Drop an index from the database

        Args:
            index_name: name of the index
            error_if_not_exists: if True, raise an error if the index doesn't exist
        """
        try:
            OrcaClient.drop_index(self.name, index_name)
        except OrcaException as e:
            if error_if_not_exists:
                raise e

    def drop_table(self, table_name: str, error_if_not_exists: bool = True) -> None:
        """Drop a table from the database

        Args:
            table_name: name of the table
            error_if_not_exists: if True, raise an error if the table doesn't exist
        """
        OrcaClient.drop_table(self.name, table_name, error_if_not_exists)
        if table_name in self.tables:
            self.tables.remove(table_name)

    def search_memory(
        self,
        index_name: str,
        query: list[float] | str,
        limit: int,
        columns: list[str],
    ) -> list[tuple[list[float], Any]]:
        """
        Search a given index for memories related to a query

        This is a convenience method that wraps the [`index.scan`][orcalib.index_handle.IndexHandle.scan]
        method to perform a quick search on a given index. For more advanced queries, use the
        [`index.scan`][orcalib.index_handle.IndexHandle.scan] or [`index.vector_scan`][orcalib.index_handle.IndexHandle.vector_scan]
        methods directly.

        Args:
            index_name: The name of the index to search
            query: Query value for the index, can either be a vector represented as a list of
                floats, or a value that matches the column type of the index, for example a string
            index, this can must match the column type this index is defined
                on, for example this would be a string if this is a text index
            limit: maximum number of results to return
            columns: list of columns to return in the result

        Returns:
            list of dictionaries containing a mapping of column names to values

        Examples:
            >>> db.search_memory(
            ...     "text_index",
            ...     query="Are Orcas really whales?",
            ...     limit=1,
            ...     columns=["id", "text"]
            ... )
            [
                {
                    'id': 1,
                    'text': "Despite being commonly known as killer whales, orcas are actually the largest member of the dolphin family."
                }
            ]
        """
        res = OrcaClient.scan_index(
            self,
            index_name,
            query,
            limit,
            columns,
        )
        return res

    def scan_index(
        self,
        index_name: str,
        query: Any,
        drop_exact_match: bool = False,
        exact_match_threshold: float = EXACT_MATCH_THRESHOLD,
    ) -> DefaultIndexQuery:
        """
        Entry point for a search query on the index

        Args:
            index_name: name of the index

        Note:
            See [IndexHandle.scan](orcalib.index_handle.IndexHandle.scan) for details.
        """
        return DefaultIndexQuery(
            db_name=self.name,
            primary_table=self._get_index_table(index_name),
            index=index_name,
            index_query=query,
            drop_exact_match=drop_exact_match,
            exact_match_threshold=exact_match_threshold,
        )

    def vector_scan_index(
        self,
        index_name: str,
        query: Any,
        drop_exact_match: bool = False,
        exact_match_threshold: float = EXACT_MATCH_THRESHOLD,
    ) -> VectorIndexQuery:
        """
        Entry point for a vector search query on the index that returns a results batch

        Args:
            index_name: name of the index

        Note:
            See [IndexHandle.vector_scan](orcalib.index_handle.IndexHandle.vector_scan) for details.
        """
        return VectorIndexQuery(
            db_name=self.name,
            primary_table=self._get_index_table(index_name),
            index=index_name,
            index_query=query,
            drop_exact_match=drop_exact_match,
            exact_match_threshold=exact_match_threshold,
        )

    def full_vector_memory_join(
        self,
        *,
        index_name: str,
        memory_index_name: str,
        num_memories: int,
        query_columns: list[str],
        page_index: int,
        page_size: int,
        drop_exact_match: bool = False,
        exact_match_threshold: float = EXACT_MATCH_THRESHOLD,
        shuffle_memories: bool = False,
    ) -> PagedResponse:
        """
        Join a vector index with a memory index

        Args:
            index_name: name of the index
            memory_index_name: name of the memory index
            num_memories: number of memories to join
            query_columns: list of columns to return
            page_index: page index
            page_size: page size

        Returns:
            dictionary containing the joined vectors and extra columns
        """
        return OrcaClient.full_vector_memory_join(
            db_name=self.name,
            index_name=index_name,
            memory_index_name=memory_index_name,
            num_memories=num_memories,
            query_columns=query_columns,
            page_index=page_index,
            page_size=page_size,
            drop_exact_match=drop_exact_match,
            exact_match_threshold=exact_match_threshold,
            shuffle_memories=shuffle_memories,
        )

    # TODO: move this directly into the OrcaMemoryDataset
    def _get_index_values(self, index_name: str) -> dict[int, list[float]]:
        """
        Get all values for an index

        Args:
            index_name: name of the index

        Returns:
            dictionary containing the index values
        """
        res = OrcaClient.get_index_values(self.name, index_name)
        return {int(k): v for k, v in res.items()}

    # TODO: move this directly into the OrcaMemoryDataset
    def _get_index_values_paginated(
        self,
        index_name: str,
        page_size: int = 1000,
    ) -> dict[int, list[float]]:
        """
        Get all values for an index, paginated

        Args:
            index_name: name of the index
            page_size: page size (default: 1000)

        Returns:
            dictionary containing the index values
        """
        page_index = 0

        result = {}

        res = OrcaClient.get_index_values_paginated(self.name, index_name, page_index=page_index, page_size=page_size)

        num_pages = res["num_pages"]

        for v in res["items"]:
            result[int(v[0])] = v[1]

        if num_pages > 1:
            print(f"Fetching vectors for index {index_name} ({num_pages} pages)")

            for page_index in trange(1, num_pages):
                res = OrcaClient.get_index_values_paginated(
                    self.name, index_name, page_index=page_index, page_size=page_size
                )

                for v in res["items"]:
                    result[int(v[0])] = v[1]

        print(f"Finished fetching vectors for index {index_name} ({num_pages} pages)")

        return result

    def _get_index_table(self, index_name: str) -> TableHandle:
        """Get the table associated with an index"""
        return TableHandle(self.name, OrcaClient.get_index_table(self.name, index_name))

    def query(self, query: str, params: list[None | int | float | bytes | str] = []) -> DataFrame:
        """
        Send a raw SQL read query to the database

        This cannot be used for inserting, updating, or deleting data.

        Args:
            query: SQL query to run
            params: optional values to pass to a parametrized query

        Returns:
            pandas DataFrame containing the results
        """
        df = DataFrame(OrcaClient.run_sql(self.name, query, params))
        return df

    def __str__(self) -> str:
        return f"OrcaDatabase({self.name}) - Tables: {', '.join(self.tables)}"

    def __repr__(self) -> str:
        return self.__str__()


def _with_default_database_method(method: Any) -> Any:
    """Decorator to add the default database as the first argument to a method."""

    def wrapper(*args, **kwargs):
        default_database = OrcaDatabase.get_default_instance()
        return method(default_database, *args, **kwargs)

    return wrapper
