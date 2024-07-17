# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import TypedDict

__all__ = ["InteractionExportParams"]


class InteractionExportParams(TypedDict, total=False):
    faithfulness_max_score: float
    """Return only interactions with a faithfulness score below this value."""

    faithfulness_min_score: float
    """Return only interactions with a faithfulness score above this value."""

    from_ts: int
    """The starting (oldest) timestamp window in seconds."""

    has_feedback_response: bool
    """Return only interactions where the user has provided a feedback response."""

    has_negative_feedback: bool
    """Return only interactions with the negative feedback."""

    has_positive_feedback: bool
    """Return only interactions with the positive feedback."""

    limit: int
    """Maximum number of artifacts to be returned by the given endpoint.

    Defaults to 100 and cannot be greater than 10k.
    """

    page: int
    """Page number for pagination to be returned by the given endpoint.

    Starts at page 1
    """

    relevance_max_score: float
    """Return only interactions with a relevance score below this value."""

    relevance_min_score: float
    """Return only interactions with a relevance score above this value."""

    search_text: str
    """
    Return only interactions where either the prompt or the response contain this
    substring.
    """

    to_ts: int
    """The ending (most recent) timestamp in seconds."""

    variants: List[str]
    """Which variants to filter on"""
