# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel
from .theme_response import ThemeResponse

__all__ = ["ThemeListResponse"]


class ThemeListResponse(BaseModel):
    current_page: int
    """The current page number."""

    items: List[ThemeResponse]
    """The data returned for the current page."""

    items_per_page: int
    """The number of items per page."""

    total_item_count: int
    """The total number of items of the query"""
