# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["MessageFeedbackParams"]


class MessageFeedbackParams(TypedDict, total=False):
    thread_id: Required[str]

    path_application_interaction_id: Required[Annotated[str, PropertyInfo(alias="application_interaction_id")]]

    body_application_interaction_id: Required[Annotated[str, PropertyInfo(alias="application_interaction_id")]]

    chat_thread_id: Required[str]

    description: Required[str]

    sentiment: Required[Literal["positive", "negative"]]
    """An enumeration."""
