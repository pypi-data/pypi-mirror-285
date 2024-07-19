import base64
from typing import Any
from uuid import UUID

import numpy as np
import torch
from pandas import DataFrame
from peewee import Select


def decode_uuid(val) -> UUID:
    buffer = base64.b64decode(val["__bytes__"].encode("utf-8"))
    return UUID(bytes=buffer)


def decode_tensor(val) -> torch.Tensor:
    buffer = base64.b64decode(val["__bytes__"].encode("utf-8"))
    return torch.from_numpy(np.frombuffer(buffer, dtype=np.float32).copy())


class BaseSelectQuery:
    def __init__(self):
        self._query = Select()
        self._selects = []
        pass

    def having(self, *args) -> "BaseSelectQuery":
        """
        Thin peewee wrapper method for having filters on aggregate function results.

        Args:
            args: The conditions to filter by

        Returns:
            The query object for chaining

        Examples:
            >>> my_query.having(sql("avg_model_feedback") == 1.0)
        """
        assert self._query is not None
        self._query = self._query.having(*args)
        return self

    def limit(self, limit: int) -> "BaseSelectQuery":
        """
        Thin peewee wrapper method to limit the number of rows returned.

        Args:
            limit: The maximum number of rows to return

        Returns:
            The query object for chaining

        Examples:
            >>> my_query.limit(5)
        """
        assert self._query is not None
        self._query = self._query.limit(limit)
        return self

    def offset(self, offset: int) -> "BaseSelectQuery":
        """
        Thin peewee wrapper method for applying an offset to the query.

        Args:
            offset: The number of rows to skip

        Returns:
            The query object for chaining

        Examples:
            >>> my_query.offset(5)
        """
        assert self._query is not None
        self._query = self._query.offset(offset)
        return self

    def order_by(self, *args) -> "BaseSelectQuery":
        """
        Thin peewee wrapper method for ordering the results.

        Args:
            args: The columns to order by

        Returns:
            The query object for chaining

        Examples:
            >>> my_query.order_by(runs_handle.id.desc())
        """
        assert self._query is not None
        self._query = self._query.order_by(*args)
        return self

    def where(self, *args) -> "BaseSelectQuery":
        """
        Thin peewee wrapper method for filtering the results.

        Args:
            args: The conditions to filter by

        Returns:
            The query object for chaining

        Examples:
            >>> my_query.where(runs_handle.id == 42)
        """
        assert self._query is not None
        self._query = self._query.where(*args)
        return self

    def fetch(self, limit: int | None = None, offset: int | None = None) -> list[dict[str, Any]]:
        # Must be implemented in the child class
        raise NotImplementedError

    def df(self, limit: int | None = None, offset: int | None = None) -> DataFrame:
        """
        Fetch rows from the table and return as a DataFrame

        Args:
            limit: The maximum number of rows to return, if `None` returns all rows
            offset: The number of rows to skip, if `None` starts from the beginning

        Returns:
            A pandas data frame containing the rows
        """
        return DataFrame(self.fetch(limit, offset))

    def sql(self) -> tuple[str, tuple[Any, ...]]:
        """
        Debugging method to get the SQL query and parameters.

        Returns:
            query: The SQL query
            params: The parameters for the query
        """
        assert self._query is not None
        return self._query.select(*self._selects).sql()
