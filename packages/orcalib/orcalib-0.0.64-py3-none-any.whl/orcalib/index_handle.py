from typing import Any, Literal, overload

from torch import Tensor

from orca_common import EXACT_MATCH_THRESHOLD, CatchupStatus, ColumnName, EmbeddingModel
from orcalib.orca_types import NumericTypeHandle, OrcaTypeHandle


class IndexHandle:
    """A handle to an index in an Orca database."""

    def __init__(
        self,
        name: str,
        db_name: str,
        table_name: str,
        column_name: ColumnName,
        column_type: OrcaTypeHandle,
        embedding_type: OrcaTypeHandle,
        index_type: str,
        artifact_columns: dict[ColumnName, str | OrcaTypeHandle],
        embedding_model: EmbeddingModel | None = None,
    ):
        """
        Initialize an index handle

        Usually this is not called directly but through the [`db.get_index`][orcalib.OrcaDatabase.get_index]
        or [`db.create_vector_index`][orcalib.OrcaDatabase.create_document_index] etc. methods on a database handle.

        Args:
            name: Name of this index
            db_name: Database that this index belongs to
            table_name: Table that this index belongs to
            column_name: Name of the column that this index is built on
            column_type: Type of the column that this index is built on
            embedding_type: Type of the vector embedding used by this index (if any)
            index_type: Type of this index
            artifact_columns: Artifact columns that are available from the index
        """
        self.name = name
        self.db_name = db_name
        self.table_name = table_name
        self.column_name = column_name
        self.column_type = column_type
        self.embedding_type = embedding_type
        self.index_type = index_type
        self.artifact_columns: dict[ColumnName, OrcaTypeHandle] = {
            column: (OrcaTypeHandle.from_string(column_type) if isinstance(column_type, str) else column_type)
            for column, column_type in artifact_columns.items()
        }
        self.embedding_model = embedding_model

    @property
    def embedding_dim(self) -> int:
        """
        Get the embedding dimension of this index (if any).

        Returns:
            Embedding dimension if this index has an embedding, `None` otherwise

        Raises:
            NotImplementedError: If the embedding type is not a numeric type

        Examples:
            >>> index.embedding_dim
            768
        """
        if self.embedding_type is None or not isinstance(self.embedding_type, NumericTypeHandle):
            raise NotImplementedError("This index type doesn't use embeddings, so it doesn't support embedding_dim")
        return self.embedding_type.length

    def scan(
        self,
        query: Any,
        drop_exact_match: bool = False,
        exact_match_threshold: float = EXACT_MATCH_THRESHOLD,
    ) -> "DefaultIndexQuery":  # noqa: F821
        """
        Entry point for a search query on the index

        Args:
            query: Query value for the index, must match the column type this index is defined
                on, for example this would be a string if this is a text index
            drop_exact_match: If True, drop exact matches from the results
            exact_match_threshold: Threshold for exact match, if the similarity score is above this

        Returns:
            chainable query builder object, see example

        Examples:
            >>> index.scan("Are Orcas really whales?").select("id", "text").fetch(1)
            [
                {
                    'id': 1,
                    'text': "Despite being commonly known as killer whales, orcas are actually the largest member of the dolphin family."
                }
            ]
        """
        from orcalib.database import OrcaDatabase
        from orcalib.index_query import DefaultIndexQuery

        return DefaultIndexQuery(
            db_name=self.db_name,
            primary_table=OrcaDatabase(self.db_name).get_table(self.table_name),
            index=self.name,
            index_query=query,
            drop_exact_match=drop_exact_match,
            exact_match_threshold=exact_match_threshold,
        )

    def vector_scan(
        self,
        query: Any,
        drop_exact_match: bool = False,
        exact_match_threshold: float = EXACT_MATCH_THRESHOLD,
    ) -> "VectorIndexQuery":  # noqa: F821
        """
        Entry point for a vector search query on the index that returns a results batch

        Args:
            query: A batch of queries to scan the index with, can either be a list of vectors
                represented by a list of floats each, or a list of for example strings if this is
                a text index. Can also be a single value, which will be treated as a list of one.
            drop_exact_match: If True, drop exact matches from the results
            exact_match_threshold: Threshold for exact match, if the similarity score is above this

        Returns:
            chainable query handle object, see example

        Examples:
            >>> res = (
            ...     index.vector_scan(torch.rand(2, index.embedding_dim).tolist())
            ...     .select("$embedding", "label")
            ...     .fetch(10)
            ... )
            >>> res.to_tensor("$embedding").shape, res.to_tensor("$embedding").dtype
            torch.Size([2, 10, 768]), torch.float64
            >>> res.to_tensor("label").shape, res.to_tensor("label").dtype
            torch.Size([2, 10]), torch.int64

            >>> res = index.vector_scan("I love Orcas").select("text", "label").fetch(2)
            >>> res.to_records_list()
            [
                [
                    {
                        'text': "Orcas use sophisticated hunting techniques.",
                        'label': 1
                    },
                    {
                        'text': "Orcas can swim at speeds up to 34 miles per hour.",
                        'label': 1
                    }
                ]
            ]

        """
        from orcalib.database import OrcaDatabase
        from orcalib.index_query import VectorIndexQuery

        return VectorIndexQuery(
            db_name=self.db_name,
            primary_table=OrcaDatabase(self.db_name).get_table(self.table_name),
            index=self.name,
            index_query=query,
            drop_exact_match=drop_exact_match,
            exact_match_threshold=exact_match_threshold,
        )

    def get_status(self) -> CatchupStatus:
        """
        Get the status of this index.

        Returns:
            The processing status of the index

        Examples:
            >>> index.get_status()
            'COMPLETED'
        """
        # TODO: refactor to remove Index Handle dependency from OrcaClient
        from orcalib.client import OrcaClient

        return OrcaClient.get_index_status(self.db_name, self.name)

    @overload
    def embed(self, text: str | list[str], result_format: Literal["pt"] = "pt") -> Tensor:
        ...

    @overload
    def embed(self, text: str | list[str], result_format: Literal["list"]) -> list[list[float]]:
        ...

    def embed(self, text: str | list[str], result_format: Literal["pt", "list"] = "pt") -> list[list[float]] | Tensor:
        """
        Encode text into vectors using the index's embedding model.

        Args:
            text: Text to encode. Can be a single string or a list of strings.
            result_format: Format of the result. Can be "pt" for a PyTorch tensor or "list" for a list of lists.

        Returns:
            The embeddings of the text in the format specified by `result_format`.

        Examples:
            >>> index.embed("I love Orcas", result_format="list")
            [[0.1, 0.2, 0.3, ...]]
            >>> x = index.embed(["I love Orcas", "Orcas are cool"], result_format="pt")
            >>> x.shape, x.dtype
            (torch.Size([2, 768]), torch.float32)
        """
        from orcalib.client import OrcaClient

        if isinstance(text, str):
            text = [text]

        return OrcaClient.index_embed_text(self.db_name, self.name, text, result_format=result_format)

    def __str__(self) -> str:
        # Do not add docstring here since we don't want this in the docs
        return f"{self.index_type} index: {self.name} on {self.db_name}.{self.table_name}.{self.column_name} ({self.column_type})"

    def __repr__(self) -> str:
        # Do not add docstring here since we don't want this in the docs
        return str(self)
