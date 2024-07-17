# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["EvaluationConfigResponse"]


class EvaluationConfigResponse(BaseModel):
    id: str
    """The unique identifier of the entity."""

    account_id: str
    """The ID of the account that owns the given entity."""

    created_at: datetime
    """The date and time when the entity was created in ISO format."""

    created_by_user_id: str
    """The user who originally created the entity."""

    evaluation_type: Literal["studio", "llm_auto", "human", "llm_benchmark"]
    """An enumeration."""

    question_set_id: str

    studio_project_id: Optional[str] = None
