from itertools import chain
from typing import IO, Any, Optional, cast

from pandas import DataFrame
from tqdm.auto import tqdm

from orca_common import ColumnName, RowDict, TableName
from orcalib.client import ColumnSpec, OrcaClient
from orcalib.client_data_model import RowData
from orcalib.orca_expr import ColumnHandle, OrcaExpr
from orcalib.orca_types import CustomSerializable, OrcaTypeHandle
from orcalib.table_query import TableQuery


class TableHandle:
    """A handle to a table in the Orca database"""

    db_name: str
    table_name: TableName
    columns: dict[ColumnName, ColumnSpec]

    def __init__(
        self,
        db_name: str,
        table_name: str,
        # used when cloning a table handle to prevent unnecessary server calls
        _columns: dict[ColumnName, ColumnSpec] | None = None,
    ):
        """
        Create a handle to a table in the database.

        Args:
            db_name: The database name
            table_name: The table name
        """
        if _columns is None:
            self.columns = {col.name: col for col in OrcaClient.table_info(db_name, table_name)}
        else:
            self.columns = _columns

        self.db_name = db_name
        self.table_name = table_name

    def get_column_type_dict(self) -> dict[ColumnName, OrcaTypeHandle]:
        """
        Get a dictionary of column names and orca types for this table

        Returns:
            A dictionary of column names and orca types

        Examples:
            >>> table.get_column_type_dict()
            { 'id': IntT, 'str': TextT, 'img': ImageT["PNG"], 'vec': VectorT[64] }
        """
        return {name: OrcaTypeHandle.from_string(spec.dtype) for name, spec in self.columns.items()}

    def copy(self) -> "TableHandle":
        """Create a copy of this table handle

        Returns:
            A copy of this table handle
        """
        return TableHandle(
            self.db_name,
            self.table_name,
            _columns=self.columns.copy(),
        )

    def copy_with_overrides(self, **kwargs) -> "TableHandle":
        """Create a copy of this table handle with the specified attributes changed

        Args:
            **kwargs: the attributes to change

        Returns:
            A copy of this table handle with the specified attributes changed
        """
        result = self.copy()

        for key, value in kwargs.items():
            setattr(result, key, value)

        return result

    def __getattr__(self, column_name: str | ColumnHandle) -> ColumnHandle:
        """Get a column handle by name

        Args:
            column_name: The name of the column

        Returns:
            A column handle
        """
        if isinstance(column_name, ColumnHandle):
            if column_name.table_name != self.table_name:
                raise ValueError(f"Column {column_name.column_name} not found in table {self.table_name}")
            return column_name
        if column_name not in self.columns:
            raise Exception(f"Column {column_name} not found in table {self.table_name}")
        return ColumnHandle(self.db_name, self.table_name, column_name)

    def __getitem__(self, column_name: str | ColumnHandle) -> ColumnHandle:
        """Get a column handle by name

        Args:
            column_name: The name of the column

        Returns:
            A column handle
        """
        return self.__getattr__(column_name)

    def __contains__(self, column_name: str) -> bool:
        return column_name in self.columns

    def get_column(self, column_name: str | ColumnHandle) -> ColumnHandle:
        """Get a column handle by name

        Args:
            column_name: The name of the column

        Returns:
            A column handle
        """
        return self.__getattr__(column_name)

    def select(self, *args) -> TableQuery:
        """
        Start a new query on this table

        Args:
            *args: The columns to select

        Returns:
            The chainable query object

        Examples:
            >>> table.select('id', 'name').where(table.tester = 1).fetch(2)
            [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
        """
        return TableQuery(self.db_name, self).select(*args)

    def where(self, *args) -> TableQuery:
        """Start a new query on this table

        Args:
            *args: The columns to select

        Returns:
            The chainable query object
        """
        return TableQuery(self.db_name, self).where(*args)

    def order_by(self, *args, **kwargs) -> TableQuery:
        """Start a new query on this table

        Args:
            *args: The columns to select

        Returns:
            The chainable query object
        """
        return TableQuery(self.db_name, self).order_by(*args, **kwargs)

    def fetch(self, *args, **kwargs) -> list[RowDict] | list[tuple[int, RowDict]]:
        """Fetch rows from the table

        Args:
            *args: The columns to fetch

        Returns:
            A list of rows
        """
        return TableQuery(self.db_name, self).fetch(*args, **kwargs)

    def df(self, limit: int | None = None) -> DataFrame:
        """Fetch rows from the table and return as a pandas DataFrame

        Args:
            limit: The maximum number of rows to fetch (default: None)

        Returns:
            A data frame with the rows
        """
        return DataFrame(self.fetch(limit))

    def _extract_rowdicts(self, row_data: RowData) -> list[RowDict]:
        # TODO: Add constraint validation based on column type parameters
        # TODO: Collect file-like object dict for binary uploads
        """Builds a list of RowDict objects from various sources of row data."""

        if isinstance(row_data, DataFrame):
            rows = row_data.to_dict(orient="records")
            return cast(list[RowDict], rows)

        match row_data:
            case dict():
                return [row_data]
            case list() as rows:
                unexpected_elements = [(x, type(x)) for x in rows if not isinstance(x, dict)]
                if unexpected_elements:
                    raise TypeError(f"List elements expected to be dict[ColumnName, Any] but got {unexpected_elements}")
                return row_data
            case _:
                raise TypeError(f"Invalid argument for insert: {row_data} type {type(row_data)}")

    def _parse_row_data(self, positional_data: tuple[RowData, ...], kw_data: Any = None) -> list[RowDict]:
        # TODO: Add collecting constraint violations based on column type parameters
        # TODO: Add collecting file-like objects for binary uploads
        """Converts the positional and keyword arguments to a list of RowDict objects

        Args:
            positional_data: The positional row data to insert.
            kw_data: The keyword row data to insert. This should be a dict[str, Any] where the keys are column names.

        Returns:
            A list of RowDict objects
        """
        # ensure either col or cols is specified, but not both
        if not positional_data and not kw_data:
            raise TypeError("No columns specified for insert")
        if positional_data and kw_data:
            raise TypeError("Cannot specify both positional and keyword arguments")

        if positional_data:
            return list(chain.from_iterable(self._extract_rowdicts(data) for data in positional_data))
        return [kw_data]

    def _extract_binary_values(self, row_dicts: list[RowDict]) -> list[tuple[str, IO[bytes]]]:
        """Extracts binary values from row dicts and adds them to the file dict

        Note:
            DO NOT read/log/inspect the file contents before sending them with the request!
            Otherwise, the file pointer will be at the end of the file and the server will receive
            an empty file.

        Args:
            row_dicts: The row data to insert. This can be a RowDict, a
                pandas DataFrame, or a list of RowDicts.

        Returns:
            A list of tuples of (filename, file-like object) that is
            required for the multipart upload
        """
        # This is a list of tuples of (filename, file-like object) that is required for the multipart upload
        named_file_list: list[tuple[str, IO[bytes]]] = []
        for row_dict in row_dicts:
            for column_name, value in row_dict.items():
                col_type = OrcaTypeHandle.from_string(self.columns[column_name].dtype)
                if not isinstance(col_type, CustomSerializable):
                    continue

                filename = f"upload_{len(named_file_list)}_{column_name}"
                named_file_list.append((filename, col_type.binary_serialize(value)))
                row_dict[column_name] = filename
        return named_file_list

    def insert(
        self,
        *args: RowData,
        _api_version: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Insert rows into the table

        Note:
            Positional and keyword arguments cannot be mixed.

        Args:
            *args: The row data to insert. This can be a RowDict, a pandas DataFrame, or a list of RowDicts.
            **kwargs: Specifies the keys and values to insert. This can be used to insert a single row.

        Examples:
            Insert a single row as a dict:
            >>> table.insert({'id': 1, 'name': 'Alice'})

            Insert multiple rows as multiple arguments:
            >>> table.insert({'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'})

            Insert multiple rows as a list of dicts:
            >>> table.insert([{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}])

            Insert multiple rows as a pandas DataFrame:
            >>> table.insert(pd.DataFrame({'id': [1, 2], 'name': ['Alice', 'Bob']}))

            Insert a single row as keyword arguments:
            >>> table.insert(id=1, name='Alice')
        """
        MAX_BATCH_SIZE = 100

        rows = self._parse_row_data(args, kwargs)
        if len(rows) <= MAX_BATCH_SIZE:
            file_list = self._extract_binary_values(rows)
            OrcaClient.insert(self.db_name, self.table_name, rows, file_list, _api_version=_api_version)
        else:
            # large batch mode
            batches = (rows[i : i + MAX_BATCH_SIZE] for i in range(0, len(rows), MAX_BATCH_SIZE))
            with tqdm(total=len(rows)) as progress_bar:
                for batch in batches:
                    file_list = self._extract_binary_values(batch)
                    OrcaClient.insert(
                        self.db_name,
                        self.table_name,
                        batch,
                        file_list,
                        _api_version=_api_version,
                    )
                    progress_bar.update(len(batch))

    def update(self, data: RowDict, filter: OrcaExpr, _api_version: str | None = None) -> None:
        """
        Update rows in the table

        Args:
            data: The row data to update. This should be a dict[str, Any] where the keys are column names.
            filter: The filter to apply to the rows to update

        Examples:
            >>> table.update([{'name': 'Alice'}], table.id == 1)
        """
        file_list = self._extract_binary_values([data])
        OrcaClient.update(
            self.db_name,
            self.table_name,
            data,
            filter.as_serializable(),
            file_list,
            _api_version=_api_version,
        )

    def upsert(
        self,
        data: RowData,
        key_columns: list[ColumnName],
        _api_version: str | None = None,
    ) -> None:
        """Upsert rows into the table

        Args:
            data: The row data to insert.
            key_columns: The columns to use as the primary key

        Examples:
            >>> table.upsert({'id': 1, 'name': 'Alice'}, ['id'])
        """
        rows = self._parse_row_data((data,))
        file_list = self._extract_binary_values(rows)
        OrcaClient.upsert(
            self.db_name,
            self.table_name,
            rows,
            key_columns,
            file_list,
            _api_version=_api_version,
        )

    def delete(self, filter: OrcaExpr) -> None:
        """
        Delete rows from the table

        Args:
            filter: The filter to apply to the rows to delete

        Examples:
            >>> table.delete(table.id == 1)
        """
        OrcaClient.delete(self.db_name, self.table_name, filter.as_serializable())

    def add_column(self, **columns: OrcaTypeHandle) -> None:
        """Add columns to the table

        Args:
            **columns: The columns to add

        Examples:
            >>> table.add_column(test=TextT.notnull, img=ImageT["PNG"])
        """
        names, dtypes, notnulls, uniques = [], [], [], []
        for column_name, column_type in columns.items():
            names.append(column_name)
            dtypes.append(column_type.full_name)
            notnulls.append(column_type._notnull)
            uniques.append(column_type._unique)
        OrcaClient.add_column(self.db_name, self.table_name, names, dtypes, notnulls, uniques)
        self.columns.update(
            {
                name: ColumnSpec(name=name, dtype=dtype, notnull=notnull, unique=unique)
                for name, dtype, notnull, unique in zip(names, dtypes, notnulls, uniques)
            }
        )

    def drop_column(self, column_names: list[str] | str) -> None:
        """Drop columns from the table

        Args:
            column_names: The column or columns to drop

        Examples:
            >>> table.drop_column('test')

            >>> table.drop_column(['test', 'img'])
        """
        column_names = [column_names] if isinstance(column_names, str) else column_names
        OrcaClient.drop_column(self.db_name, self.table_name, column_names)
        for column_name in column_names:
            del self.columns[column_name]

    def __str__(self) -> str:
        ret = f"{self.db_name}.{self.table_name}(\n"
        for column in self.columns.values():
            ret += f"\t{column.name} {column.dtype}{' NOT NULL' if column.notnull else ''}{' UNIQUE' if column.unique else ''},\n"
        ret += ")"
        return ret

    def __repr__(self) -> str:
        return self.__str__()
