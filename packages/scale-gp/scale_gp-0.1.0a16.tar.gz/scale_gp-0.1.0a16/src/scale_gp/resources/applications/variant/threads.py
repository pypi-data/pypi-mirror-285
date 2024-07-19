# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable

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
from ....types.applications.variant import thread_create_params, thread_process_params
from ....types.applications.variant.chat_thread import ChatThread
from ....types.applications.variant.thread_list_response import ThreadListResponse

__all__ = ["ThreadsResource", "AsyncThreadsResource"]


class ThreadsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ThreadsResourceWithRawResponse:
        return ThreadsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ThreadsResourceWithStreamingResponse:
        return ThreadsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        path_application_variant_id: str,
        account_id: str,
        body_application_variant_id: str,
        title: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChatThread:
        """
        Create New Application Thread

        Args:
          account_id: The ID of the account that owns the given entity.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_application_variant_id:
            raise ValueError(
                f"Expected a non-empty value for `path_application_variant_id` but received {path_application_variant_id!r}"
            )
        return self._post(
            f"/v4/applications/{path_application_variant_id}/threads",
            body=maybe_transform(
                {
                    "account_id": account_id,
                    "application_variant_id": body_application_variant_id,
                    "title": title,
                },
                thread_create_params.ThreadCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ChatThread,
        )

    def list(
        self,
        application_variant_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ThreadListResponse:
        """
        List Application Threads

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not application_variant_id:
            raise ValueError(
                f"Expected a non-empty value for `application_variant_id` but received {application_variant_id!r}"
            )
        return self._get(
            f"/v4/applications/{application_variant_id}/threads",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ThreadListResponse,
        )

    def process(
        self,
        thread_id: str,
        *,
        application_variant_id: str,
        inputs: Dict[str, object],
        history: Iterable[thread_process_params.History] | NotGiven = NOT_GIVEN,
        overrides: Dict[str, thread_process_params.Overrides] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Process Deployed Application For Thread

        Args:
          inputs: Input data for the application. You must provide inputs for each input node

          history: History of the application

          overrides: Optional overrides for the application

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not application_variant_id:
            raise ValueError(
                f"Expected a non-empty value for `application_variant_id` but received {application_variant_id!r}"
            )
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        return self._post(
            f"/v4/applications/{application_variant_id}/threads/{thread_id}/process",
            body=maybe_transform(
                {
                    "inputs": inputs,
                    "history": history,
                    "overrides": overrides,
                },
                thread_process_params.ThreadProcessParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncThreadsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncThreadsResourceWithRawResponse:
        return AsyncThreadsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncThreadsResourceWithStreamingResponse:
        return AsyncThreadsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        path_application_variant_id: str,
        account_id: str,
        body_application_variant_id: str,
        title: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChatThread:
        """
        Create New Application Thread

        Args:
          account_id: The ID of the account that owns the given entity.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_application_variant_id:
            raise ValueError(
                f"Expected a non-empty value for `path_application_variant_id` but received {path_application_variant_id!r}"
            )
        return await self._post(
            f"/v4/applications/{path_application_variant_id}/threads",
            body=await async_maybe_transform(
                {
                    "account_id": account_id,
                    "application_variant_id": body_application_variant_id,
                    "title": title,
                },
                thread_create_params.ThreadCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ChatThread,
        )

    async def list(
        self,
        application_variant_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ThreadListResponse:
        """
        List Application Threads

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not application_variant_id:
            raise ValueError(
                f"Expected a non-empty value for `application_variant_id` but received {application_variant_id!r}"
            )
        return await self._get(
            f"/v4/applications/{application_variant_id}/threads",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ThreadListResponse,
        )

    async def process(
        self,
        thread_id: str,
        *,
        application_variant_id: str,
        inputs: Dict[str, object],
        history: Iterable[thread_process_params.History] | NotGiven = NOT_GIVEN,
        overrides: Dict[str, thread_process_params.Overrides] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Process Deployed Application For Thread

        Args:
          inputs: Input data for the application. You must provide inputs for each input node

          history: History of the application

          overrides: Optional overrides for the application

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not application_variant_id:
            raise ValueError(
                f"Expected a non-empty value for `application_variant_id` but received {application_variant_id!r}"
            )
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        return await self._post(
            f"/v4/applications/{application_variant_id}/threads/{thread_id}/process",
            body=await async_maybe_transform(
                {
                    "inputs": inputs,
                    "history": history,
                    "overrides": overrides,
                },
                thread_process_params.ThreadProcessParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class ThreadsResourceWithRawResponse:
    def __init__(self, threads: ThreadsResource) -> None:
        self._threads = threads

        self.create = to_raw_response_wrapper(
            threads.create,
        )
        self.list = to_raw_response_wrapper(
            threads.list,
        )
        self.process = to_raw_response_wrapper(
            threads.process,
        )


class AsyncThreadsResourceWithRawResponse:
    def __init__(self, threads: AsyncThreadsResource) -> None:
        self._threads = threads

        self.create = async_to_raw_response_wrapper(
            threads.create,
        )
        self.list = async_to_raw_response_wrapper(
            threads.list,
        )
        self.process = async_to_raw_response_wrapper(
            threads.process,
        )


class ThreadsResourceWithStreamingResponse:
    def __init__(self, threads: ThreadsResource) -> None:
        self._threads = threads

        self.create = to_streamed_response_wrapper(
            threads.create,
        )
        self.list = to_streamed_response_wrapper(
            threads.list,
        )
        self.process = to_streamed_response_wrapper(
            threads.process,
        )


class AsyncThreadsResourceWithStreamingResponse:
    def __init__(self, threads: AsyncThreadsResource) -> None:
        self._threads = threads

        self.create = async_to_streamed_response_wrapper(
            threads.create,
        )
        self.list = async_to_streamed_response_wrapper(
            threads.list,
        )
        self.process = async_to_streamed_response_wrapper(
            threads.process,
        )
