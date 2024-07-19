# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .events import (
    EventsResource,
    AsyncEventsResource,
    EventsResourceWithRawResponse,
    AsyncEventsResourceWithRawResponse,
    EventsResourceWithStreamingResponse,
    AsyncEventsResourceWithStreamingResponse,
)
from ...types import fine_tuning_job_list_params, fine_tuning_job_create_params
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
from ...types.shared.delete_response import DeleteResponse
from ...types.fine_tuning_job_response import FineTuningJobResponse
from ...types.pagination_response_list_egp_api_backend_server_api_models_fine_tuning_job_models_fine_tuning_job_response import (
    PaginationResponseListEgpAPIBackendServerAPIModelsFineTuningJobModelsFineTuningJobResponse,
)

__all__ = ["FineTuningJobsResource", "AsyncFineTuningJobsResource"]


class FineTuningJobsResource(SyncAPIResource):
    @cached_property
    def events(self) -> EventsResource:
        return EventsResource(self._client)

    @cached_property
    def with_raw_response(self) -> FineTuningJobsResourceWithRawResponse:
        return FineTuningJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FineTuningJobsResourceWithStreamingResponse:
        return FineTuningJobsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        account_id: str,
        training_dataset_id: str,
        base_model_id: str | NotGiven = NOT_GIVEN,
        fine_tuned_model_id: str | NotGiven = NOT_GIVEN,
        validation_dataset_id: str | NotGiven = NOT_GIVEN,
        vendor_configuration: fine_tuning_job_create_params.VendorConfiguration | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FineTuningJobResponse:
        """
        ### Description

        Model fine tuning jobs.

        ### Details

        TODO

        Args:
          account_id: The ID of the account that owns the given entity.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v4/fine-tuning-jobs",
            body=maybe_transform(
                {
                    "account_id": account_id,
                    "training_dataset_id": training_dataset_id,
                    "base_model_id": base_model_id,
                    "fine_tuned_model_id": fine_tuned_model_id,
                    "validation_dataset_id": validation_dataset_id,
                    "vendor_configuration": vendor_configuration,
                },
                fine_tuning_job_create_params.FineTuningJobCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuningJobResponse,
        )

    def retrieve(
        self,
        fine_tuning_job_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FineTuningJobResponse:
        """
        ### Description

        Gets the details of a fine tuning job

        ### Details

        This API can be used to get information about a single fine tuning job by ID. To
        use this API, pass in the `id` that was returned from your Create Fine Tuning
        Job API call as a path parameter.

        Review the response schema to see the fields that will be returned.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not fine_tuning_job_id:
            raise ValueError(f"Expected a non-empty value for `fine_tuning_job_id` but received {fine_tuning_job_id!r}")
        return self._get(
            f"/v4/fine-tuning-jobs/{fine_tuning_job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuningJobResponse,
        )

    def list(
        self,
        *,
        account_id: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PaginationResponseListEgpAPIBackendServerAPIModelsFineTuningJobModelsFineTuningJobResponse:
        """
        ### Description

        Lists all fine tuning jobs accessible to the user.

        ### Details

        This API can be used to list fine tuning jobs. If a user has access to multiple
        accounts, all fine tuning jobs from all accounts the user is associated with
        will be returned.

        Args:
          limit: Maximum number of artifacts to be returned by the given endpoint. Defaults to
              100 and cannot be greater than 10k.

          page: Page number for pagination to be returned by the given endpoint. Starts at page
              1

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v4/fine-tuning-jobs",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "account_id": account_id,
                        "limit": limit,
                        "page": page,
                    },
                    fine_tuning_job_list_params.FineTuningJobListParams,
                ),
            ),
            cast_to=PaginationResponseListEgpAPIBackendServerAPIModelsFineTuningJobModelsFineTuningJobResponse,
        )

    def delete(
        self,
        fine_tuning_job_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeleteResponse:
        """
        ### Description

        Deletes a fine tuning job

        ### Details

        This API can be used to delete a fine tuning job by ID. To use this API, pass in
        the `id` that was returned from your Create Fine Tuning Job API call as a path
        parameter.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not fine_tuning_job_id:
            raise ValueError(f"Expected a non-empty value for `fine_tuning_job_id` but received {fine_tuning_job_id!r}")
        return self._delete(
            f"/v4/fine-tuning-jobs/{fine_tuning_job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )


class AsyncFineTuningJobsResource(AsyncAPIResource):
    @cached_property
    def events(self) -> AsyncEventsResource:
        return AsyncEventsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncFineTuningJobsResourceWithRawResponse:
        return AsyncFineTuningJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFineTuningJobsResourceWithStreamingResponse:
        return AsyncFineTuningJobsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        account_id: str,
        training_dataset_id: str,
        base_model_id: str | NotGiven = NOT_GIVEN,
        fine_tuned_model_id: str | NotGiven = NOT_GIVEN,
        validation_dataset_id: str | NotGiven = NOT_GIVEN,
        vendor_configuration: fine_tuning_job_create_params.VendorConfiguration | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FineTuningJobResponse:
        """
        ### Description

        Model fine tuning jobs.

        ### Details

        TODO

        Args:
          account_id: The ID of the account that owns the given entity.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v4/fine-tuning-jobs",
            body=await async_maybe_transform(
                {
                    "account_id": account_id,
                    "training_dataset_id": training_dataset_id,
                    "base_model_id": base_model_id,
                    "fine_tuned_model_id": fine_tuned_model_id,
                    "validation_dataset_id": validation_dataset_id,
                    "vendor_configuration": vendor_configuration,
                },
                fine_tuning_job_create_params.FineTuningJobCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuningJobResponse,
        )

    async def retrieve(
        self,
        fine_tuning_job_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FineTuningJobResponse:
        """
        ### Description

        Gets the details of a fine tuning job

        ### Details

        This API can be used to get information about a single fine tuning job by ID. To
        use this API, pass in the `id` that was returned from your Create Fine Tuning
        Job API call as a path parameter.

        Review the response schema to see the fields that will be returned.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not fine_tuning_job_id:
            raise ValueError(f"Expected a non-empty value for `fine_tuning_job_id` but received {fine_tuning_job_id!r}")
        return await self._get(
            f"/v4/fine-tuning-jobs/{fine_tuning_job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuningJobResponse,
        )

    async def list(
        self,
        *,
        account_id: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PaginationResponseListEgpAPIBackendServerAPIModelsFineTuningJobModelsFineTuningJobResponse:
        """
        ### Description

        Lists all fine tuning jobs accessible to the user.

        ### Details

        This API can be used to list fine tuning jobs. If a user has access to multiple
        accounts, all fine tuning jobs from all accounts the user is associated with
        will be returned.

        Args:
          limit: Maximum number of artifacts to be returned by the given endpoint. Defaults to
              100 and cannot be greater than 10k.

          page: Page number for pagination to be returned by the given endpoint. Starts at page
              1

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v4/fine-tuning-jobs",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "account_id": account_id,
                        "limit": limit,
                        "page": page,
                    },
                    fine_tuning_job_list_params.FineTuningJobListParams,
                ),
            ),
            cast_to=PaginationResponseListEgpAPIBackendServerAPIModelsFineTuningJobModelsFineTuningJobResponse,
        )

    async def delete(
        self,
        fine_tuning_job_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeleteResponse:
        """
        ### Description

        Deletes a fine tuning job

        ### Details

        This API can be used to delete a fine tuning job by ID. To use this API, pass in
        the `id` that was returned from your Create Fine Tuning Job API call as a path
        parameter.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not fine_tuning_job_id:
            raise ValueError(f"Expected a non-empty value for `fine_tuning_job_id` but received {fine_tuning_job_id!r}")
        return await self._delete(
            f"/v4/fine-tuning-jobs/{fine_tuning_job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )


class FineTuningJobsResourceWithRawResponse:
    def __init__(self, fine_tuning_jobs: FineTuningJobsResource) -> None:
        self._fine_tuning_jobs = fine_tuning_jobs

        self.create = to_raw_response_wrapper(
            fine_tuning_jobs.create,
        )
        self.retrieve = to_raw_response_wrapper(
            fine_tuning_jobs.retrieve,
        )
        self.list = to_raw_response_wrapper(
            fine_tuning_jobs.list,
        )
        self.delete = to_raw_response_wrapper(
            fine_tuning_jobs.delete,
        )

    @cached_property
    def events(self) -> EventsResourceWithRawResponse:
        return EventsResourceWithRawResponse(self._fine_tuning_jobs.events)


class AsyncFineTuningJobsResourceWithRawResponse:
    def __init__(self, fine_tuning_jobs: AsyncFineTuningJobsResource) -> None:
        self._fine_tuning_jobs = fine_tuning_jobs

        self.create = async_to_raw_response_wrapper(
            fine_tuning_jobs.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            fine_tuning_jobs.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            fine_tuning_jobs.list,
        )
        self.delete = async_to_raw_response_wrapper(
            fine_tuning_jobs.delete,
        )

    @cached_property
    def events(self) -> AsyncEventsResourceWithRawResponse:
        return AsyncEventsResourceWithRawResponse(self._fine_tuning_jobs.events)


class FineTuningJobsResourceWithStreamingResponse:
    def __init__(self, fine_tuning_jobs: FineTuningJobsResource) -> None:
        self._fine_tuning_jobs = fine_tuning_jobs

        self.create = to_streamed_response_wrapper(
            fine_tuning_jobs.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            fine_tuning_jobs.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            fine_tuning_jobs.list,
        )
        self.delete = to_streamed_response_wrapper(
            fine_tuning_jobs.delete,
        )

    @cached_property
    def events(self) -> EventsResourceWithStreamingResponse:
        return EventsResourceWithStreamingResponse(self._fine_tuning_jobs.events)


class AsyncFineTuningJobsResourceWithStreamingResponse:
    def __init__(self, fine_tuning_jobs: AsyncFineTuningJobsResource) -> None:
        self._fine_tuning_jobs = fine_tuning_jobs

        self.create = async_to_streamed_response_wrapper(
            fine_tuning_jobs.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            fine_tuning_jobs.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            fine_tuning_jobs.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            fine_tuning_jobs.delete,
        )

    @cached_property
    def events(self) -> AsyncEventsResourceWithStreamingResponse:
        return AsyncEventsResourceWithStreamingResponse(self._fine_tuning_jobs.events)
