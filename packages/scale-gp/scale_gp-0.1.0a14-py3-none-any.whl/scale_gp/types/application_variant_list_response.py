# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, Annotated

from .._utils import PropertyInfo
from .._models import BaseModel

__all__ = [
    "ApplicationVariantListResponse",
    "Item",
    "ItemOnlineApplicationVariantResponse",
    "ItemOnlineApplicationVariantResponseConfiguration",
    "ItemOnlineApplicationVariantResponseConfigurationEdge",
    "ItemOnlineApplicationVariantResponseConfigurationNode",
    "ItemOnlineApplicationVariantResponseConfigurationNodeConfiguration",
    "ItemOfflineApplicationVariantResponse",
    "ItemOfflineApplicationVariantResponseConfiguration",
]


class ItemOnlineApplicationVariantResponseConfigurationEdge(BaseModel):
    from_field: str

    from_node: str

    to_field: str

    to_node: str


class ItemOnlineApplicationVariantResponseConfigurationNodeConfiguration(BaseModel):
    value: object


class ItemOnlineApplicationVariantResponseConfigurationNode(BaseModel):
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

    configuration: Optional[Dict[str, ItemOnlineApplicationVariantResponseConfigurationNodeConfiguration]] = None


class ItemOnlineApplicationVariantResponseConfiguration(BaseModel):
    edges: List[ItemOnlineApplicationVariantResponseConfigurationEdge]

    nodes: List[ItemOnlineApplicationVariantResponseConfigurationNode]


class ItemOnlineApplicationVariantResponse(BaseModel):
    id: str

    account_id: str
    """The ID of the account that owns the given entity."""

    application_spec_id: str

    configuration: ItemOnlineApplicationVariantResponseConfiguration

    created_at: datetime
    """The date and time when the entity was created in ISO format."""

    created_by_user_id: str
    """The user who originally created the entity."""

    name: str

    version: Literal["V0"]

    description: Optional[str] = None
    """Optional description of the application variant"""


class ItemOfflineApplicationVariantResponseConfiguration(BaseModel):
    metadata: Optional[object] = None
    """User defined metadata about the offline application"""

    output_schema_type: Optional[Literal["completion_only", "context_string", "context_chunks"]] = None
    """An enumeration."""


class ItemOfflineApplicationVariantResponse(BaseModel):
    id: str

    account_id: str
    """The ID of the account that owns the given entity."""

    application_spec_id: str

    configuration: ItemOfflineApplicationVariantResponseConfiguration

    created_at: datetime
    """The date and time when the entity was created in ISO format."""

    created_by_user_id: str
    """The user who originally created the entity."""

    name: str

    version: Literal["OFFLINE"]

    description: Optional[str] = None
    """Optional description of the application variant"""


Item = Annotated[
    Union[ItemOnlineApplicationVariantResponse, ItemOfflineApplicationVariantResponse],
    PropertyInfo(discriminator="version"),
]


class ApplicationVariantListResponse(BaseModel):
    current_page: int
    """The current page number."""

    items: List[Item]
    """The data returned for the current page."""

    items_per_page: int
    """The number of items per page."""

    total_item_count: int
    """The total number of items of the query"""
