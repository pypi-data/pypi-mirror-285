# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel
from .training_dataset_response import TrainingDatasetResponse

__all__ = ["PaginationResponseListEgpAPIBackendServerAPIModelsFineTuningJobModelsTrainingDatasetResponse"]


class PaginationResponseListEgpAPIBackendServerAPIModelsFineTuningJobModelsTrainingDatasetResponse(BaseModel):
    current_page: int
    """The current page number."""

    items: List[TrainingDatasetResponse]
    """The data returned for the current page."""

    items_per_page: int
    """The number of items per page."""

    total_item_count: int
    """The total number of items of the query"""
