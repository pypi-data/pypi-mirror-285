# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, Annotated

from .._utils import PropertyInfo
from .._models import BaseModel

__all__ = [
    "ApplicationVariantCreateResponse",
    "OnlineApplicationVariantResponse",
    "OnlineApplicationVariantResponseConfiguration",
    "OnlineApplicationVariantResponseConfigurationEdge",
    "OnlineApplicationVariantResponseConfigurationNode",
    "OnlineApplicationVariantResponseConfigurationNodeConfiguration",
    "OfflineApplicationVariantResponse",
    "OfflineApplicationVariantResponseConfiguration",
]


class OnlineApplicationVariantResponseConfigurationEdge(BaseModel):
    from_field: str

    from_node: str

    to_field: str

    to_node: str


class OnlineApplicationVariantResponseConfigurationNodeConfiguration(BaseModel):
    value: object


class OnlineApplicationVariantResponseConfigurationNode(BaseModel):
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

    configuration: Optional[Dict[str, OnlineApplicationVariantResponseConfigurationNodeConfiguration]] = None


class OnlineApplicationVariantResponseConfiguration(BaseModel):
    edges: List[OnlineApplicationVariantResponseConfigurationEdge]

    nodes: List[OnlineApplicationVariantResponseConfigurationNode]


class OnlineApplicationVariantResponse(BaseModel):
    id: str

    account_id: str
    """The ID of the account that owns the given entity."""

    application_spec_id: str

    configuration: OnlineApplicationVariantResponseConfiguration

    created_at: datetime
    """The date and time when the entity was created in ISO format."""

    created_by_user_id: str
    """The user who originally created the entity."""

    name: str

    version: Literal["V0"]

    description: Optional[str] = None
    """Optional description of the application variant"""


class OfflineApplicationVariantResponseConfiguration(BaseModel):
    metadata: Optional[object] = None
    """User defined metadata about the offline application"""

    output_schema_type: Optional[Literal["completion_only", "context_string", "context_chunks"]] = None
    """An enumeration."""


class OfflineApplicationVariantResponse(BaseModel):
    id: str

    account_id: str
    """The ID of the account that owns the given entity."""

    application_spec_id: str

    configuration: OfflineApplicationVariantResponseConfiguration

    created_at: datetime
    """The date and time when the entity was created in ISO format."""

    created_by_user_id: str
    """The user who originally created the entity."""

    name: str

    version: Literal["OFFLINE"]

    description: Optional[str] = None
    """Optional description of the application variant"""


ApplicationVariantCreateResponse = Annotated[
    Union[OnlineApplicationVariantResponse, OfflineApplicationVariantResponse], PropertyInfo(discriminator="version")
]
