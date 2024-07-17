# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = [
    "TestCaseBatchParams",
    "Body",
    "BodyTestCaseData",
    "BodyTestCaseDataArtifactSchemaGeneration",
    "BodyTestCaseDataArtifactSchemaGenerationExpectedExtraInfo",
    "BodyTestCaseDataArtifactSchemaGenerationExpectedExtraInfoChunkExtraInfoSchema",
    "BodyTestCaseDataArtifactSchemaGenerationExpectedExtraInfoChunkExtraInfoSchemaChunk",
    "BodyTestCaseDataArtifactSchemaGenerationExpectedExtraInfoStringExtraInfoSchema",
    "BodyTestCaseDataSchemaGenerationBase",
    "BodyTestCaseDataSchemaGenerationBaseExpectedExtraInfo",
    "BodyTestCaseDataSchemaGenerationBaseExpectedExtraInfoChunkExtraInfoSchema",
    "BodyTestCaseDataSchemaGenerationBaseExpectedExtraInfoChunkExtraInfoSchemaChunk",
    "BodyTestCaseDataSchemaGenerationBaseExpectedExtraInfoStringExtraInfoSchema",
]


class TestCaseBatchParams(TypedDict, total=False):
    body: Required[Iterable[Body]]


class BodyTestCaseDataArtifactSchemaGenerationExpectedExtraInfoChunkExtraInfoSchemaChunk(TypedDict, total=False):
    metadata: Required[object]

    text: Required[str]


class BodyTestCaseDataArtifactSchemaGenerationExpectedExtraInfoChunkExtraInfoSchema(TypedDict, total=False):
    chunks: Required[Iterable[BodyTestCaseDataArtifactSchemaGenerationExpectedExtraInfoChunkExtraInfoSchemaChunk]]

    schema_type: Literal["CHUNKS"]


class BodyTestCaseDataArtifactSchemaGenerationExpectedExtraInfoStringExtraInfoSchema(TypedDict, total=False):
    info: Required[str]

    schema_type: Literal["STRING"]


BodyTestCaseDataArtifactSchemaGenerationExpectedExtraInfo = Union[
    BodyTestCaseDataArtifactSchemaGenerationExpectedExtraInfoChunkExtraInfoSchema,
    BodyTestCaseDataArtifactSchemaGenerationExpectedExtraInfoStringExtraInfoSchema,
]


class BodyTestCaseDataArtifactSchemaGeneration(TypedDict, total=False):
    artifact_ids_filter: Required[List[str]]

    input: Required[str]

    expected_extra_info: BodyTestCaseDataArtifactSchemaGenerationExpectedExtraInfo

    expected_output: str


class BodyTestCaseDataSchemaGenerationBaseExpectedExtraInfoChunkExtraInfoSchemaChunk(TypedDict, total=False):
    metadata: Required[object]

    text: Required[str]


class BodyTestCaseDataSchemaGenerationBaseExpectedExtraInfoChunkExtraInfoSchema(TypedDict, total=False):
    chunks: Required[Iterable[BodyTestCaseDataSchemaGenerationBaseExpectedExtraInfoChunkExtraInfoSchemaChunk]]

    schema_type: Literal["CHUNKS"]


class BodyTestCaseDataSchemaGenerationBaseExpectedExtraInfoStringExtraInfoSchema(TypedDict, total=False):
    info: Required[str]

    schema_type: Literal["STRING"]


BodyTestCaseDataSchemaGenerationBaseExpectedExtraInfo = Union[
    BodyTestCaseDataSchemaGenerationBaseExpectedExtraInfoChunkExtraInfoSchema,
    BodyTestCaseDataSchemaGenerationBaseExpectedExtraInfoStringExtraInfoSchema,
]


class BodyTestCaseDataSchemaGenerationBase(TypedDict, total=False):
    input: Required[str]

    expected_extra_info: BodyTestCaseDataSchemaGenerationBaseExpectedExtraInfo

    expected_output: str


BodyTestCaseData = Union[BodyTestCaseDataArtifactSchemaGeneration, BodyTestCaseDataSchemaGenerationBase]


class Body(TypedDict, total=False):
    schema_type: Required[Literal["GENERATION"]]
    """An enumeration."""

    test_case_data: Required[BodyTestCaseData]
    """The data for the test case in a format matching the provided schema_type"""

    account_id: str
    """The ID of the account that owns the given entity."""

    chat_history: object
    """Used for tracking previous chat interactions for multi-chat test cases"""

    test_case_metadata: object
    """Metadata for the test case"""
