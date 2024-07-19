# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import (
    maybe_transform,
    async_maybe_transform,
)
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.shared.delete_response import DeleteResponse
from ....types.evaluation_datasets.test_cases import history_list_params
from ....types.shared.test_case_version_response import TestCaseVersionResponse
from ....types.evaluation_datasets.test_cases.history_list_response import HistoryListResponse

__all__ = ["HistoryResource", "AsyncHistoryResource"]


class HistoryResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> HistoryResourceWithRawResponse:
        return HistoryResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> HistoryResourceWithStreamingResponse:
        return HistoryResourceWithStreamingResponse(self)

    def retrieve(
        self,
        num: str,
        *,
        evaluation_dataset_id: str,
        test_case_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TestCaseVersionResponse:
        """
        ### Description

        Get the test case by its id for a specified dataset version.

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
        if not test_case_id:
            raise ValueError(f"Expected a non-empty value for `test_case_id` but received {test_case_id!r}")
        if not num:
            raise ValueError(f"Expected a non-empty value for `num` but received {num!r}")
        return self._get(
            f"/v4/evaluation-datasets/{evaluation_dataset_id}/test-cases/{test_case_id}/history/{num}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TestCaseVersionResponse,
        )

    def list(
        self,
        num: str,
        *,
        evaluation_dataset_id: str,
        account_id: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HistoryListResponse:
        """
        ### Description

        List all test cases for a specified dataset version.

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
        if not evaluation_dataset_id:
            raise ValueError(
                f"Expected a non-empty value for `evaluation_dataset_id` but received {evaluation_dataset_id!r}"
            )
        if not num:
            raise ValueError(f"Expected a non-empty value for `num` but received {num!r}")
        return self._get(
            f"/v4/evaluation-datasets/{evaluation_dataset_id}/test-cases/history/{num}",
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
                    history_list_params.HistoryListParams,
                ),
            ),
            cast_to=HistoryListResponse,
        )

    def delete(
        self,
        test_case_id: str,
        *,
        evaluation_dataset_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeleteResponse:
        """
        ### Description

        Delete a specified test case and remove all its history from past dataset
        versions too.

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
        if not test_case_id:
            raise ValueError(f"Expected a non-empty value for `test_case_id` but received {test_case_id!r}")
        return self._delete(
            f"/v4/evaluation-datasets/{evaluation_dataset_id}/test-cases/{test_case_id}/history",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )


class AsyncHistoryResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncHistoryResourceWithRawResponse:
        return AsyncHistoryResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncHistoryResourceWithStreamingResponse:
        return AsyncHistoryResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        num: str,
        *,
        evaluation_dataset_id: str,
        test_case_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TestCaseVersionResponse:
        """
        ### Description

        Get the test case by its id for a specified dataset version.

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
        if not test_case_id:
            raise ValueError(f"Expected a non-empty value for `test_case_id` but received {test_case_id!r}")
        if not num:
            raise ValueError(f"Expected a non-empty value for `num` but received {num!r}")
        return await self._get(
            f"/v4/evaluation-datasets/{evaluation_dataset_id}/test-cases/{test_case_id}/history/{num}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TestCaseVersionResponse,
        )

    async def list(
        self,
        num: str,
        *,
        evaluation_dataset_id: str,
        account_id: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HistoryListResponse:
        """
        ### Description

        List all test cases for a specified dataset version.

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
        if not evaluation_dataset_id:
            raise ValueError(
                f"Expected a non-empty value for `evaluation_dataset_id` but received {evaluation_dataset_id!r}"
            )
        if not num:
            raise ValueError(f"Expected a non-empty value for `num` but received {num!r}")
        return await self._get(
            f"/v4/evaluation-datasets/{evaluation_dataset_id}/test-cases/history/{num}",
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
                    history_list_params.HistoryListParams,
                ),
            ),
            cast_to=HistoryListResponse,
        )

    async def delete(
        self,
        test_case_id: str,
        *,
        evaluation_dataset_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeleteResponse:
        """
        ### Description

        Delete a specified test case and remove all its history from past dataset
        versions too.

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
        if not test_case_id:
            raise ValueError(f"Expected a non-empty value for `test_case_id` but received {test_case_id!r}")
        return await self._delete(
            f"/v4/evaluation-datasets/{evaluation_dataset_id}/test-cases/{test_case_id}/history",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )


class HistoryResourceWithRawResponse:
    def __init__(self, history: HistoryResource) -> None:
        self._history = history

        self.retrieve = to_raw_response_wrapper(
            history.retrieve,
        )
        self.list = to_raw_response_wrapper(
            history.list,
        )
        self.delete = to_raw_response_wrapper(
            history.delete,
        )


class AsyncHistoryResourceWithRawResponse:
    def __init__(self, history: AsyncHistoryResource) -> None:
        self._history = history

        self.retrieve = async_to_raw_response_wrapper(
            history.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            history.list,
        )
        self.delete = async_to_raw_response_wrapper(
            history.delete,
        )


class HistoryResourceWithStreamingResponse:
    def __init__(self, history: HistoryResource) -> None:
        self._history = history

        self.retrieve = to_streamed_response_wrapper(
            history.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            history.list,
        )
        self.delete = to_streamed_response_wrapper(
            history.delete,
        )


class AsyncHistoryResourceWithStreamingResponse:
    def __init__(self, history: AsyncHistoryResource) -> None:
        self._history = history

        self.retrieve = async_to_streamed_response_wrapper(
            history.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            history.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            history.delete,
        )
