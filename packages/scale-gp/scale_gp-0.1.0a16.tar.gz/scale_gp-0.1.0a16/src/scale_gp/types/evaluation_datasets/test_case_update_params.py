# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = [
    "TestCaseUpdateParams",
    "PartialTestCaseVersionRequest",
    "PartialTestCaseVersionRequestTestCaseData",
    "PartialTestCaseVersionRequestTestCaseDataArtifactSchemaGeneration",
    "PartialTestCaseVersionRequestTestCaseDataArtifactSchemaGenerationExpectedExtraInfo",
    "PartialTestCaseVersionRequestTestCaseDataArtifactSchemaGenerationExpectedExtraInfoChunkExtraInfoSchema",
    "PartialTestCaseVersionRequestTestCaseDataArtifactSchemaGenerationExpectedExtraInfoChunkExtraInfoSchemaChunk",
    "PartialTestCaseVersionRequestTestCaseDataArtifactSchemaGenerationExpectedExtraInfoStringExtraInfoSchema",
    "PartialTestCaseVersionRequestTestCaseDataSchemaGenerationBase",
    "PartialTestCaseVersionRequestTestCaseDataSchemaGenerationBaseExpectedExtraInfo",
    "PartialTestCaseVersionRequestTestCaseDataSchemaGenerationBaseExpectedExtraInfoChunkExtraInfoSchema",
    "PartialTestCaseVersionRequestTestCaseDataSchemaGenerationBaseExpectedExtraInfoChunkExtraInfoSchemaChunk",
    "PartialTestCaseVersionRequestTestCaseDataSchemaGenerationBaseExpectedExtraInfoStringExtraInfoSchema",
    "RestoreRequest",
]


class PartialTestCaseVersionRequest(TypedDict, total=False):
    evaluation_dataset_id: Required[str]

    chat_history: object
    """Used for tracking previous chat interactions for multi-chat test cases"""

    restore: Literal[False]
    """Set to true to restore the entity from the database."""

    schema_type: Literal["GENERATION"]
    """An enumeration."""

    test_case_data: PartialTestCaseVersionRequestTestCaseData
    """The data for the test case in a format matching the provided schema_type"""

    test_case_metadata: object
    """Metadata for the test case"""


class PartialTestCaseVersionRequestTestCaseDataArtifactSchemaGenerationExpectedExtraInfoChunkExtraInfoSchemaChunk(
    TypedDict, total=False
):
    metadata: Required[object]

    text: Required[str]


class PartialTestCaseVersionRequestTestCaseDataArtifactSchemaGenerationExpectedExtraInfoChunkExtraInfoSchema(
    TypedDict, total=False
):
    chunks: Required[
        Iterable[
            PartialTestCaseVersionRequestTestCaseDataArtifactSchemaGenerationExpectedExtraInfoChunkExtraInfoSchemaChunk
        ]
    ]

    schema_type: Literal["CHUNKS"]


class PartialTestCaseVersionRequestTestCaseDataArtifactSchemaGenerationExpectedExtraInfoStringExtraInfoSchema(
    TypedDict, total=False
):
    info: Required[str]

    schema_type: Literal["STRING"]


PartialTestCaseVersionRequestTestCaseDataArtifactSchemaGenerationExpectedExtraInfo = Union[
    PartialTestCaseVersionRequestTestCaseDataArtifactSchemaGenerationExpectedExtraInfoChunkExtraInfoSchema,
    PartialTestCaseVersionRequestTestCaseDataArtifactSchemaGenerationExpectedExtraInfoStringExtraInfoSchema,
]


class PartialTestCaseVersionRequestTestCaseDataArtifactSchemaGeneration(TypedDict, total=False):
    artifact_ids_filter: Required[List[str]]

    input: Required[str]

    expected_extra_info: PartialTestCaseVersionRequestTestCaseDataArtifactSchemaGenerationExpectedExtraInfo

    expected_output: str


class PartialTestCaseVersionRequestTestCaseDataSchemaGenerationBaseExpectedExtraInfoChunkExtraInfoSchemaChunk(
    TypedDict, total=False
):
    metadata: Required[object]

    text: Required[str]


class PartialTestCaseVersionRequestTestCaseDataSchemaGenerationBaseExpectedExtraInfoChunkExtraInfoSchema(
    TypedDict, total=False
):
    chunks: Required[
        Iterable[
            PartialTestCaseVersionRequestTestCaseDataSchemaGenerationBaseExpectedExtraInfoChunkExtraInfoSchemaChunk
        ]
    ]

    schema_type: Literal["CHUNKS"]


class PartialTestCaseVersionRequestTestCaseDataSchemaGenerationBaseExpectedExtraInfoStringExtraInfoSchema(
    TypedDict, total=False
):
    info: Required[str]

    schema_type: Literal["STRING"]


PartialTestCaseVersionRequestTestCaseDataSchemaGenerationBaseExpectedExtraInfo = Union[
    PartialTestCaseVersionRequestTestCaseDataSchemaGenerationBaseExpectedExtraInfoChunkExtraInfoSchema,
    PartialTestCaseVersionRequestTestCaseDataSchemaGenerationBaseExpectedExtraInfoStringExtraInfoSchema,
]


class PartialTestCaseVersionRequestTestCaseDataSchemaGenerationBase(TypedDict, total=False):
    input: Required[str]

    expected_extra_info: PartialTestCaseVersionRequestTestCaseDataSchemaGenerationBaseExpectedExtraInfo

    expected_output: str


PartialTestCaseVersionRequestTestCaseData = Union[
    PartialTestCaseVersionRequestTestCaseDataArtifactSchemaGeneration,
    PartialTestCaseVersionRequestTestCaseDataSchemaGenerationBase,
]


class RestoreRequest(TypedDict, total=False):
    evaluation_dataset_id: Required[str]

    restore: Required[Literal[True]]
    """Set to true to restore the entity from the database."""


TestCaseUpdateParams = Union[PartialTestCaseVersionRequest, RestoreRequest]
