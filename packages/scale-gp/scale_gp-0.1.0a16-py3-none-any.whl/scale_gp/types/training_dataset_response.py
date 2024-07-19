# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["TrainingDatasetResponse"]


class TrainingDatasetResponse(BaseModel):
    id: str
    """The unique identifier of the entity."""

    account_id: str
    """The ID of the account that owns the given entity."""

    created_at: datetime
    """The date and time when the entity was created in ISO format."""

    created_by_user_id: str
    """The user who originally created the entity."""

    data_source: Literal[
        "S3", "SharePoint", "LocalFile", "LocalChunks", "GoogleDrive", "AzureBlobStorage", "Confluence", "Slack"
    ]
    """An enumeration."""

    name: str
    """The name of the dataset"""

    schema_type: Literal["GENERATION", "RERANKING_QUESTIONS"]
    """An enumeration."""
