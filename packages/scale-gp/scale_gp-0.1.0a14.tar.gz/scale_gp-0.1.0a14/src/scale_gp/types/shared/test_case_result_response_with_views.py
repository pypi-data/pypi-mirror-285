# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from ..._models import BaseModel
from .test_case_result_response import TestCaseResultResponse
from .test_case_version_response import TestCaseVersionResponse

__all__ = [
    "TestCaseResultResponseWithViews",
    "AnnotationResult",
    "AnnotationResultLlmAutoEvalMetadata",
    "Task",
    "TaskAssignedTo",
]


class AnnotationResultLlmAutoEvalMetadata(BaseModel):
    annotation_result_id: str
    """The ID of the associated annotation result."""

    completion_tokens: int

    llm_reasoning: str
    """The reasoning the LLM gave for the annotation it provided."""

    prompt_tokens: int

    time_elapsed_s: int
    """The time elapsed to generate this annotation in seconds."""

    cost: Optional[int] = None
    """The cost of the annotation in cents."""


class AnnotationResult(BaseModel):
    id: str
    """The unique identifier of the entity."""

    annotation_type: Literal["llm_auto", "human"]
    """An enumeration."""

    created_at: datetime
    """The date and time when the entity was created in ISO format."""

    question_id: str

    selected_choice: object
    """The selected choices(s) for the annotation result, in JSON form.

    For categorical questions, this is an object or list of objects (depending on if
    multiple selections are allowed). For free text questions, this is a string.
    """

    test_case_result_lineage_id: str

    llm_auto_eval_metadata: Optional[AnnotationResultLlmAutoEvalMetadata] = None


class TaskAssignedTo(BaseModel):
    id: str

    email: str

    first_name: Optional[str] = None

    last_name: Optional[str] = None


class Task(BaseModel):
    id: str

    account_id: str
    """The ID of the account that owns the given entity."""

    priority: int

    status: Literal["PENDING", "COMPLETED"]
    """An enumeration."""

    task_entity_id: str

    task_entity_parent_id: str

    task_type: Literal["EVALUATION_ANNOTATION"]
    """An enumeration."""

    assigned_to: Optional[TaskAssignedTo] = None

    assignment_expires_at: Optional[datetime] = None
    """The date and time when the task assignment expires in ISO format."""

    task_entity: Optional[TestCaseResultResponse] = None
    """The entity that the task is associated with."""


class TestCaseResultResponseWithViews(BaseModel):
    __test__ = False
    id: str
    """The unique identifier of the entity."""

    account_id: str
    """The ID of the account that owns the given entity."""

    application_spec_id: str

    created_at: datetime
    """The date and time when the entity was created in ISO format."""

    created_by_user_id: str
    """The user who originally created the entity."""

    evaluation_dataset_id: str

    evaluation_dataset_version_num: str

    evaluation_id: str

    label_status: Literal["PENDING", "COMPLETED", "FAILED"]
    """An enumeration."""

    test_case_evaluation_data: object

    test_case_evaluation_data_schema: Literal["GENERATION"]
    """An enumeration."""

    test_case_id: str

    annotated_by_user_id: Optional[str] = None
    """The user who annotated the task."""

    annotation_results: Optional[List[AnnotationResult]] = None

    archived_at: Optional[datetime] = None
    """The date and time when the entity was archived in ISO format."""

    audit_comment: Optional[str] = None

    audit_required: Optional[bool] = None

    audit_status: Optional[Literal["UNAUDITED", "FIXED", "APPROVED"]] = None
    """An enumeration."""

    completed_at: Optional[datetime] = None

    result: Optional[object] = None

    task: Optional[Task] = None

    test_case_version: Optional[TestCaseVersionResponse] = None

    time_spent_labeling_s: Optional[int] = None
    """The time spent labeling in seconds."""
