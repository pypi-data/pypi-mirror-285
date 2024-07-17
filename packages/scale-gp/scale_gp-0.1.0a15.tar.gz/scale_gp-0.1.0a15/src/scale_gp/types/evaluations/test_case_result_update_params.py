# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["TestCaseResultUpdateParams"]


class TestCaseResultUpdateParams(TypedDict, total=False):
    evaluation_id: Required[str]

    annotated_by_user_id: str
    """The user who annotated the task."""

    application_spec_id: str

    audit_comment: str

    audit_required: bool

    audit_status: Literal["UNAUDITED", "FIXED", "APPROVED"]
    """An enumeration."""

    evaluation_dataset_version_num: str

    result: object

    test_case_evaluation_data: object

    test_case_evaluation_data_schema: Literal["GENERATION"]
    """An enumeration."""

    test_case_id: str

    time_spent_labeling_s: int
    """The time spent labeling in seconds."""
