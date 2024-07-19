from enum import Enum
from typing import Any, Literal, TypeAlias
from uuid import UUID

from orcalib.client import OrcaClient, OrcaMetadataDict


class FeedbackKind(str, Enum):
    """
    The kind of feedback that can be recorded.

    Attributes:
        CONTINUOUS: any float values between -1.0 and 1.0 are allowed
        BINARY: only the float or integer -1 or 1 is allowed
        UNARY: only the float or integer 1 is allowed
    """

    CONTINUOUS = "CONTINUOUS"
    BINARY = "BINARY"
    UNARY = "UNARY"


RunId: TypeAlias = int
"""The id of a model run."""


def generate_run_ids(
    db_name: str,
    batch_size: int,
    tags: set[str],
    metadata: OrcaMetadataDict,
    model_id: str,
    model_version: str | None = None,
    seq_id: UUID | None = None,
) -> list[RunId]:
    """Generates run ids for the next model run.

    Args:
        db_name: The name of the database.
        model_id: The id of the model.
        model_version: The version of the model. (default: None)
        batch_size: The batch size.
        tags: The tags for the model run.
        metadata: The metadata for the model run.
        seq_id: The sequence id for the model run. (default: None)
    """
    return OrcaClient.init_forward_pass(
        db_name=db_name,
        model_id=model_id,
        model_version=model_version,
        batch_size=batch_size,
        tags=tags,
        metadata=metadata,
        seq_id=seq_id,
    )


# TODO: consider switching the interface to list[Feedback] instead of several lists
def record_model_feedback(
    db_name: str,
    run_ids: list[RunId] | RunId,
    feedback: list[float] | float | int | list[int],
    name: str = "default",
    kind: FeedbackKind = FeedbackKind.CONTINUOUS,
) -> None:
    """Records feedback for the given model runs.

    Args:
        db_name: The name of the database.
        run_ids: The run ids for which the feedback is recorded.
        feedback: The feedback to be recorded.
        name: The name of the feedback. (default: "default")
        kind: The kind of feedback. (default: FeedbackKind.CONTINUOUS)
    """
    # Ensure feedback is a list of the right length
    if isinstance(feedback, (float, int)):
        feedback = [feedback]
    if isinstance(run_ids, int):
        run_ids = [run_ids]
    if len(feedback) != len(run_ids):
        raise ValueError(f"Feedback length ({len(feedback)}) did not match run_ids length ({len(run_ids)})")
    # Ensure feedback is a list of correct floats based on the passed kind
    float_feedback: list[float] = []
    for f in feedback:
        float_value = float(f)
        match kind:
            case FeedbackKind.UNARY:
                if float_value != 1.0:
                    raise ValueError(f"Unary feedback must be 1.0, got {float_value}")
            case FeedbackKind.BINARY:
                if isinstance(f, bool):
                    float_value = +1.0 if f else -1.0
                if float_value not in (-1.0, +1.0):
                    raise ValueError(f"Binary feedback must be -1 or +1, got {float_value}")
            case FeedbackKind.CONTINUOUS:
                if float_value > 1.0 or float_value < -1.0:
                    raise ValueError(f"Continuous feedback must be between -1 and +1, got {float_value}")
            case _:
                raise ValueError(f"Unsupported feedback kind: {kind}")
        float_feedback.append(float_value)
    # TODO: update api to allow recording several types of feedback with different names
    OrcaClient.record_model_scores(db_name, run_ids, float_feedback)


# TODO: consider switching the interface to list[InputOutput] instead of several lists
def record_model_input_output(
    db_name: str,
    run_ids: list[RunId] | RunId,
    inputs: list[Any] | Any | None,
    outputs: list[Any] | Any | None,
) -> None:
    """Records the inputs and outputs of the given model runs.

    Args:
        db_name: The name of the database.
        run_ids: The run ids for which the inputs and outputs are
            recorded.
        inputs: The inputs to be recorded.
        outputs: The outputs to be recorded.
    """
    if not isinstance(run_ids, list):
        run_ids = [run_ids]
    if inputs is None:
        inputs = [None] * len(run_ids)
    if not isinstance(inputs, list):
        inputs = [inputs]
    if outputs is None:
        outputs = [None] * len(run_ids)
    if not isinstance(outputs, list):
        outputs = [outputs]
    if not (len(inputs) == len(outputs) == len(run_ids)):
        raise ValueError(
            f"Inputs length ({len(inputs)}), output length ({len(outputs)}) and run_ids length ({len(run_ids)}) did not match"
        )
    OrcaClient.record_model_input_output(db_name, run_ids, inputs, outputs)
