# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypedDict

__all__ = ["EvaluationUpdateParams", "PartialPatchEvaluationRequest", "RestoreRequest"]


class PartialPatchEvaluationRequest(TypedDict, total=False):
    application_spec_id: str

    application_variant_id: str

    description: str

    evaluation_config: object

    evaluation_config_id: str
    """The ID of the associated evaluation config."""

    evaluation_type: Literal["llm_benchmark"]
    """
    If llm_benchmark is provided, the evaluation will be updated to a hybrid
    evaluation. No-op on existing hybrid evaluations, and not available for studio
    evaluations.
    """

    name: str

    restore: Literal[False]
    """Set to true to restore the entity from the database."""

    tags: object


class RestoreRequest(TypedDict, total=False):
    restore: Required[Literal[True]]
    """Set to true to restore the entity from the database."""


EvaluationUpdateParams = Union[PartialPatchEvaluationRequest, RestoreRequest]
