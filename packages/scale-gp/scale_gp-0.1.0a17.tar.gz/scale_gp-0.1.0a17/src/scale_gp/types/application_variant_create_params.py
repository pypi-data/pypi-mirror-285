# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = [
    "ApplicationVariantCreateParams",
    "OnlineApplicationVariantRequest",
    "OnlineApplicationVariantRequestConfiguration",
    "OnlineApplicationVariantRequestConfigurationEdge",
    "OnlineApplicationVariantRequestConfigurationNode",
    "OnlineApplicationVariantRequestConfigurationNodeConfiguration",
    "OfflineApplicationVariantRequest",
    "OfflineApplicationVariantRequestConfiguration",
]


class OnlineApplicationVariantRequest(TypedDict, total=False):
    account_id: Required[str]
    """The ID of the account that owns the given entity."""

    application_spec_id: Required[str]

    configuration: Required[OnlineApplicationVariantRequestConfiguration]

    name: Required[str]

    version: Required[Literal["V0"]]

    description: str
    """Optional description of the application variant"""


class OnlineApplicationVariantRequestConfigurationEdge(TypedDict, total=False):
    from_field: Required[str]

    from_node: Required[str]

    to_field: Required[str]

    to_node: Required[str]


class OnlineApplicationVariantRequestConfigurationNodeConfiguration(TypedDict, total=False):
    value: Required[object]


class OnlineApplicationVariantRequestConfigurationNode(TypedDict, total=False):
    id: Required[str]

    application_node_schema_id: Required[
        Literal[
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
    ]
    """An enumeration."""

    configuration: Dict[str, OnlineApplicationVariantRequestConfigurationNodeConfiguration]


class OnlineApplicationVariantRequestConfiguration(TypedDict, total=False):
    edges: Required[Iterable[OnlineApplicationVariantRequestConfigurationEdge]]

    nodes: Required[Iterable[OnlineApplicationVariantRequestConfigurationNode]]


class OfflineApplicationVariantRequest(TypedDict, total=False):
    account_id: Required[str]
    """The ID of the account that owns the given entity."""

    application_spec_id: Required[str]

    configuration: Required[OfflineApplicationVariantRequestConfiguration]

    name: Required[str]

    version: Required[Literal["OFFLINE"]]

    description: str
    """Optional description of the application variant"""


class OfflineApplicationVariantRequestConfiguration(TypedDict, total=False):
    metadata: object
    """User defined metadata about the offline application"""

    output_schema_type: Literal["completion_only", "context_string", "context_chunks"]
    """An enumeration."""


ApplicationVariantCreateParams = Union[OnlineApplicationVariantRequest, OfflineApplicationVariantRequest]
