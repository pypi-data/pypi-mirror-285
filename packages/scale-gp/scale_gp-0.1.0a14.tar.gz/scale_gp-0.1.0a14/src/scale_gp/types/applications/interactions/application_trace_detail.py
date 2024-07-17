# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from datetime import datetime
from typing_extensions import Literal

from ...._models import BaseModel
from ..variant.application_interaction import ApplicationInteraction

__all__ = [
    "ApplicationTraceDetail",
    "ApplicationVariant",
    "ApplicationVariantConfiguration",
    "ApplicationVariantConfigurationApplicationConfiguration",
    "ApplicationVariantConfigurationApplicationConfigurationEdge",
    "ApplicationVariantConfigurationApplicationConfigurationNode",
    "ApplicationVariantConfigurationApplicationConfigurationNodeConfiguration",
    "ApplicationVariantConfigurationOfflineApplicationConfiguration",
    "Span",
]


class ApplicationVariantConfigurationApplicationConfigurationEdge(BaseModel):
    from_field: str

    from_node: str

    to_field: str

    to_node: str


class ApplicationVariantConfigurationApplicationConfigurationNodeConfiguration(BaseModel):
    value: object


class ApplicationVariantConfigurationApplicationConfigurationNode(BaseModel):
    id: str

    application_node_schema_id: Literal[
        "text_input_schema",
        "text_output_schema",
        "knowledge_base_schema",
        "reranker_schema",
        "prompt_engineering_schema",
        "completion_model_schema",
        "external_endpoint_schema",
        "document_input_schema",
        "map_reduce_schema",
        "document_search_schema",
        "document_prompt_schema",
    ]
    """An enumeration."""

    configuration: Optional[Dict[str, ApplicationVariantConfigurationApplicationConfigurationNodeConfiguration]] = None


class ApplicationVariantConfigurationApplicationConfiguration(BaseModel):
    edges: List[ApplicationVariantConfigurationApplicationConfigurationEdge]

    nodes: List[ApplicationVariantConfigurationApplicationConfigurationNode]


class ApplicationVariantConfigurationOfflineApplicationConfiguration(BaseModel):
    metadata: Optional[object] = None
    """User defined metadata about the offline application"""

    output_schema_type: Optional[Literal["completion_only", "context_string", "context_chunks"]] = None
    """An enumeration."""


ApplicationVariantConfiguration = Union[
    ApplicationVariantConfigurationApplicationConfiguration,
    ApplicationVariantConfigurationOfflineApplicationConfiguration,
]


class ApplicationVariant(BaseModel):
    id: str

    account_id: str
    """The ID of the account that owns the given entity."""

    application_spec_id: str

    configuration: ApplicationVariantConfiguration

    created_at: datetime
    """The date and time when the entity was created in ISO format."""

    created_by_user_id: str
    """The user who originally created the entity."""

    name: str

    version: Literal["OFFLINE", "V0"]
    """
    An enum representing the version states of an application and its nodes'
    schemas. Attributes: V0: The initial version of an application schema.
    """

    description: Optional[str] = None
    """Optional description of the application variant"""


class Span(BaseModel):
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


class ApplicationTraceDetail(BaseModel):
    application_variant: ApplicationVariant
    """Application variant"""

    interaction: ApplicationInteraction
    """Interaction details"""

    feedback: Optional[Literal["positive", "negative"]] = None
    """An enumeration."""

    feedback_comment: Optional[str] = None
    """Feedback comment"""

    metadata: Optional[object] = None
    """Trace metadata"""

    spans: Optional[List[Span]] = None
    """List of Span IDs belonging to this trace"""

    thread_interactions: Optional[List[ApplicationInteraction]] = None
    """List of interactions in the same thread"""
