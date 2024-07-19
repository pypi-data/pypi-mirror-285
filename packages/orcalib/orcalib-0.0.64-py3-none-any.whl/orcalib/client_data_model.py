from typing import Any, Optional, TypedDict

import numpy as np
from pandas import DataFrame
from pydantic import BaseModel

from orca_common import ColumnName, Order, OrderByColumns, RowDict
from orca_common.api_types import OperationEnum


class ApiFilter(BaseModel):
    """Client-side model of a filter that's used with calls to `select(...)`"""

    op: OperationEnum
    args: tuple[str, str | int | float | bool] | list["ApiFilter"]


# Type alias for various types of row data that can be passed to the insert/update/upsert function.
RowData = RowDict | DataFrame | list[RowDict]
OrderByColumn = ColumnName | tuple[ColumnName, Order]


class SimpleTableQueryRequest(BaseModel):
    """Client-side model of the request to the `simple_table_query` endpoint.

    NOTE:
        This is currently a duplicate of the server's model, but we want them to
        remain separate for now, since the client's model may change in the future.
    """

    columns: list[str] | None = None
    limit: int | None = None
    filter: ApiFilter | None = None
    order_by_columns: OrderByColumns | None = None
    default_order: Order = Order.ASCENDING


class TableRowResponse(TypedDict):
    """Client-side model of a row in the response from the `simple_table_query` endpoint."""

    row_id: int
    column_values: dict[ColumnName, Any]


class TableSelectResponse(TypedDict):
    """Client-side model of the response from the `simple_table_query` endpoint."""

    status_code: int
    rows: list[TableRowResponse]


def decode_ndarray(obj: Any) -> Any:
    """Decode a JSON object that was encoded with `encode_ndarray`.

    TODO: This needs to be generalized to use the type handles to decode column types.

    Args:
        obj: The object to decode

    Returns:
        The decoded object
    """
    if "__ndarray__" in obj:
        return np.array(obj["__ndarray__"])
    return obj
