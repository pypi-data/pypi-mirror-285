# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = [
    "ApplicationTestCaseOutputBatchParams",
    "Body",
    "BodyOutput",
    "BodyOutputGenerationExtraInfo",
    "BodyOutputGenerationExtraInfoChunkExtraInfoSchema",
    "BodyOutputGenerationExtraInfoChunkExtraInfoSchemaChunk",
    "BodyOutputGenerationExtraInfoStringExtraInfoSchema",
]


class ApplicationTestCaseOutputBatchParams(TypedDict, total=False):
    body: Required[Iterable[Body]]


class BodyOutputGenerationExtraInfoChunkExtraInfoSchemaChunk(TypedDict, total=False):
    metadata: Required[object]

    text: Required[str]


class BodyOutputGenerationExtraInfoChunkExtraInfoSchema(TypedDict, total=False):
    chunks: Required[Iterable[BodyOutputGenerationExtraInfoChunkExtraInfoSchemaChunk]]

    schema_type: Literal["CHUNKS"]


class BodyOutputGenerationExtraInfoStringExtraInfoSchema(TypedDict, total=False):
    info: Required[str]

    schema_type: Literal["STRING"]


BodyOutputGenerationExtraInfo = Union[
    BodyOutputGenerationExtraInfoChunkExtraInfoSchema, BodyOutputGenerationExtraInfoStringExtraInfoSchema
]


class BodyOutput(TypedDict, total=False):
    generation_output: Required[str]

    generation_extra_info: BodyOutputGenerationExtraInfo


class Body(TypedDict, total=False):
    account_id: Required[str]
    """The ID of the account that owns the given entity."""

    application_variant_id: Required[str]

    evaluation_dataset_version_num: Required[int]

    output: Required[BodyOutput]

    schema_type: Required[Literal["GENERATION"]]
    """An enumeration."""

    test_case_id: Required[str]

    application_interaction_id: str
