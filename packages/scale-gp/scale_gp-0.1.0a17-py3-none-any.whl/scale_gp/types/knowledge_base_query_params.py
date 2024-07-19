# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["KnowledgeBaseQueryParams"]


class KnowledgeBaseQueryParams(TypedDict, total=False):
    query: Required[str]
    """
    The natural language query to be answered by referencing the data ingested into
    the knowledge base
    """

    top_k: Required[int]
    """Number of chunks to return.

    Must be greater than 0 if specified. If not specified, all chunks will be
    returned.
    """

    include_embeddings: bool
    """Whether or not to include the embeddings for each chunk"""

    metadata_filters: object
    """Optional filter by metadata fields, encoded as a JSON object"""

    verbose: bool
    """Enable or disable verbose logging"""
