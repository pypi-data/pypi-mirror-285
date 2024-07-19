# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = ["ApplicationProcessParams", "Edge", "Node", "NodeConfiguration", "History", "Overrides"]


class ApplicationProcessParams(TypedDict, total=False):
    edges: Required[Iterable[Edge]]
    """List of edges in the application graph"""

    inputs: Required[Dict[str, object]]
    """Input data for the application. You must provide inputs for each input node"""

    nodes: Required[Iterable[Node]]
    """List of nodes in the application graph"""

    version: Required[Literal["V0"]]
    """Version of the application schema"""

    history: Iterable[History]
    """History of the application"""

    overrides: Dict[str, Overrides]
    """Optional overrides for the application"""


class Edge(TypedDict, total=False):
    from_field: Required[str]

    from_node: Required[str]

    to_field: Required[str]

    to_node: Required[str]


class NodeConfiguration(TypedDict, total=False):
    value: Required[object]


class Node(TypedDict, total=False):
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

    configuration: Dict[str, NodeConfiguration]


class History(TypedDict, total=False):
    request: Required[str]
    """Request inputs"""

    response: Required[str]
    """Response outputs"""

    session_data: object
    """Session data corresponding to the request response pair"""


class Overrides(TypedDict, total=False):
    artifact_ids_filter: List[str]

    type: Literal["knowledge_base_schema"]
