# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .knowledge_base_data_source_response import KnowledgeBaseDataSourceResponse

__all__ = [
    "KnowledgeBaseItemV2",
    "EmbeddingConfig",
    "EmbeddingConfigEmbeddingConfigModelsAPI",
    "EmbeddingConfigEmbeddingConfigBase",
    "ArtifactsStatus",
    "Connection",
]


class EmbeddingConfigEmbeddingConfigModelsAPI(BaseModel):
    api_model_deployment_id: str = FieldInfo(alias="model_deployment_id")
    """The ID of the deployment of the created model in the Models API V3."""

    type: Literal["models_api"]
    """The type of the embedding configuration."""


class EmbeddingConfigEmbeddingConfigBase(BaseModel):
    embedding_model: Literal[
        "sentence-transformers/all-MiniLM-L12-v2",
        "sentence-transformers/multi-qa-distilbert-cos-v1",
        "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        "openai/text-embedding-ada-002",
        "openai/text-embedding-3-small",
        "openai/text-embedding-3-large",
        "embed-english-v3.0",
        "embed-english-light-v3.0",
        "embed-multilingual-v3.0",
    ]
    """An enumeration."""

    type: Optional[Literal["base"]] = None
    """The type of the embedding configuration."""


EmbeddingConfig = Union[EmbeddingConfigEmbeddingConfigModelsAPI, EmbeddingConfigEmbeddingConfigBase]


class ArtifactsStatus(BaseModel):
    artifacts_chunking: int
    """Number of artifacts in the chunking state"""

    artifacts_completed: int
    """Number of artifacts uploaded successfully."""

    artifacts_embedding: int
    """Number of artifacts in the embedding state"""

    artifacts_failed: int
    """Number of artifacts that failed while being processed."""

    artifacts_pending: int
    """Previously: Number of artifacts awaiting upload.

    Note that this status will be deprecated soon and should show 0
    """

    artifacts_uploading: int
    """Number of artifacts with upload in progress."""


class Connection(BaseModel):
    knowledge_base_data_source: KnowledgeBaseDataSourceResponse
    """The knowledge base data source entity."""

    last_uploaded_at: datetime
    """The date and time when the last upload for the data source was initiated."""

    deletion_status: Optional[Literal["DELETING", "FAILED"]] = None
    """An enumeration."""


class KnowledgeBaseItemV2(BaseModel):
    created_at: str
    """The timestamp at which the knowledge base was created"""

    embedding_config: EmbeddingConfig
    """The embedding configuration"""

    knowledge_base_id: str
    """The unique ID of the knowledge base"""

    knowledge_base_name: str
    """The name of the knowledge base"""

    vector_store_id: str
    """(Legacy) The unique ID of the underlying vector store.

    This is to allow for backwards compatibility with the V1 Vector Store APIs. This
    will be removed in the near future.
    """

    artifact_count: Optional[int] = None
    """The total number of artifacts in the knowledge base.

    Only returned with the `view=ArtifactCount` query parameter.
    """

    artifacts_status: Optional[ArtifactsStatus] = None
    """
    Number of artifacts in each of the various states, such as completed and failed
    for this knowledge base. This includes all data sources.
    """

    cluster_status: Optional[str] = None
    """Whether the knowledge base has been clustered."""

    connections: Optional[List[Connection]] = None
    """The data source connections associated with the knowledge base.

    Only returned with the `view=Connections` query parameter.
    """

    metadata: Optional[object] = None
    """Metadata associated with the knowledge base"""

    updated_at: Optional[str] = None
    """The timestamp at which the knowledge base was last updated"""
