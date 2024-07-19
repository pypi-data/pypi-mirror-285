# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from datetime import datetime
from typing_extensions import Literal, Annotated

from ..._utils import PropertyInfo
from ..._models import BaseModel
from ..knowledge_base_data_source_response import KnowledgeBaseDataSourceResponse

__all__ = [
    "KnowledgeBaseUploadScheduleResponseWithViews",
    "ChunkingStrategyConfig",
    "ChunkingStrategyConfigCharacterChunkingStrategyConfig",
    "ChunkingStrategyConfigTokenChunkingStrategyConfig",
    "ChunkingStrategyConfigCustomChunkingStrategyConfig",
]


class ChunkingStrategyConfigCharacterChunkingStrategyConfig(BaseModel):
    strategy: Literal["character"]

    chunk_overlap: Optional[int] = None
    """Number of characters to overlap between chunks.

    If not specified, an overlap of 200 will be used. For example if the chunk size
    is 3 and the overlap size is 1, and the text to chunk is 'abcde', the chunks
    will be 'abc', 'cde'.
    """

    chunk_size: Optional[int] = None
    """Maximum number of characters in each chunk.

    If not specified, a chunk size of 1000 will be used.
    """

    separator: Optional[str] = None
    """Character designating breaks in input data.

    Text data will first be split into sections by this separator, then each section
    will be split into chunks of size `chunk_size`.
    """


class ChunkingStrategyConfigTokenChunkingStrategyConfig(BaseModel):
    strategy: Literal["token"]

    chunk_overlap: Optional[int] = None
    """Number of tokens to overlap between chunks.

    If not specified, an overlap of 0 will be used. Not this if only followed
    approximately.
    """

    max_chunk_size: Optional[int] = None
    """Maximum number of tokens in each chunk.

    If not specified, a maximum chunk size of 600 will be used.
    """

    separator: Optional[str] = None
    """Character designating breaks in input data.

    Text data will first be split into sections by this separator, then each section
    will be split into chunks of size `chunk_size`.
    """

    target_chunk_size: Optional[int] = None
    """Target number of tokens in each chunk.

    If not specified, a target chunk size of 200 will be used.
    """


class ChunkingStrategyConfigCustomChunkingStrategyConfig(BaseModel):
    endpoint: str
    """Endpoint path to call for custom chunking"""

    strategy: Literal["custom"]

    params: Optional[object] = None
    """Parameters that will be appended to the body of the request for the chunk."""


ChunkingStrategyConfig = Annotated[
    Union[
        ChunkingStrategyConfigCharacterChunkingStrategyConfig,
        ChunkingStrategyConfigTokenChunkingStrategyConfig,
        ChunkingStrategyConfigCustomChunkingStrategyConfig,
    ],
    PropertyInfo(discriminator="strategy"),
]


class KnowledgeBaseUploadScheduleResponseWithViews(BaseModel):
    id: str
    """The unique identifier of the entity."""

    account_id: str
    """The ID of the account that owns the given entity."""

    chunking_strategy_config: ChunkingStrategyConfig

    created_at: datetime
    """The date and time when the entity was created in ISO format."""

    created_by_user_id: str
    """The user who originally created the entity."""

    interval: float

    knowledge_base_data_source_id: str

    knowledge_base_id: str

    status: Literal["HEALTHY", "UNHEALTHY", "ERROR", "PAUSED"]
    """An enumeration."""

    updated_at: datetime
    """The date and time when the entity was last updated in ISO format."""

    knowledge_base_data_source: Optional[KnowledgeBaseDataSourceResponse] = None

    next_run_at: Optional[datetime] = None

    status_reason: Optional[str] = None
