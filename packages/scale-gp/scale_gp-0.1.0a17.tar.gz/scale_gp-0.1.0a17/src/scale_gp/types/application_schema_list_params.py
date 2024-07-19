# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ApplicationSchemaListParams"]


class ApplicationSchemaListParams(TypedDict, total=False):
    version: Required[Literal["OFFLINE", "V0"]]
    """
    An enum representing the version states of an application and its nodes'
    schemas. Attributes: V0: The initial version of an application schema.
    """
