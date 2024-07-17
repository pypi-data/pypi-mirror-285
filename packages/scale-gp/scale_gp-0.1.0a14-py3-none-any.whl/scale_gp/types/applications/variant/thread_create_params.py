# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["ThreadCreateParams"]


class ThreadCreateParams(TypedDict, total=False):
    path_application_variant_id: Required[Annotated[str, PropertyInfo(alias="application_variant_id")]]

    account_id: Required[str]
    """The ID of the account that owns the given entity."""

    body_application_variant_id: Required[Annotated[str, PropertyInfo(alias="application_variant_id")]]

    title: Required[str]
