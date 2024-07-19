# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ThreadUpdateParams"]


class ThreadUpdateParams(TypedDict, total=False):
    archived_at: str
    """Date when the chat thread is archived, or None to un-archive."""

    title: str
    """The title of the chat thread."""
