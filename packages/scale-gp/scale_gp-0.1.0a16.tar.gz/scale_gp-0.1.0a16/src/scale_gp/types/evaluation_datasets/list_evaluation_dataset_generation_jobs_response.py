# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ..._models import BaseModel
from .get_evaluation_dataset_generation_job_response import GetEvaluationDatasetGenerationJobResponse

__all__ = ["ListEvaluationDatasetGenerationJobsResponse"]


class ListEvaluationDatasetGenerationJobsResponse(BaseModel):
    generation_jobs: List[GetEvaluationDatasetGenerationJobResponse]
    """List of evaluation dataset generation jobs."""
