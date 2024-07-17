# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.



from ..._models import BaseModel

__all__ = ["CancelKnowledgeBaseV2UploadResponse"]


class CancelKnowledgeBaseV2UploadResponse(BaseModel):
    canceled: bool
    """Whether cancellation was successful."""

    upload_id: str
    """ID of the knowledge base upload job that was cancelled."""
