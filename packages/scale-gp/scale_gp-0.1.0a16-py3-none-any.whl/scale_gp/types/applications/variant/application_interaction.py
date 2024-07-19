# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["ApplicationInteraction"]


class ApplicationInteraction(BaseModel):
    id: str

    application_spec_id: str

    application_variant_id: str

    created_at: datetime
    """The date and time when the entity was created in ISO format."""

    duration_ms: int
    """How much time the step took in milliseconds(ms)"""

    input: object

    operation_status: Literal["SUCCESS", "ERROR"]
    """An enumeration."""

    output: object

    start_timestamp: datetime

    chat_thread_id: Optional[str] = None
