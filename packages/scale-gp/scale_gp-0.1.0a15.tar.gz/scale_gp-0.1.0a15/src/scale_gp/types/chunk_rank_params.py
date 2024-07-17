# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = [
    "ChunkRankParams",
    "RankStrategy",
    "RankStrategyCrossEncoderRankStrategy",
    "RankStrategyCrossEncoderRankStrategyParams",
    "RankStrategyRougeRankStrategy",
    "RankStrategyRougeRankStrategyParams",
    "RankStrategyModelRankStrategy",
    "RankStrategyModelRankStrategyParams",
    "RelevantChunk",
]


class ChunkRankParams(TypedDict, total=False):
    query: Required[str]
    """Natural language query to re-rank chunks against.

    If a vector store query was originally used to retrieve these chunks, please use
    the same query for this ranking
    """

    rank_strategy: Required[RankStrategy]
    """The ranking strategy to use.

    Rank strategies determine how the ranking is done, They consist of the ranking
    method name and additional params needed to compute the ranking.

    Use the built-in `cross_encoder` or `rouge` strategies or create a custom one
    with the Models API.
    """

    relevant_chunks: Required[Iterable[RelevantChunk]]
    """List of chunks to rank"""

    account_id: str
    """Account to rank chunks with.

    If you have access to more than one account, you must specify an account_id
    """

    top_k: int
    """Number of chunks to return.

    Must be greater than 0 if specified. If not specified, all chunks will be
    returned.
    """


class RankStrategyCrossEncoderRankStrategyParams(TypedDict, total=False):
    cross_encoder_model: Literal["cross-encoder/ms-marco-MiniLM-L-12-v2", "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"]
    """Cross encoder model to use when ranking.

    Currently supports
    [cross-encoder/ms-marco-MiniLM-L-12-v2](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-12-v2)
    and
    [cross-encoder/mmarco-mMiniLMv2-L12-H384-v1](https://huggingface.co/cross-encoder/mmarco-mMiniLMv2-L12-H384-v1).
    """


class RankStrategyCrossEncoderRankStrategy(TypedDict, total=False):
    method: Literal["cross_encoder"]
    """The name of the rank strategy. Must be `cross_encoder`."""

    params: RankStrategyCrossEncoderRankStrategyParams
    """The parameters needed for ranking."""


class RankStrategyRougeRankStrategyParams(TypedDict, total=False):
    metric: str
    """Rouge type, can be n-gram based (e.g.

    rouge1, rouge2) or longest common subsequence (rougeL or rougeLsum)
    """

    score: Literal["precision", "recall", "fmeasure"]
    """Metric to use from Rouge score"""


class RankStrategyRougeRankStrategy(TypedDict, total=False):
    method: Literal["rouge"]
    """The name of the rank strategy."""

    params: RankStrategyRougeRankStrategyParams
    """The parameters needed for ranking."""


class RankStrategyModelRankStrategyParams(TypedDict, total=False):
    base_model_name: str
    """The name of a base model to use for reranking"""

    model_deployment_id: str
    """The model deployment id of a custom model to use for reranking"""

    model_params: object


class RankStrategyModelRankStrategy(TypedDict, total=False):
    method: Literal["model"]
    """Use a model from Models API for ranking."""

    params: RankStrategyModelRankStrategyParams
    """The parameters needed for ranking."""


RankStrategy = Union[RankStrategyCrossEncoderRankStrategy, RankStrategyRougeRankStrategy, RankStrategyModelRankStrategy]


class RelevantChunk(TypedDict, total=False):
    chunk_id: Required[str]
    """The unique ID of the chunk with embedding"""

    score: Required[float]
    """
    A number between 0 and 1 representing how similar a chunk's embedding is to the
    query embedding. Higher numbers mean that this chunk with embedding is more
    similar.
    """

    text: Required[str]
    """The text associated with the chunk"""

    attachment_url: str
    """Original attachment URL from which this chunk got its data from"""

    embedding: Iterable[float]
    """The vector embedding of the text associated with the chunk"""

    metadata: object
    """
    Any additional key value pairs of information stored by you on the chunk with
    embedding
    """

    title: str
    """Title for this chunk, for example the file name"""

    user_supplied_metadata: object
    """
    Any additional key value pairs of information returned from the custom chunking.
    """
