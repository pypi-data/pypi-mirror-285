# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = ["VariantProcessParams", "History", "Overrides"]


class VariantProcessParams(TypedDict, total=False):
    inputs: Required[Dict[str, object]]
    """Input data for the application. You must provide inputs for each input node"""

    history: Iterable[History]
    """History of the application"""

    overrides: Dict[str, Overrides]
    """Optional overrides for the application"""


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
