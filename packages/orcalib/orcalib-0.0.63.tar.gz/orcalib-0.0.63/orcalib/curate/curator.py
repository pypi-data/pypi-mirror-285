from typing import TYPE_CHECKING, Any, Literal, Union

if TYPE_CHECKING:
    from orcalib.database import OrcaDatabase
    from orcalib.orca_torch import OrcaModule

from ._tracking import (
    FeedbackKind,
    RunId,
    record_model_feedback,
    record_model_input_output,
)
from .memories_handle import MemoriesHandle
from .runs_handle import RunsHandle


class Curator:
    """
    The Curator class provides an interface to record and query model feedback and input/output data.

    Attributes:
        model_id: The model id to filter runs by.
        model_version: The model version to filter runs by.
        runs: The runs table handle.

    Examples:
            Given a model with a lookup layer:
            ```py
            class MyModel(OrcaModel):
                def __init__(self):
                    super().__init__(
                        db,
                        model_id="my_model_id"
                        model_version="1"
                    )
                    self.lookup = OrcaLookupLayer(
                        memory_index_name="text_index",
                        lookup_column_names=["label, "$embedding"],
                        num_memories=10
                    )

                def forward(self, x):
                    res = self.lookup(x)
                    # do something with the memories

            model = MyModel()
            ```

            Create a curator for the model:
            >>> curator = Curator(model)
            >>> curator.model_id
            'my_model_id'
            >>> curator.model_version
            '1'

            Record feedback and input/output data for a model run:
            >>> curator.record_model_feedback(
            ...     run_ids=1,
            ...     feedback=0.5,
            ...     name="default",
            ...     kind="CONTINUOUS"
            ... )
            >>> curator.record_model_input_output(
            ...     run_ids=1,
            ...     inputs="test input",
            ...     outputs="test output"
            ... )

            Query the runs of a model:
            >>> runs_handle = curator.runs
            >>> runs_handle.select(
            ...     "inputs", "outputs", "default_feedback"
            ... ).where(runs_handle.id == 1).fetch()
            [{'inputs': 'test input', 'outputs': 'test output', 'default_feedback': 0.5}]

            Query the memories of a model:
            >>> my_memories_handle = curator.get_memories_handle("my_index")
            >>> my_memories_handle.select("label", "text").aggregate_runs(
            ...     fn.avg(runs_handle.default_feedback).alias("avg_feedback"),
            ...     fn.count(runs_handle.id).alias("num_runs")
            ... ).fetch(1)
            [{'label': 'my_label', 'text': 'my_text', 'avg_feedback': 0.5, 'num_runs': 1}]
    """

    runs: RunsHandle
    """A handle to query model runs."""

    def __init__(
        self,
        target: Union["OrcaModule", "OrcaDatabase", str],
        model_id: str | None = None,
        model_version: str | None = None,
    ):
        """
        Initializes the curator

        Args:
            target: The target model or database to curate.
            model_id: The model id to filter the results by.
            model_version: The model version to filter the results by.
        """
        from orcalib.database import OrcaDatabase
        from orcalib.orca_torch import OrcaModule

        if isinstance(target, OrcaModule):
            if not target.curate_database:
                raise ValueError("The target module does not have a curate database set.")
            self.database_name = target.curate_database
        elif isinstance(target, OrcaDatabase):
            self.database_name = target.name
        elif isinstance(target, str):
            self.database_name = target
        else:
            raise ValueError("Must provide a valid OrcaModule, OrcaDatabase, or database name.")
        # set model default filters if available
        self.model_id = model_id or (target.curate_model_id if isinstance(target, OrcaModule) else None)
        self.model_version = model_version or (target.curate_model_version if isinstance(target, OrcaModule) else None)
        # table handles
        self.runs = RunsHandle(self.database_name, self.model_id, self.model_version)

    def get_memories_handle(self, index_name: str) -> MemoriesHandle:
        """
        Get a handle to query the memories table associated with the given index or table name.

        Args:
            index_name: The index name associated with the memories.

        Returns:
            A handle to query the memories table.

        Examples:
            >>> my_memories = curator.get_memories_handle("my_index")
            >>> my_memories.select("label", "text").

        """
        return MemoriesHandle(
            index_name=index_name,
            database_name=self.database_name,
            model_id=self.model_id,
            model_version=self.model_version,
        )

    # TODO: consider switching the interface to list[Feedback] instead of several lists
    def record_model_feedback(
        self,
        run_ids: list[RunId] | RunId,
        feedback: list[float] | float | int | list[int],
        name: str = "default",
        kind: FeedbackKind = FeedbackKind.CONTINUOUS,
    ) -> None:
        """
        Records feedback for the given model runs.

        Args:
            run_ids: The run ids for which the feedback is recorded.
            feedback: The feedback to be recorded.
            name: The name of the feedback.
            kind: The kind of feedback
        """
        record_model_feedback(self.database_name, run_ids, feedback, name, kind)

    # TODO: consider switching the interface to list[InputOutput] instead of several lists
    def record_model_input_output(
        self, run_ids: list[RunId] | RunId, inputs: list[Any] | Any | None, outputs: list[Any] | Any | None
    ) -> None:
        """
        Records the inputs and outputs of the given model runs.

        Args:
            run_ids: The run ids for which the inputs and outputs are recorded.
            inputs: The inputs to be recorded.
            outputs: The outputs to be recorded.
        """
        record_model_input_output(self.database_name, run_ids, inputs, outputs)
