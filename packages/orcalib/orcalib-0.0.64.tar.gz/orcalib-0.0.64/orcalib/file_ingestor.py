import json
import pickle
from abc import ABC
from collections import Counter
from typing import Any, Hashable, Union, cast
from urllib.request import urlopen

import numpy as np
import pandas
from datasets import ClassLabel, Dataset, DatasetDict, Sequence, Value, load_dataset
from tqdm.auto import trange

from orca_common import RowDict
from orcalib.database import OrcaDatabase, TableCreateMode, TableHandle
from orcalib.orca_types import (
    DocumentT,
    DocumentTypeHandle,
    EnumT,
    FloatT,
    Int8T,
    IntT,
    OrcaTypeHandle,
    TextT,
    VectorT,
)


class FileIngestorBase(ABC):
    """Base class for file ingestors"""

    def __init__(
        self,
        db: OrcaDatabase,
        table_name: str,
        dataset: list[dict[Hashable, Any]],
        auto_table: bool = False,
        replace: bool = False,
        max_text_col_len: int = 220,
    ):
        """
        Initialize the ingestor

        Args:
            db: The database to ingest into
            table_name: The name of the table to ingest the data into
            dataset: The dataset to ingest
            auto_table: Whether to automatically create the table if it doesn't exist
            replace: Whether to replace the table if it already exists
            max_text_col_len: If a column has a median length greater than this, it will be parsed as a document column
        """
        if auto_table and not replace:
            assert table_name not in db.tables, "Table already exists - can't use auto_table"
        self._db = db
        self._table_name = table_name
        self._dataset = dataset
        self._auto_table = auto_table
        self._replace = replace
        self._convert_to_hashable_format = True
        self._schema = None
        self.max_text_col_len = max_text_col_len

    def _schema_from_dataset(self) -> dict[str, OrcaTypeHandle]:
        """Infer schema from the dataset"""
        # TODO: replace this with an implementation based on pandas.DataFrame.dtypes instead
        if self._schema is not None:
            return self._schema
        # Infer schema from the dataset since it's not known yet
        sample = self._dataset[0]
        self._schema = {}
        for col in sample.keys():
            if isinstance(sample[col], str):
                # TODO: use median length of the column instead of the first row length
                if len(sample[col]) > self.max_text_col_len:
                    self._schema[col] = DocumentT
                else:
                    self._schema[col] = TextT
            # TODO: rethink if we really want to default to 32-bit ints and floats, which do not match python's precision
            elif isinstance(sample[col], int):
                self._schema[col] = IntT
            elif isinstance(sample[col], float):
                self._schema[col] = FloatT
            elif isinstance(sample[col], bool):
                # TODO: use BoolT when it's implemented
                self._schema[col] = Int8T
            elif isinstance(sample[col], list):
                self._schema[col] = VectorT[len(sample[col])]
            else:
                raise ValueError(f"Can't infer type for column {col}")
        return self._schema

    def _df_to_row_dict_list(self, df: pandas.DataFrame) -> list[dict]:
        """Convert DataFrame to list of dicts, similar to to_dict(orient="records") but handles arrays"""
        dataset = []
        columns = df.columns.values.tolist()
        for i in trange(len(df)):
            curr_row = df.iloc[i].tolist()
            for j in range(len(curr_row)):
                # Process vectors and numpy integers
                if isinstance(curr_row[j], str) and curr_row[j][0] == "[":
                    if curr_row[j][-1] != "]":
                        raise Exception("Incorrectly formatted list in CSV file")
                    curr_row[j] = [float(x.strip()) for x in curr_row[j][1 : len(curr_row[j]) - 1].split(",")]
                elif isinstance(curr_row[j], np.integer):
                    curr_row[j] = int(curr_row[j])
                elif isinstance(curr_row[j], np.ndarray):
                    curr_row[j] = list(curr_row[j])
            dataset.append(dict(zip(columns, curr_row)))
        return dataset

    def _create_table(self) -> Any:
        schema = self._schema_from_dataset()
        print(f"Creating table {self._table_name} with schema {schema}")
        return self._db.create_table(
            self._table_name,
            if_table_exists=(
                TableCreateMode.REPLACE_CURR_TABLE if self._replace else TableCreateMode.ERROR_IF_TABLE_EXISTS
            ),
            **schema,
        )

    def run(self, only_create_table: bool = False, skip_create_table: bool = False) -> TableHandle:
        """
        Ingest the data into the database table

        Args:
            only_create_table: Whether to only create the table and not ingest the data
            skip_create_table: Whether to skip creating the table

        Returns:
            A handle to the table that was created
        """
        if self._auto_table and not skip_create_table:
            table = self._create_table()
        else:
            table = self._db[self._table_name]
            # Convert file schema to hashable format with strings so we can use Counter
            file_col_types = []
            for file_col in self._schema_from_dataset().values():
                if isinstance(file_col, DocumentTypeHandle):
                    file_col_types.append("text")
                else:
                    file_col_types.append(file_col.full_name)
            # Do the same for the schema of the existing table
            curr_col_types = []
            for table_col in table.columns:
                col_type = table.columns[table_col].dtype
                # Just like above, we treat text and document as the same type
                if col_type == "document":
                    curr_col_types.append("text")
                else:
                    curr_col_types.append(col_type)
            # Raise exception if the file schema does not match the table schema
            if self._auto_table and Counter(file_col_types) != Counter(curr_col_types):
                raise Exception("File schema does not match table schema")
        # ingest the data
        if not only_create_table:
            table.insert(*cast(list[dict[str, Any]], list(self._dataset)))
        return table


class PickleIngestor(FileIngestorBase):
    """
    Ingestor for [Pickle][pickle] files

    Examples:
        >>> ingestor = PickleIngestor(db, "my_table", "data.pkl", auto_table=True)
        >>> table = ingestor.run()
    """

    def __init__(
        self,
        db: OrcaDatabase,
        table_name: str,
        dataset_path: str,
        auto_table: bool = False,
        replace: bool = False,
        max_text_col_len: int = 220,
    ):
        """
        Initialize the ingestor

        Args:
            db: The database to ingest into
            table_name: The name of the table to ingest the data into
            dataset: The dataset to ingest
            auto_table: Whether to automatically create the table if it doesn't exist
            replace: Whether to replace the table if it already exists
            max_text_col_len: If a column has a median length greater than this, it will be parsed as a document column
        """
        if dataset_path[0:4] == "http":
            with urlopen(dataset_path) as f:
                dataset = pickle.load(f)
        else:
            with open(dataset_path, "rb") as f:
                dataset = pickle.load(f)
        FileIngestorBase.__init__(self, db, table_name, dataset, auto_table, replace, max_text_col_len)


class JSONIngestor(FileIngestorBase):
    """
    Ingestor for JSON files

    Examples:
        >>> ingestor = JSONIngestor(db, "my_table", "data.json", auto_table=True)
        >>> table = ingestor.run()
    """

    def __init__(
        self,
        db: OrcaDatabase,
        table_name: str,
        dataset_path: str,
        auto_table: bool = False,
        replace: bool = False,
        max_text_col_len: int = 220,
    ):
        """
        Initialize the ingestor

        Args:
            db: The database to ingest into
            table_name: The name of the table to ingest the data into
            dataset: The dataset to ingest
            auto_table: Whether to automatically create the table if it doesn't exist
            replace: Whether to replace the table if it already exists
            max_text_col_len: If a column has a median length greater than this, it will be parsed as a document column
        """
        if dataset_path[0:4] == "http":
            with urlopen(dataset_path) as f:
                json_dataset = json.load(f)
        else:
            with open(dataset_path, "r") as f:
                json_dataset = json.load(f)
        if isinstance(json_dataset, list):
            dataset = json_dataset
        elif "data" in json_dataset:
            dataset = json_dataset["data"]
        else:
            raise Exception("Incorrectly formatted JSON file")
        FileIngestorBase.__init__(self, db, table_name, dataset, auto_table, replace, max_text_col_len)


class JSONLIngestor(FileIngestorBase):
    """
    Ingestor for [JSONL](https://jsonlines.org/) files

    Examples:
        >>> ingestor = JSONLIngestor(db, "my_table", "data.jsonl", auto_table=True)
        >>> table = ingestor.run()
    """

    def __init__(
        self,
        db: OrcaDatabase,
        table_name: str,
        dataset_path: str,
        auto_table: bool = False,
        replace: bool = False,
        max_text_col_len: int = 220,
    ):
        """
        Initialize the ingestor

        Args:
            db: The database to ingest into
            table_name: The name of the table to ingest the data into
            dataset: The dataset to ingest
            auto_table: Whether to automatically create the table if it doesn't exist
            replace: Whether to replace the table if it already exists
            max_text_col_len: If a column has a median length greater than this, it will be parsed as a document column
        """
        dataset = []
        if dataset_path[0:4] == "http":
            with urlopen(dataset_path) as f:
                for line in f:
                    dataset.append(json.loads(line))
        else:
            with open(dataset_path, "r") as f:
                for line in f:
                    dataset.append(json.loads(line))
        FileIngestorBase.__init__(self, db, table_name, dataset, auto_table, replace)


class CSVIngestor(FileIngestorBase):
    """
    Ingestor for CSV files

    Examples:
        >>> ingestor = CSVIngestor(db, "my_table", "data.csv", auto_table=True)
        >>> table = ingestor.run()
    """

    def __init__(
        self,
        db: OrcaDatabase,
        table_name: str,
        dataset_path: str,
        auto_table: bool = False,
        replace: bool = False,
        max_text_col_len: int = 220,
    ):
        """
        Initialize the ingestor

        Args:
            db: The database to ingest into
            table_name: The name of the table to ingest the data into
            dataset: The dataset to ingest
            auto_table: Whether to automatically create the table if it doesn't exist
            replace: Whether to replace the table if it already exists
            max_text_col_len: If a column has a median length greater than this, it will be parsed as a document column
        """
        df = pandas.read_csv(dataset_path)
        FileIngestorBase.__init__(
            self, db, table_name, self._df_to_row_dict_list(df), auto_table, replace, max_text_col_len
        )


class ParquetIngestor(FileIngestorBase):
    """
    Ingestor for [Parquet](https://parquet.apache.org/) files

    Examples:
        >>> ingestor = ParquetIngestor(db, "my_table", "data.parquet", auto_table=True)
        >>> table = ingestor.run()
    """

    def __init__(
        self,
        db: OrcaDatabase,
        table_name: str,
        dataset_path: str,
        auto_table: bool = False,
        replace: bool = False,
        max_text_col_len: int = 220,
    ):
        """
        Initialize the ingestor

        Args:
            db: The database to ingest into
            table_name: The name of the table to ingest the data into
            dataset: The dataset to ingest
            auto_table: Whether to automatically create the table if it doesn't exist
            replace: Whether to replace the table if it already exists
            max_text_col_len: If a column has a median length greater than this, it will be parsed as a document column
        """
        try:
            import pyarrow
        except ImportError:
            raise ImportError("Please install pyarrow to use the ParquetIngestor")

        df = pyarrow.parquet.read_table(dataset_path).to_pandas()
        FileIngestorBase.__init__(
            self, db, table_name, self._df_to_row_dict_list(df), auto_table, replace, max_text_col_len
        )


class HFDatasetIngestor(FileIngestorBase):
    """
    [HuggingFace Dataset](https://huggingface.co/datasets) Ingestor

    Examples:
        >>> ingestor = HFDatasetIngestor(db, "my_table", "imdb", split="train")
        >>> table = ingestor.run()
    """

    def __init__(
        self,
        db: OrcaDatabase,
        table_name: str,
        dataset: Dataset | str,
        auto_table: bool = False,
        replace: bool = False,
        max_text_col_len: int = 220,
        split: str | None = None,
        cache_dir: str | None = None,
    ):
        """
        Initialize the ingestor

        Args:
            db: The database to ingest into
            table_name: The name of the table to ingest the data into
            dataset: The dataset to ingest
            auto_table: Whether to automatically create the table if it doesn't exist
            replace: Whether to replace the table if it already exists
            max_text_col_len: If a column has a median length greater than this, it will be parsed as a document column
            split: The split of the dataset to ingest
            cache_dir: The directory to cache the dataset in
        """
        super().__init__(db, table_name, [], auto_table, replace)
        if isinstance(dataset, str):
            temp = load_dataset(dataset, cache_dir=cache_dir)
            if isinstance(temp, DatasetDict):
                temp = temp[split or "train"]
            assert isinstance(temp, Dataset)
            self._dataset = temp
        else:
            self._dataset = dataset

    def _schema_from_dataset(self) -> dict[str, OrcaTypeHandle]:
        """Infer schema from the dataset"""
        # If schema is already known, return it
        if self._schema is not None:
            return self._schema
        # Otherwise, infer schema from the dataset
        self._schema = {}
        for name, field_type in self._dataset.features.items():
            if isinstance(field_type, ClassLabel):
                self._schema[name] = EnumT[field_type.names]
            elif isinstance(field_type, Value):
                if field_type.dtype == "string":
                    if np.median([len(t) for t in self._dataset[name]]) > self.max_text_col_len:
                        self._schema[name] = DocumentT
                    else:
                        self._schema[name] = TextT
                else:
                    try:
                        self._schema[name] = OrcaTypeHandle.from_string(field_type.dtype)
                    except ValueError:
                        raise ValueError(f"Unknown dtype {field_type.dtype} for column {name}")
            elif isinstance(field_type, Sequence):
                length = field_type.length if field_type.length >= 0 else len(self._dataset[0][name])
                try:
                    self._schema[name] = OrcaTypeHandle.from_string(f"{field_type.feature.dtype}[{length}]")
                except ValueError:
                    raise ValueError(f"Unknown sequence dtype {field_type.feature.dtype} for column {name}")
            else:
                raise ValueError(f"Unknown type {field_type} for column {name}")
        return self._schema
