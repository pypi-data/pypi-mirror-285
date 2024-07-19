# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.training_datasets.content_list_response import ContentListResponse

__all__ = ["ContentsResource", "AsyncContentsResource"]


class ContentsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ContentsResourceWithRawResponse:
        return ContentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ContentsResourceWithStreamingResponse:
        return ContentsResourceWithStreamingResponse(self)

    def list(
        self,
        training_dataset_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ContentListResponse:
        """
        Get Training Dataset Contents

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not training_dataset_id:
            raise ValueError(
                f"Expected a non-empty value for `training_dataset_id` but received {training_dataset_id!r}"
            )
        return self._get(
            f"/v4/training-datasets/{training_dataset_id}/contents",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ContentListResponse,
        )


class AsyncContentsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncContentsResourceWithRawResponse:
        return AsyncContentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncContentsResourceWithStreamingResponse:
        return AsyncContentsResourceWithStreamingResponse(self)

    async def list(
        self,
        training_dataset_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ContentListResponse:
        """
        Get Training Dataset Contents

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not training_dataset_id:
            raise ValueError(
                f"Expected a non-empty value for `training_dataset_id` but received {training_dataset_id!r}"
            )
        return await self._get(
            f"/v4/training-datasets/{training_dataset_id}/contents",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ContentListResponse,
        )


class ContentsResourceWithRawResponse:
    def __init__(self, contents: ContentsResource) -> None:
        self._contents = contents

        self.list = to_raw_response_wrapper(
            contents.list,
        )


class AsyncContentsResourceWithRawResponse:
    def __init__(self, contents: AsyncContentsResource) -> None:
        self._contents = contents

        self.list = async_to_raw_response_wrapper(
            contents.list,
        )


class ContentsResourceWithStreamingResponse:
    def __init__(self, contents: ContentsResource) -> None:
        self._contents = contents

        self.list = to_streamed_response_wrapper(
            contents.list,
        )


class AsyncContentsResourceWithStreamingResponse:
    def __init__(self, contents: AsyncContentsResource) -> None:
        self._contents = contents

        self.list = async_to_streamed_response_wrapper(
            contents.list,
        )
