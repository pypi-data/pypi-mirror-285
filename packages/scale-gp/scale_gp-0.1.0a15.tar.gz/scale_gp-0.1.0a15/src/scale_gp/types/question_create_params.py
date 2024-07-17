# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = ["QuestionCreateParams"]


class QuestionCreateParams(TypedDict, total=False):
    account_id: Required[str]
    """The ID of the account that owns the given entity."""

    prompt: Required[str]

    title: Required[str]

    type: Required[Literal["categorical", "free_text"]]
    """An enumeration."""

    choices: Iterable[object]
    """List of choices for the question. Required for CATEGORICAL questions."""

    conditions: Iterable[object]
    """Conditions for the question to be shown."""

    dropdown: bool
    """Whether the question is displayed as a dropdown in the UI."""

    multi: bool
    """Whether the question allows multiple answers."""

    required: bool
    """Whether the question is required."""
