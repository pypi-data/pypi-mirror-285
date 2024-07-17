# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = [
    "TestCaseCreateParams",
    "TestCaseData",
    "TestCaseDataArtifactSchemaGeneration",
    "TestCaseDataArtifactSchemaGenerationExpectedExtraInfo",
    "TestCaseDataArtifactSchemaGenerationExpectedExtraInfoChunkExtraInfoSchema",
    "TestCaseDataArtifactSchemaGenerationExpectedExtraInfoChunkExtraInfoSchemaChunk",
    "TestCaseDataArtifactSchemaGenerationExpectedExtraInfoStringExtraInfoSchema",
    "TestCaseDataSchemaGenerationBase",
    "TestCaseDataSchemaGenerationBaseExpectedExtraInfo",
    "TestCaseDataSchemaGenerationBaseExpectedExtraInfoChunkExtraInfoSchema",
    "TestCaseDataSchemaGenerationBaseExpectedExtraInfoChunkExtraInfoSchemaChunk",
    "TestCaseDataSchemaGenerationBaseExpectedExtraInfoStringExtraInfoSchema",
]


class TestCaseCreateParams(TypedDict, total=False):
    schema_type: Required[Literal["GENERATION"]]
    """An enumeration."""

    test_case_data: Required[TestCaseData]
    """The data for the test case in a format matching the provided schema_type"""

    account_id: str
    """The ID of the account that owns the given entity."""

    chat_history: object
    """Used for tracking previous chat interactions for multi-chat test cases"""

    test_case_metadata: object
    """Metadata for the test case"""


class TestCaseDataArtifactSchemaGenerationExpectedExtraInfoChunkExtraInfoSchemaChunk(TypedDict, total=False):
    metadata: Required[object]

    text: Required[str]


class TestCaseDataArtifactSchemaGenerationExpectedExtraInfoChunkExtraInfoSchema(TypedDict, total=False):
    chunks: Required[Iterable[TestCaseDataArtifactSchemaGenerationExpectedExtraInfoChunkExtraInfoSchemaChunk]]

    schema_type: Literal["CHUNKS"]


class TestCaseDataArtifactSchemaGenerationExpectedExtraInfoStringExtraInfoSchema(TypedDict, total=False):
    info: Required[str]

    schema_type: Literal["STRING"]


TestCaseDataArtifactSchemaGenerationExpectedExtraInfo = Union[
    TestCaseDataArtifactSchemaGenerationExpectedExtraInfoChunkExtraInfoSchema,
    TestCaseDataArtifactSchemaGenerationExpectedExtraInfoStringExtraInfoSchema,
]


class TestCaseDataArtifactSchemaGeneration(TypedDict, total=False):
    artifact_ids_filter: Required[List[str]]

    input: Required[str]

    expected_extra_info: TestCaseDataArtifactSchemaGenerationExpectedExtraInfo

    expected_output: str


class TestCaseDataSchemaGenerationBaseExpectedExtraInfoChunkExtraInfoSchemaChunk(TypedDict, total=False):
    metadata: Required[object]

    text: Required[str]


class TestCaseDataSchemaGenerationBaseExpectedExtraInfoChunkExtraInfoSchema(TypedDict, total=False):
    chunks: Required[Iterable[TestCaseDataSchemaGenerationBaseExpectedExtraInfoChunkExtraInfoSchemaChunk]]

    schema_type: Literal["CHUNKS"]


class TestCaseDataSchemaGenerationBaseExpectedExtraInfoStringExtraInfoSchema(TypedDict, total=False):
    info: Required[str]

    schema_type: Literal["STRING"]


TestCaseDataSchemaGenerationBaseExpectedExtraInfo = Union[
    TestCaseDataSchemaGenerationBaseExpectedExtraInfoChunkExtraInfoSchema,
    TestCaseDataSchemaGenerationBaseExpectedExtraInfoStringExtraInfoSchema,
]


class TestCaseDataSchemaGenerationBase(TypedDict, total=False):
    input: Required[str]

    expected_extra_info: TestCaseDataSchemaGenerationBaseExpectedExtraInfo

    expected_output: str


TestCaseData = Union[TestCaseDataArtifactSchemaGeneration, TestCaseDataSchemaGenerationBase]
