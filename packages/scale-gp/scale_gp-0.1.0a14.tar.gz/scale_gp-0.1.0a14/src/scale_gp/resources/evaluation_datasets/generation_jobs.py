# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import (
    maybe_transform,
    async_maybe_transform,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.evaluation_datasets import generation_job_create_params
from ...types.evaluation_datasets.get_evaluation_dataset_generation_job_response import (
    GetEvaluationDatasetGenerationJobResponse,
)
from ...types.evaluation_datasets.list_evaluation_dataset_generation_jobs_response import (
    ListEvaluationDatasetGenerationJobsResponse,
)
from ...types.evaluation_datasets.create_evaluation_dataset_generation_job_response import (
    CreateEvaluationDatasetGenerationJobResponse,
)

__all__ = ["GenerationJobsResource", "AsyncGenerationJobsResource"]


class GenerationJobsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> GenerationJobsResourceWithRawResponse:
        return GenerationJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> GenerationJobsResourceWithStreamingResponse:
        return GenerationJobsResourceWithStreamingResponse(self)

    def create(
        self,
        evaluation_dataset_id: str,
        *,
        group_by_artifact_id: bool | NotGiven = NOT_GIVEN,
        num_test_cases: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CreateEvaluationDatasetGenerationJobResponse:
        """
        Create Evaluation Dataset Generation Job

        Args:
          group_by_artifact_id: If this flag is true, for every generated test case, the chunks used to generate
              it will be guaranteed to be from the same document (artifact).

          num_test_cases: Number of test cases to generate for the evaluation dataset

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not evaluation_dataset_id:
            raise ValueError(
                f"Expected a non-empty value for `evaluation_dataset_id` but received {evaluation_dataset_id!r}"
            )
        return self._post(
            f"/v4/evaluation-datasets/{evaluation_dataset_id}/generation-jobs",
            body=maybe_transform(
                {
                    "group_by_artifact_id": group_by_artifact_id,
                    "num_test_cases": num_test_cases,
                },
                generation_job_create_params.GenerationJobCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CreateEvaluationDatasetGenerationJobResponse,
        )

    def retrieve(
        self,
        generation_job_id: str,
        *,
        evaluation_dataset_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GetEvaluationDatasetGenerationJobResponse:
        """
        Get Evaluation Dataset Generation Job

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not evaluation_dataset_id:
            raise ValueError(
                f"Expected a non-empty value for `evaluation_dataset_id` but received {evaluation_dataset_id!r}"
            )
        if not generation_job_id:
            raise ValueError(f"Expected a non-empty value for `generation_job_id` but received {generation_job_id!r}")
        return self._get(
            f"/v4/evaluation-datasets/{evaluation_dataset_id}/generation-jobs/{generation_job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GetEvaluationDatasetGenerationJobResponse,
        )

    def list(
        self,
        evaluation_dataset_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ListEvaluationDatasetGenerationJobsResponse:
        """
        Get Evaluation Dataset Generation Jobs

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not evaluation_dataset_id:
            raise ValueError(
                f"Expected a non-empty value for `evaluation_dataset_id` but received {evaluation_dataset_id!r}"
            )
        return self._get(
            f"/v4/evaluation-datasets/{evaluation_dataset_id}/generation-jobs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ListEvaluationDatasetGenerationJobsResponse,
        )

    def cancel(
        self,
        generation_job_id: str,
        *,
        evaluation_dataset_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Cancel Evaluation Dataset Generation Job

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not evaluation_dataset_id:
            raise ValueError(
                f"Expected a non-empty value for `evaluation_dataset_id` but received {evaluation_dataset_id!r}"
            )
        if not generation_job_id:
            raise ValueError(f"Expected a non-empty value for `generation_job_id` but received {generation_job_id!r}")
        return self._post(
            f"/v4/evaluation-datasets/{evaluation_dataset_id}/generation-jobs/{generation_job_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncGenerationJobsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncGenerationJobsResourceWithRawResponse:
        return AsyncGenerationJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncGenerationJobsResourceWithStreamingResponse:
        return AsyncGenerationJobsResourceWithStreamingResponse(self)

    async def create(
        self,
        evaluation_dataset_id: str,
        *,
        group_by_artifact_id: bool | NotGiven = NOT_GIVEN,
        num_test_cases: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CreateEvaluationDatasetGenerationJobResponse:
        """
        Create Evaluation Dataset Generation Job

        Args:
          group_by_artifact_id: If this flag is true, for every generated test case, the chunks used to generate
              it will be guaranteed to be from the same document (artifact).

          num_test_cases: Number of test cases to generate for the evaluation dataset

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not evaluation_dataset_id:
            raise ValueError(
                f"Expected a non-empty value for `evaluation_dataset_id` but received {evaluation_dataset_id!r}"
            )
        return await self._post(
            f"/v4/evaluation-datasets/{evaluation_dataset_id}/generation-jobs",
            body=await async_maybe_transform(
                {
                    "group_by_artifact_id": group_by_artifact_id,
                    "num_test_cases": num_test_cases,
                },
                generation_job_create_params.GenerationJobCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CreateEvaluationDatasetGenerationJobResponse,
        )

    async def retrieve(
        self,
        generation_job_id: str,
        *,
        evaluation_dataset_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GetEvaluationDatasetGenerationJobResponse:
        """
        Get Evaluation Dataset Generation Job

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not evaluation_dataset_id:
            raise ValueError(
                f"Expected a non-empty value for `evaluation_dataset_id` but received {evaluation_dataset_id!r}"
            )
        if not generation_job_id:
            raise ValueError(f"Expected a non-empty value for `generation_job_id` but received {generation_job_id!r}")
        return await self._get(
            f"/v4/evaluation-datasets/{evaluation_dataset_id}/generation-jobs/{generation_job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GetEvaluationDatasetGenerationJobResponse,
        )

    async def list(
        self,
        evaluation_dataset_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ListEvaluationDatasetGenerationJobsResponse:
        """
        Get Evaluation Dataset Generation Jobs

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not evaluation_dataset_id:
            raise ValueError(
                f"Expected a non-empty value for `evaluation_dataset_id` but received {evaluation_dataset_id!r}"
            )
        return await self._get(
            f"/v4/evaluation-datasets/{evaluation_dataset_id}/generation-jobs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ListEvaluationDatasetGenerationJobsResponse,
        )

    async def cancel(
        self,
        generation_job_id: str,
        *,
        evaluation_dataset_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Cancel Evaluation Dataset Generation Job

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not evaluation_dataset_id:
            raise ValueError(
                f"Expected a non-empty value for `evaluation_dataset_id` but received {evaluation_dataset_id!r}"
            )
        if not generation_job_id:
            raise ValueError(f"Expected a non-empty value for `generation_job_id` but received {generation_job_id!r}")
        return await self._post(
            f"/v4/evaluation-datasets/{evaluation_dataset_id}/generation-jobs/{generation_job_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class GenerationJobsResourceWithRawResponse:
    def __init__(self, generation_jobs: GenerationJobsResource) -> None:
        self._generation_jobs = generation_jobs

        self.create = to_raw_response_wrapper(
            generation_jobs.create,
        )
        self.retrieve = to_raw_response_wrapper(
            generation_jobs.retrieve,
        )
        self.list = to_raw_response_wrapper(
            generation_jobs.list,
        )
        self.cancel = to_raw_response_wrapper(
            generation_jobs.cancel,
        )


class AsyncGenerationJobsResourceWithRawResponse:
    def __init__(self, generation_jobs: AsyncGenerationJobsResource) -> None:
        self._generation_jobs = generation_jobs

        self.create = async_to_raw_response_wrapper(
            generation_jobs.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            generation_jobs.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            generation_jobs.list,
        )
        self.cancel = async_to_raw_response_wrapper(
            generation_jobs.cancel,
        )


class GenerationJobsResourceWithStreamingResponse:
    def __init__(self, generation_jobs: GenerationJobsResource) -> None:
        self._generation_jobs = generation_jobs

        self.create = to_streamed_response_wrapper(
            generation_jobs.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            generation_jobs.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            generation_jobs.list,
        )
        self.cancel = to_streamed_response_wrapper(
            generation_jobs.cancel,
        )


class AsyncGenerationJobsResourceWithStreamingResponse:
    def __init__(self, generation_jobs: AsyncGenerationJobsResource) -> None:
        self._generation_jobs = generation_jobs

        self.create = async_to_streamed_response_wrapper(
            generation_jobs.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            generation_jobs.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            generation_jobs.list,
        )
        self.cancel = async_to_streamed_response_wrapper(
            generation_jobs.cancel,
        )
