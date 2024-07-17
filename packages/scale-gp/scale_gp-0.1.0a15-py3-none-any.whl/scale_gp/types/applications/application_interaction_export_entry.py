# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ApplicationInteractionExportEntry", "Evaluation", "Feedback", "TraceSpan"]


class Evaluation(BaseModel):
    id: str
    """The unique identifier of the entity."""

    application_interaction_id: str

    created_at: datetime
    """The date and time when the entity was created in ISO format."""

    metric_type: str

    score: Optional[float] = None


class Feedback(BaseModel):
    id: str

    application_interaction_id: str

    chat_thread_id: str

    created_at: datetime
    """The date and time when the entity was created in ISO format."""

    description: str

    sentiment: Literal["positive", "negative"]
    """An enumeration."""


class TraceSpan(BaseModel):
    id: str
    """Identifies the application step"""

    application_interaction_id: str
    """The id of the application insight this step belongs to"""

    duration_ms: int
    """How much time the step took in milliseconds(ms)"""

    node_id: str
    """The id of the node in the application_variant config that emitted this insight"""

    operation_status: Literal["SUCCESS", "ERROR"]
    """An enumeration."""

    operation_type: str
    """Type of the operation, e.g. RERANKING"""

    start_timestamp: datetime
    """The start time of the step"""

    operation_input: Optional[object] = None
    """The JSON representation of the input that this step received"""

    operation_metadata: Optional[object] = None
    """The JSON representation of the metadata insights emitted through the execution.

    This can differ based on different types of operations
    """

    operation_output: Optional[object] = None
    """The JSON representation of the output that this step emitted"""


class ApplicationInteractionExportEntry(BaseModel):
    id: str

    application_spec_id: str

    application_variant_id: str

    created_at: datetime
    """The date and time when the entity was created in ISO format."""

    duration_ms: int
    """How much time the step took in milliseconds(ms)"""

    input: object

    operation_status: Literal["SUCCESS", "ERROR"]
    """An enumeration."""

    output: object

    start_timestamp: datetime

    chat_thread_id: Optional[str] = None

    created_by_user_id: Optional[str] = None

    evaluations: Optional[List[Evaluation]] = None

    feedback: Optional[Feedback] = None
    """Represents the user feedback given to a thread entry output"""

    trace_spans: Optional[List[TraceSpan]] = None
