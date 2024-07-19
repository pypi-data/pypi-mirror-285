# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Iterable
from typing_extensions import Literal

import httpx

from ..types import (
    application_test_case_output_list_params,
    application_test_case_output_batch_params,
    application_test_case_output_create_params,
    application_test_case_output_retrieve_params,
)
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import (
    maybe_transform,
    async_maybe_transform,
)
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.application_test_case_output import ApplicationTestCaseOutput
from ..types.application_test_case_output_list_response import ApplicationTestCaseOutputListResponse
from ..types.application_test_case_output_batch_response import ApplicationTestCaseOutputBatchResponse
from ..types.application_test_case_output_create_response import ApplicationTestCaseOutputCreateResponse

__all__ = ["ApplicationTestCaseOutputsResource", "AsyncApplicationTestCaseOutputsResource"]


class ApplicationTestCaseOutputsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ApplicationTestCaseOutputsResourceWithRawResponse:
        return ApplicationTestCaseOutputsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ApplicationTestCaseOutputsResourceWithStreamingResponse:
        return ApplicationTestCaseOutputsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        account_id: str,
        application_variant_id: str,
        evaluation_dataset_version_num: int,
        output: application_test_case_output_create_params.Output,
        schema_type: Literal["GENERATION"],
        test_case_id: str,
        application_interaction_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationTestCaseOutputCreateResponse:
        """
        ### Description

        Creates a application test case output

        ### Details

        This API can be used to create a application test case output. To use this API,
        review the request schema and pass in all fields that are required to create a
        application test case output.

        Args:
          account_id: The ID of the account that owns the given entity.

          schema_type: An enumeration.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v4/application-test-case-outputs",
            body=maybe_transform(
                {
                    "account_id": account_id,
                    "application_variant_id": application_variant_id,
                    "evaluation_dataset_version_num": evaluation_dataset_version_num,
                    "output": output,
                    "schema_type": schema_type,
                    "test_case_id": test_case_id,
                    "application_interaction_id": application_interaction_id,
                },
                application_test_case_output_create_params.ApplicationTestCaseOutputCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApplicationTestCaseOutputCreateResponse,
        )

    def retrieve(
        self,
        application_test_case_output_id: str,
        *,
        view: List[Literal["MetricScores", "TestCaseVersion", "Trace"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationTestCaseOutput:
        """
        ### Description

        Gets the details of a application test case output

        ### Details

        This API can be used to get information about a single application test case
        output by ID. To use this API, pass in the `id` that was returned from your
        Create Application Test Case Output API call as a path parameter.

        Review the response schema to see the fields that will be returned.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not application_test_case_output_id:
            raise ValueError(
                f"Expected a non-empty value for `application_test_case_output_id` but received {application_test_case_output_id!r}"
            )
        return self._get(
            f"/v4/application-test-case-outputs/{application_test_case_output_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"view": view}, application_test_case_output_retrieve_params.ApplicationTestCaseOutputRetrieveParams
                ),
            ),
            cast_to=ApplicationTestCaseOutput,
        )

    def list(
        self,
        *,
        account_id: str | NotGiven = NOT_GIVEN,
        application_variant_id: Union[int, str] | NotGiven = NOT_GIVEN,
        application_variant_report_id: Union[int, str] | NotGiven = NOT_GIVEN,
        evaluation_dataset_id: Union[int, str] | NotGiven = NOT_GIVEN,
        evaluation_dataset_version_num: Union[int, str] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        view: List[Literal["MetricScores", "TestCaseVersion", "Trace"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationTestCaseOutputListResponse:
        """
        ### Description

        Lists all application test case outputs accessible to the user.

        ### Details

        This API can be used to list application test case outputs. If a user has access
        to multiple accounts, all application test case outputs from all accounts the
        user is associated with will be returned.

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
            "/v4/application-test-case-outputs",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "account_id": account_id,
                        "application_variant_id": application_variant_id,
                        "application_variant_report_id": application_variant_report_id,
                        "evaluation_dataset_id": evaluation_dataset_id,
                        "evaluation_dataset_version_num": evaluation_dataset_version_num,
                        "limit": limit,
                        "page": page,
                        "view": view,
                    },
                    application_test_case_output_list_params.ApplicationTestCaseOutputListParams,
                ),
            ),
            cast_to=ApplicationTestCaseOutputListResponse,
        )

    def batch(
        self,
        *,
        body: Iterable[application_test_case_output_batch_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationTestCaseOutputBatchResponse:
        """
        ### Description

        Creates a batch of application test case outputs

        ### Details

        This API can be used to create multiple application test case outputs so users
        do not have to the incur the cost of repeated network calls. To use this API,
        pass in a list of application test case outputs in the request body.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v4/application-test-case-outputs/batch",
            body=maybe_transform(body, application_test_case_output_batch_params.ApplicationTestCaseOutputBatchParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApplicationTestCaseOutputBatchResponse,
        )


class AsyncApplicationTestCaseOutputsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncApplicationTestCaseOutputsResourceWithRawResponse:
        return AsyncApplicationTestCaseOutputsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncApplicationTestCaseOutputsResourceWithStreamingResponse:
        return AsyncApplicationTestCaseOutputsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        account_id: str,
        application_variant_id: str,
        evaluation_dataset_version_num: int,
        output: application_test_case_output_create_params.Output,
        schema_type: Literal["GENERATION"],
        test_case_id: str,
        application_interaction_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationTestCaseOutputCreateResponse:
        """
        ### Description

        Creates a application test case output

        ### Details

        This API can be used to create a application test case output. To use this API,
        review the request schema and pass in all fields that are required to create a
        application test case output.

        Args:
          account_id: The ID of the account that owns the given entity.

          schema_type: An enumeration.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v4/application-test-case-outputs",
            body=await async_maybe_transform(
                {
                    "account_id": account_id,
                    "application_variant_id": application_variant_id,
                    "evaluation_dataset_version_num": evaluation_dataset_version_num,
                    "output": output,
                    "schema_type": schema_type,
                    "test_case_id": test_case_id,
                    "application_interaction_id": application_interaction_id,
                },
                application_test_case_output_create_params.ApplicationTestCaseOutputCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApplicationTestCaseOutputCreateResponse,
        )

    async def retrieve(
        self,
        application_test_case_output_id: str,
        *,
        view: List[Literal["MetricScores", "TestCaseVersion", "Trace"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationTestCaseOutput:
        """
        ### Description

        Gets the details of a application test case output

        ### Details

        This API can be used to get information about a single application test case
        output by ID. To use this API, pass in the `id` that was returned from your
        Create Application Test Case Output API call as a path parameter.

        Review the response schema to see the fields that will be returned.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not application_test_case_output_id:
            raise ValueError(
                f"Expected a non-empty value for `application_test_case_output_id` but received {application_test_case_output_id!r}"
            )
        return await self._get(
            f"/v4/application-test-case-outputs/{application_test_case_output_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"view": view}, application_test_case_output_retrieve_params.ApplicationTestCaseOutputRetrieveParams
                ),
            ),
            cast_to=ApplicationTestCaseOutput,
        )

    async def list(
        self,
        *,
        account_id: str | NotGiven = NOT_GIVEN,
        application_variant_id: Union[int, str] | NotGiven = NOT_GIVEN,
        application_variant_report_id: Union[int, str] | NotGiven = NOT_GIVEN,
        evaluation_dataset_id: Union[int, str] | NotGiven = NOT_GIVEN,
        evaluation_dataset_version_num: Union[int, str] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        view: List[Literal["MetricScores", "TestCaseVersion", "Trace"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationTestCaseOutputListResponse:
        """
        ### Description

        Lists all application test case outputs accessible to the user.

        ### Details

        This API can be used to list application test case outputs. If a user has access
        to multiple accounts, all application test case outputs from all accounts the
        user is associated with will be returned.

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
            "/v4/application-test-case-outputs",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "account_id": account_id,
                        "application_variant_id": application_variant_id,
                        "application_variant_report_id": application_variant_report_id,
                        "evaluation_dataset_id": evaluation_dataset_id,
                        "evaluation_dataset_version_num": evaluation_dataset_version_num,
                        "limit": limit,
                        "page": page,
                        "view": view,
                    },
                    application_test_case_output_list_params.ApplicationTestCaseOutputListParams,
                ),
            ),
            cast_to=ApplicationTestCaseOutputListResponse,
        )

    async def batch(
        self,
        *,
        body: Iterable[application_test_case_output_batch_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationTestCaseOutputBatchResponse:
        """
        ### Description

        Creates a batch of application test case outputs

        ### Details

        This API can be used to create multiple application test case outputs so users
        do not have to the incur the cost of repeated network calls. To use this API,
        pass in a list of application test case outputs in the request body.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v4/application-test-case-outputs/batch",
            body=await async_maybe_transform(
                body, application_test_case_output_batch_params.ApplicationTestCaseOutputBatchParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApplicationTestCaseOutputBatchResponse,
        )


class ApplicationTestCaseOutputsResourceWithRawResponse:
    def __init__(self, application_test_case_outputs: ApplicationTestCaseOutputsResource) -> None:
        self._application_test_case_outputs = application_test_case_outputs

        self.create = to_raw_response_wrapper(
            application_test_case_outputs.create,
        )
        self.retrieve = to_raw_response_wrapper(
            application_test_case_outputs.retrieve,
        )
        self.list = to_raw_response_wrapper(
            application_test_case_outputs.list,
        )
        self.batch = to_raw_response_wrapper(
            application_test_case_outputs.batch,
        )


class AsyncApplicationTestCaseOutputsResourceWithRawResponse:
    def __init__(self, application_test_case_outputs: AsyncApplicationTestCaseOutputsResource) -> None:
        self._application_test_case_outputs = application_test_case_outputs

        self.create = async_to_raw_response_wrapper(
            application_test_case_outputs.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            application_test_case_outputs.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            application_test_case_outputs.list,
        )
        self.batch = async_to_raw_response_wrapper(
            application_test_case_outputs.batch,
        )


class ApplicationTestCaseOutputsResourceWithStreamingResponse:
    def __init__(self, application_test_case_outputs: ApplicationTestCaseOutputsResource) -> None:
        self._application_test_case_outputs = application_test_case_outputs

        self.create = to_streamed_response_wrapper(
            application_test_case_outputs.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            application_test_case_outputs.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            application_test_case_outputs.list,
        )
        self.batch = to_streamed_response_wrapper(
            application_test_case_outputs.batch,
        )


class AsyncApplicationTestCaseOutputsResourceWithStreamingResponse:
    def __init__(self, application_test_case_outputs: AsyncApplicationTestCaseOutputsResource) -> None:
        self._application_test_case_outputs = application_test_case_outputs

        self.create = async_to_streamed_response_wrapper(
            application_test_case_outputs.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            application_test_case_outputs.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            application_test_case_outputs.list,
        )
        self.batch = async_to_streamed_response_wrapper(
            application_test_case_outputs.batch,
        )
