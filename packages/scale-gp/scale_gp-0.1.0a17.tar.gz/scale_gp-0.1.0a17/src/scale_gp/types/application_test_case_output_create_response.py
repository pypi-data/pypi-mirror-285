# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, Annotated

from .._utils import PropertyInfo
from .._models import BaseModel

__all__ = [
    "ApplicationTestCaseOutputCreateResponse",
    "Output",
    "OutputGenerationExtraInfo",
    "OutputGenerationExtraInfoChunkExtraInfoSchema",
    "OutputGenerationExtraInfoChunkExtraInfoSchemaChunk",
    "OutputGenerationExtraInfoStringExtraInfoSchema",
]


class OutputGenerationExtraInfoChunkExtraInfoSchemaChunk(BaseModel):
    metadata: object

    text: str


class OutputGenerationExtraInfoChunkExtraInfoSchema(BaseModel):
    chunks: List[OutputGenerationExtraInfoChunkExtraInfoSchemaChunk]

    schema_type: Optional[Literal["CHUNKS"]] = None


class OutputGenerationExtraInfoStringExtraInfoSchema(BaseModel):
    info: str

    schema_type: Optional[Literal["STRING"]] = None


OutputGenerationExtraInfo = Annotated[
    Union[OutputGenerationExtraInfoChunkExtraInfoSchema, OutputGenerationExtraInfoStringExtraInfoSchema],
    PropertyInfo(discriminator="schema_type"),
]


class Output(BaseModel):
    generation_output: str

    generation_extra_info: Optional[OutputGenerationExtraInfo] = None


class ApplicationTestCaseOutputCreateResponse(BaseModel):
    id: str
    """The unique identifier of the entity."""

    account_id: str
    """The ID of the account that owns the given entity."""

    application_variant_id: str

    created_at: datetime
    """The date and time when the entity was created in ISO format."""

    evaluation_dataset_id: str

    output: Output

    schema_type: Literal["GENERATION"]
    """An enumeration."""

    test_case_id: str

    application_interaction_id: Optional[str] = None
