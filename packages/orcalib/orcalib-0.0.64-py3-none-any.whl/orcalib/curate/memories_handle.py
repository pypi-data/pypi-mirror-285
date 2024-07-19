import json
from typing import Any

from peewee import Alias, Column, Table

from orcalib.client import OrcaClient

from ._base_select_query import BaseSelectQuery, decode_tensor
from ._curate_table_schema import memory_lookups_table, runs_table


class MemoriesHandle:
    """
    A handle to query memories associated with an index used in a model.
    """

    # TODO: Document column attributes

    # Columns:
    # - table_row_id (int): The __id of the table row that was looked up.
    # - table_name (int): The name of the table from which the row that was looked up.
    # - memory_index_name (str): The name of the memory index used for the lookup.
    # - $embedding (Tensor): The embedding of the index column value.
    # - <index_column> (Any): The value of the index column in the table row.
    # - ...<lookup_columns> (Any): The values of the additional columns on the reference row.
    # - ...<aggregate_data> (Any): Aggregated data selected.

    def __init__(
        self,
        database_name: str,
        index_name: str | None = None,
        table_name: str | None = None,
        model_id: str | None = None,
        model_version: str | None = None,
    ):
        """
        Initializes the memories table handle.

        Args:
            index_name: The index that the memories are associated with.
            table_name: The table that the memories are stored in.
            database_name: The name of the database the index is defined on.
            model_id: The model id to filter the model run memory lookups by.
            model_version: The model version to filter the model run memory lookups by.
        """
        self._database_name = database_name
        self._model_id = model_id
        self._model_version = model_version
        # Columns
        self.run_id = memory_lookups_table.run_id
        self.layer_name = memory_lookups_table.layer_name.alias("memory_layer_name")
        self.memory_index_name = memory_lookups_table.index_name.alias("memory_index_name")
        self.table_name = memory_lookups_table.table_name
        self.table_row_id = memory_lookups_table.reference_row_id.alias("table_row_id")
        self._table_index_column = memory_lookups_table.index_column.alias("_index_column_name")
        self._other_table_columns = memory_lookups_table.extra_columns.alias("_lookup_column_names")
        self._table_row_snapshot = memory_lookups_table.reference_row_data.alias("_table_row_snapshot")

        if index_name is None and table_name is None:
            raise ValueError("Either index_name or table_name must be specified")
        # Get table name from index_name
        if index_name:
            self._table_name = OrcaClient.get_index_table(database_name, index_name)
        else:
            self._table_name = table_name

        # Get table columns and add column definitions for each
        if self._table_name is None:
            raise ValueError(f"Table not found for index_name: {index_name}")
        columns = OrcaClient.table_info(self._database_name, self._table_name)
        self._reference_table_column_names = [c.name for c in columns]
        self._reference_table_handle = Table(self._table_name)
        for col in self._reference_table_column_names:
            self.__setattr__(col, Column(self._reference_table_handle, col))

    def select(self, *args: str | Column | Alias) -> "MemoriesSelectQuery":
        """
        Thin peewee wrapper method for selecting the columns to return.

        Args:
            args: The columns to select

        Returns:
            The query object for chaining

        Examples:
            >>> my_memories.select("label", "text")
        """
        return MemoriesSelectQuery(self, *args)


class MemoriesSelectQuery(BaseSelectQuery):
    def __init__(self, memories_table: MemoriesHandle, *args: str | Column | Alias):
        self._memories_table = memories_table
        self._embedding = False
        # initialize the query
        self._query = (
            memory_lookups_table.select()
            .join(
                self._memories_table._reference_table_handle,
                on=(memory_lookups_table.reference_row_id == self._memories_table._reference_table_handle.c["__id"]),
            )
            .group_by(self._memories_table.table_row_id)
            .order_by(self._memories_table.run_id, "DESC")
        )
        self._selects = [self._memories_table._table_row_snapshot]
        if not args:
            self._selects = [
                self._memories_table.table_row_id,
                self._memories_table._table_row_snapshot,
            ]
            for col in self._memories_table._reference_table_column_names:
                column = getattr(self._memories_table, col)
                self._selects.append(column)
        else:
            for arg in args:
                if arg != "$embedding":
                    if isinstance(arg, str):
                        col = getattr(self._memories_table, arg)
                        if col is None or not (isinstance(col, Column) or isinstance(col, Alias)):
                            raise ValueError(f"Invalid column: {arg}")
                        self._selects.append(col)
                    else:
                        self._selects.append(arg)
                else:
                    self._embedding = True

    def aggregate_runs(self, *args):
        """
        Thin peewee wrapper method for aggregating the results by runs.

        Args:
            args: The columns to aggregate by

        Returns:
            The query object for chaining

        Examples:
            >>> my_query.aggregate_runs(
            ...     fn.count(runs_handle.id).alias("num_runs")
            ... )
        """
        assert self._selects is not None
        assert self._query is not None
        if args:
            self._selects.extend(args)
        self._query = self._query.join(runs_table, on=(memory_lookups_table.run_id == runs_table.run_id))
        if self._memories_table._model_id:
            self._query = self._query.where(runs_table.model_id == self._memories_table._model_id)
        if self._memories_table._model_version:
            self._query = self._query.where(runs_table.model_version == self._memories_table._model_version)
        return self

    def fetch(self, limit: int | None = None, offset: int | None = None) -> list[dict[str, Any]]:
        """
        Extract the SQL query from peewee and run it through Orca Client to get results.

        Args:
            limit: The maximum number of rows to return, if `None` returns all rows
            offset: The number of rows to skip, if `None` starts from the beginning

        Returns:
            A list of dictionaries mapping column names to values.

        Examples:
            >>> my_query.fetch(1)
            [{'label': 'my_label', 'text': 'my_text', 'avg_feedback': 0.5, 'num_runs': 1}]
        """
        assert self._memories_table._database_name is not None
        if limit is not None:
            self.limit(limit)
        if offset is not None:
            self.offset(offset)
        statement, params = self._query.select(*self._selects).sql()
        rows = OrcaClient.run_sql(
            self._memories_table._database_name,
            statement,
            params,
        )
        # decode the results
        if len(rows) == 0:
            return rows
        for row in rows:
            table_row_snapshot = json.loads(row["_table_row_snapshot"])
            if self._embedding:
                # decode the index column embedding
                row["$embedding"] = decode_tensor(table_row_snapshot["$embedding"])
            del row["_table_row_snapshot"]

        return rows
