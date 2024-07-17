# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = [
    "UploadScheduleCreateParams",
    "ChunkingStrategyConfig",
    "ChunkingStrategyConfigCharacterChunkingStrategyConfig",
    "ChunkingStrategyConfigTokenChunkingStrategyConfig",
    "ChunkingStrategyConfigCustomChunkingStrategyConfig",
]


class UploadScheduleCreateParams(TypedDict, total=False):
    chunking_strategy_config: Required[ChunkingStrategyConfig]

    interval: Required[float]

    knowledge_base_data_source_id: Required[str]

    account_id: str
    """The ID of the account that owns the given entity."""

    next_run_at: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]


class ChunkingStrategyConfigCharacterChunkingStrategyConfig(TypedDict, total=False):
    strategy: Required[Literal["character"]]

    chunk_overlap: int
    """Number of characters to overlap between chunks.

    If not specified, an overlap of 200 will be used. For example if the chunk size
    is 3 and the overlap size is 1, and the text to chunk is 'abcde', the chunks
    will be 'abc', 'cde'.
    """

    chunk_size: int
    """Maximum number of characters in each chunk.

    If not specified, a chunk size of 1000 will be used.
    """

    separator: str
    """Character designating breaks in input data.

    Text data will first be split into sections by this separator, then each section
    will be split into chunks of size `chunk_size`.
    """


class ChunkingStrategyConfigTokenChunkingStrategyConfig(TypedDict, total=False):
    strategy: Required[Literal["token"]]

    chunk_overlap: int
    """Number of tokens to overlap between chunks.

    If not specified, an overlap of 0 will be used. Not this if only followed
    approximately.
    """

    max_chunk_size: int
    """Maximum number of tokens in each chunk.

    If not specified, a maximum chunk size of 600 will be used.
    """

    separator: str
    """Character designating breaks in input data.

    Text data will first be split into sections by this separator, then each section
    will be split into chunks of size `chunk_size`.
    """

    target_chunk_size: int
    """Target number of tokens in each chunk.

    If not specified, a target chunk size of 200 will be used.
    """


class ChunkingStrategyConfigCustomChunkingStrategyConfig(TypedDict, total=False):
    endpoint: Required[str]
    """Endpoint path to call for custom chunking"""

    strategy: Required[Literal["custom"]]

    params: object
    """Parameters that will be appended to the body of the request for the chunk."""


ChunkingStrategyConfig = Union[
    ChunkingStrategyConfigCharacterChunkingStrategyConfig,
    ChunkingStrategyConfigTokenChunkingStrategyConfig,
    ChunkingStrategyConfigCustomChunkingStrategyConfig,
]
