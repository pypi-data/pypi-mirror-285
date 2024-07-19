# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["GenerationJobCreateParams"]


class GenerationJobCreateParams(TypedDict, total=False):
    group_by_artifact_id: bool
    """
    If this flag is true, for every generated test case, the chunks used to generate
    it will be guaranteed to be from the same document (artifact).
    """

    num_test_cases: int
    """Number of test cases to generate for the evaluation dataset"""
