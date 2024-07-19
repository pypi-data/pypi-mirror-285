# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = [
    "ApplicationTestCaseOutputCreateParams",
    "Output",
    "OutputGenerationExtraInfo",
    "OutputGenerationExtraInfoChunkExtraInfoSchema",
    "OutputGenerationExtraInfoChunkExtraInfoSchemaChunk",
    "OutputGenerationExtraInfoStringExtraInfoSchema",
]


class ApplicationTestCaseOutputCreateParams(TypedDict, total=False):
    account_id: Required[str]
    """The ID of the account that owns the given entity."""

    application_variant_id: Required[str]

    evaluation_dataset_version_num: Required[int]

    output: Required[Output]

    schema_type: Required[Literal["GENERATION"]]
    """An enumeration."""

    test_case_id: Required[str]

    application_interaction_id: str


class OutputGenerationExtraInfoChunkExtraInfoSchemaChunk(TypedDict, total=False):
    metadata: Required[object]

    text: Required[str]


class OutputGenerationExtraInfoChunkExtraInfoSchema(TypedDict, total=False):
    chunks: Required[Iterable[OutputGenerationExtraInfoChunkExtraInfoSchemaChunk]]

    schema_type: Literal["CHUNKS"]


class OutputGenerationExtraInfoStringExtraInfoSchema(TypedDict, total=False):
    info: Required[str]

    schema_type: Literal["STRING"]


OutputGenerationExtraInfo = Union[
    OutputGenerationExtraInfoChunkExtraInfoSchema, OutputGenerationExtraInfoStringExtraInfoSchema
]


class Output(TypedDict, total=False):
    generation_output: Required[str]

    generation_extra_info: OutputGenerationExtraInfo
