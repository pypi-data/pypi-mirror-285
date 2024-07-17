# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["QuestionResponse"]


class QuestionResponse(BaseModel):
    id: str
    """The unique identifier of the entity."""

    account_id: str
    """The ID of the account that owns the given entity."""

    created_at: datetime
    """The date and time when the entity was created in ISO format."""

    created_by_user_id: str
    """The user who originally created the entity."""

    prompt: str

    title: str

    type: Literal["categorical", "free_text"]
    """An enumeration."""

    choices: Optional[List[object]] = None
    """List of choices for the question. Required for CATEGORICAL questions."""

    conditions: Optional[List[object]] = None
    """Conditions for the question to be shown."""

    dropdown: Optional[bool] = None
    """Whether the question is displayed as a dropdown in the UI."""

    multi: Optional[bool] = None
    """Whether the question allows multiple answers."""

    required: Optional[bool] = None
    """Whether the question is required."""
