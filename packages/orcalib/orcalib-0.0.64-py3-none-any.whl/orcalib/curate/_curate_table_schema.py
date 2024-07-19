from peewee import Column, SqliteDatabase, Table


class _CurateForwardPassTable(Table):
    def __init__(self):
        super().__init__("__curate_forward_pass")
        self.run_id = Column(self, "run_id")
        self.model_id = Column(self, "model_id")
        self.model_version = Column(self, "model_version")
        self.timestamp = Column(self, "timestamp")
        self.batch_id = Column(self, "batch_id")
        self.seq_id = Column(self, "seq_id")
        self.tags = Column(self, "tags")
        self.metadata = Column(self, "metadata")
        self.score = Column(self, "score")
        self.model_inputs = Column(self, "model_inputs")
        self.model_outputs = Column(self, "model_outputs")
        self.bind(SqliteDatabase(None))


class _CurateMemoriesTable(Table):
    def __init__(self):
        super().__init__("__curate_memories")
        self.run_id = Column(self, "run_id")
        self.layer_name = Column(self, "layer_name")
        self.memory_score = Column(self, "memory_score")
        self.table_name = Column(self, "table_name")
        self.index_name = Column(self, "index_name")
        self.index_column = Column(self, "index_column")
        self.extra_columns = Column(self, "extra_columns")
        self.reference_row_id = Column(self, "reference_row_id")
        self.reference_row_data = Column(self, "reference_row_data")
        self.attention_weight = Column(self, "attention_weight")
        self.bind(SqliteDatabase(None))


memory_lookups_table = _CurateMemoriesTable()
runs_table = _CurateForwardPassTable()
