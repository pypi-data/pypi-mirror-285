# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

import httpx

from ..types import (
    application_test_case_output_list_params,
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

__all__ = ["ApplicationTestCaseOutputsResource", "AsyncApplicationTestCaseOutputsResource"]


class ApplicationTestCaseOutputsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ApplicationTestCaseOutputsResourceWithRawResponse:
        return ApplicationTestCaseOutputsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ApplicationTestCaseOutputsResourceWithStreamingResponse:
        return ApplicationTestCaseOutputsResourceWithStreamingResponse(self)

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
        application_variant_report_id: str | NotGiven = NOT_GIVEN,
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
                        "application_variant_report_id": application_variant_report_id,
                        "limit": limit,
                        "page": page,
                        "view": view,
                    },
                    application_test_case_output_list_params.ApplicationTestCaseOutputListParams,
                ),
            ),
            cast_to=ApplicationTestCaseOutputListResponse,
        )


class AsyncApplicationTestCaseOutputsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncApplicationTestCaseOutputsResourceWithRawResponse:
        return AsyncApplicationTestCaseOutputsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncApplicationTestCaseOutputsResourceWithStreamingResponse:
        return AsyncApplicationTestCaseOutputsResourceWithStreamingResponse(self)

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
        application_variant_report_id: str | NotGiven = NOT_GIVEN,
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
                        "application_variant_report_id": application_variant_report_id,
                        "limit": limit,
                        "page": page,
                        "view": view,
                    },
                    application_test_case_output_list_params.ApplicationTestCaseOutputListParams,
                ),
            ),
            cast_to=ApplicationTestCaseOutputListResponse,
        )


class ApplicationTestCaseOutputsResourceWithRawResponse:
    def __init__(self, application_test_case_outputs: ApplicationTestCaseOutputsResource) -> None:
        self._application_test_case_outputs = application_test_case_outputs

        self.retrieve = to_raw_response_wrapper(
            application_test_case_outputs.retrieve,
        )
        self.list = to_raw_response_wrapper(
            application_test_case_outputs.list,
        )


class AsyncApplicationTestCaseOutputsResourceWithRawResponse:
    def __init__(self, application_test_case_outputs: AsyncApplicationTestCaseOutputsResource) -> None:
        self._application_test_case_outputs = application_test_case_outputs

        self.retrieve = async_to_raw_response_wrapper(
            application_test_case_outputs.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            application_test_case_outputs.list,
        )


class ApplicationTestCaseOutputsResourceWithStreamingResponse:
    def __init__(self, application_test_case_outputs: ApplicationTestCaseOutputsResource) -> None:
        self._application_test_case_outputs = application_test_case_outputs

        self.retrieve = to_streamed_response_wrapper(
            application_test_case_outputs.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            application_test_case_outputs.list,
        )


class AsyncApplicationTestCaseOutputsResourceWithStreamingResponse:
    def __init__(self, application_test_case_outputs: AsyncApplicationTestCaseOutputsResource) -> None:
        self._application_test_case_outputs = application_test_case_outputs

        self.retrieve = async_to_streamed_response_wrapper(
            application_test_case_outputs.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            application_test_case_outputs.list,
        )
