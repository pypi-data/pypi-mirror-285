# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from ..._models import BaseModel
from .variant.application_interaction import ApplicationInteraction

__all__ = ["ApplicationInteractionEntry", "Item", "ItemEvaluation", "ItemDetails"]


class ItemEvaluation(BaseModel):
    id: str
    """The unique identifier of the entity."""

    application_interaction_id: str

    created_at: datetime
    """The date and time when the entity was created in ISO format."""

    metric_type: str

    score: Optional[float] = None


class ItemDetails(BaseModel):
    feedback_response: Optional[str] = None

    feedback_sentiment: Optional[Literal["positive", "negative"]] = None
    """An enumeration."""

    tokens_used: Optional[int] = None


class Item(BaseModel):
    evaluations: List[ItemEvaluation]

    interaction: ApplicationInteraction

    details: Optional[ItemDetails] = None

    grader: Optional[str] = None

    metrics: Optional[List[object]] = None


class ApplicationInteractionEntry(BaseModel):
    current_page: int
    """The current page number."""

    items: List[Item]
    """The data returned for the current page."""

    items_per_page: int
    """The number of items per page."""

    total_item_count: int
    """The total number of items of the query"""
