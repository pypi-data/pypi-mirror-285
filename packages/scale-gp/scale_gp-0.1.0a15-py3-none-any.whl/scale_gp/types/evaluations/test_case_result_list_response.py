# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ..._models import BaseModel
from ..shared.test_case_result_response_with_views import TestCaseResultResponseWithViews

__all__ = ["TestCaseResultListResponse"]


class TestCaseResultListResponse(BaseModel):
    __test__ = False
    current_page: int
    """The current page number."""

    items: List[TestCaseResultResponseWithViews]
    """The data returned for the current page."""

    items_per_page: int
    """The number of items per page."""

    total_item_count: int
    """The total number of items of the query"""
