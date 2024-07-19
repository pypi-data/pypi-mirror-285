import json
from datetime import datetime
from typing import Any

from peewee import Alias, Column

from orcalib.client import OrcaClient

from ._base_select_query import BaseSelectQuery, decode_tensor, decode_uuid
from ._curate_table_schema import memory_lookups_table, runs_table


class memory_lookup:
    score = memory_lookups_table.memory_score.alias("$score")


class RunsHandle:
    """
    A handle to query runs of a model.
    """

    # TODO: Document column attributes

    # Columns:
    # - id (int): The run id.
    # - timestamp (datetime): The timestamp of the run.
    # - model_version (str): The model version.
    # - tags (set[str]): The tags of the run.
    # - metadata (dict[str, Any]): The metadata of the run.
    # - batch_id (UUID): The batch id of the run.
    # - seq_id (UUID | None): The sequence id of the run.
    # - inputs (Any | None): The inputs of the run.
    # - outputs (Any | None): The outputs of the run.
    # - ...<feedback_name>_feedback (float): The feedback values that were recorded for the run.

    def __init__(self, database_name: str, model_id: str | None = None, model_version: str | None = None):
        """
        Initializes the runs table handle.

        Args:
            database_name: The name of the database the runs are stored in.
            model_id: The model id to filter the model runs by.
            model_version: The model version to filter the model runs by.
        """
        self._database_name = database_name
        self._model_id = model_id
        self._model_version = model_version
        # Columns
        self.id = runs_table.run_id.alias("id")
        self.model_id = runs_table.model_id
        self.model_version = runs_table.model_version
        self.timestamp = runs_table.timestamp
        self.batch_id = runs_table.batch_id
        self.seq_id = runs_table.seq_id
        self.tags = runs_table.tags
        self.metadata = runs_table.metadata
        self.default_feedback = runs_table.score.alias("default_feedback")
        self.inputs = runs_table.model_inputs.alias("inputs")
        self.outputs = runs_table.model_outputs.alias("outputs")

        self.memory_lookup = memory_lookup

    def select(self, *args: str | Column | Alias):
        """
        A thin peewee wrapper method for selecting columns in the query.

        Args:
            args: The columns to select

        Returns:
            The query object for chaining

        Examples:
            >>> my_query.select("id", "timestamp")
        """
        return ModelRunsSelectQuery(self, *args)


class ModelRunsSelectQuery(BaseSelectQuery):
    def __init__(self, table: RunsHandle, *args: str | Column | Alias):
        self._table = table
        self._aggregated_memory_lookups = False
        self._joined_memory_lookups = False
        # initialize the query
        self._query = runs_table.select().order_by(runs_table.timestamp.desc())
        if self._table._model_id is not None:
            self._query = self._query.where(runs_table.model_id == self._table._model_id)  # type: ignore
        if self._table._model_version is not None:
            self._query = self._query.where(runs_table.model_version == self._table._model_version)  # type: ignore
        if not args:
            self._selects = [
                self._table.id,
                self._table.model_id,
                self._table.model_version,
                self._table.timestamp,
                self._table.tags,
                self._table.metadata,
                self._table.batch_id,
                self._table.seq_id,
                self._table.inputs,
                self._table.outputs,
                self._table.default_feedback,
            ]
        else:
            self._selects = []
            for arg in args:
                if isinstance(arg, str):
                    col = getattr(self._table, arg)
                    if col is None or not (isinstance(col, Column) or isinstance(col, Alias)):
                        raise ValueError(f"Invalid column: {arg}")
                    self._selects.append(col)
                else:
                    self._selects.append(arg)

    def aggregate_memory_lookups(self, *args):
        """
        Thin peewee wrapper method for aggregating the memory lookups.

        Args:
            args: The columns to aggregate by

        Returns:
            The query object for chaining

        Examples:
            >>> my_query.aggregate_memory_lookups(
            ...     fn.avg(runs.lookups.score).alias("avg_score"),
            ... )
        """
        if self._joined_memory_lookups:
            raise ValueError("Cannot aggregate and join memory lookups at the same time.")
        assert self._selects is not None
        assert self._query is not None
        if args:
            self._selects.extend(args)
        self._query = self._query.join(
            memory_lookups_table, on=(runs_table.run_id == memory_lookups_table.run_id)
        ).group_by(
            runs_table.run_id
        )  # type: ignore
        self._aggregated_memory_lookups = True
        return self

    def join_memory_lookups(self) -> "ModelRunsSelectQuery":
        """
        Thin peewee wrapper method for joining the memory lookups.

        Returns:
            The query object for chaining
        """
        if self._aggregated_memory_lookups:
            raise ValueError("Cannot aggregate and join memory lookups at the same time.")
        assert self._selects is not None
        assert self._query is not None
        self._selects.extend(
            [
                memory_lookups_table.reference_row_data.alias("_table_row_snapshot"),
                self._table.memory_lookup.score,
                memory_lookups_table.attention_weight,
                memory_lookups_table.layer_name.alias("model_layer_name"),
                memory_lookups_table.table_name,
                memory_lookups_table.index_name.alias("memory_index_name"),
                memory_lookups_table.index_column.alias("_index_column_name"),
                memory_lookups_table.extra_columns.alias("_lookup_column_names"),
            ]
        )
        self._query = self._query.join(
            memory_lookups_table, on=(runs_table.run_id == memory_lookups_table.run_id)
        )  # type: ignore
        self._joined_memory_lookups = True
        return self

    def fetch(self, limit: int | None = None, offset: int | None = None) -> list[dict[str, Any]]:
        """
        Fetches the runs from the database.

        Args:
            limit: The number of rows to fetch
            offset: The number of rows to skip

        Returns:
            A list of dictionaries mapping column names to values.

        Examples:
            >>> my_query.fetch(1)
            [{'id': 42, tags: ['tag1', 'tag2'], ...}]
        """
        assert self._table._database_name is not None
        if limit is not None:
            self.limit(limit)
        if offset is not None:
            self.offset(offset)
        statement, params = self._query.select(*self._selects).sql()
        rows = OrcaClient.run_sql(self._table._database_name, statement, params)
        # decode the results
        for row in rows:
            # decode Run data
            if row.get("tags") is not None:
                row["tags"] = set(json.loads(row["tags"]))
            if row.get("metadata") is not None:
                row["metadata"] = json.loads(row["metadata"])
            if row.get("inputs") is not None:
                row["inputs"] = json.loads(row["inputs"])
            if row.get("outputs") is not None:
                row["outputs"] = json.loads(row["outputs"])
            if row.get("seq_id") is not None:
                row["seq_id"] = decode_uuid(row["seq_id"])
            if row.get("batch_id") is not None:
                row["batch_id"] = decode_uuid(row["batch_id"])
            if row.get("timestamp") is not None:
                row["timestamp"] = datetime.fromtimestamp(row["timestamp"])

            # decode memory data if joined
            if self._joined_memory_lookups:
                table_row_snapshot = json.loads(row["_table_row_snapshot"])
                del row["_table_row_snapshot"]
                # decode the index column embedding
                row["$embedding"] = decode_tensor(table_row_snapshot["$embedding"])
                # unpack index column value
                index_column_name = row["_index_column_name"]
                row[index_column_name] = table_row_snapshot[index_column_name]
                del row["_index_column_name"]
                # unpack additional lookup columns
                lookup_column_names = [c for c in json.loads(row["_lookup_column_names"]) if not c.startswith("$")]
                for col_name in lookup_column_names:
                    row[col_name] = table_row_snapshot[col_name]
                del row["_lookup_column_names"]
        return rows
