# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["EvaluationResponse"]


class EvaluationResponse(BaseModel):
    id: str
    """The unique identifier of the entity."""

    account_id: str
    """The ID of the account that owns the given entity."""

    application_spec_id: str

    completed_test_case_result_count: int
    """The number of test case results that have been completed for the evaluation"""

    created_at: datetime
    """The date and time when the entity was created in ISO format."""

    created_by_user_id: str
    """The user who originally created the entity."""

    description: str

    name: str

    status: Literal["PENDING", "COMPLETED", "FAILED"]
    """An enumeration."""

    total_test_case_result_count: int
    """The total number of test case results for the evaluation"""

    application_variant_id: Optional[str] = None

    archived_at: Optional[datetime] = None
    """The date and time when the entity was archived in ISO format."""

    completed_at: Optional[datetime] = None
    """
    The date and time that all test case results for the evaluation were completed
    for the evaluation in ISO format.
    """

    evaluation_config: Optional[object] = None

    evaluation_config_id: Optional[str] = None
    """The ID of the associated evaluation config."""

    tags: Optional[object] = None
