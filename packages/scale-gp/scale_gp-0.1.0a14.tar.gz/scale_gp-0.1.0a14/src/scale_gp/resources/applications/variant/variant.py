# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable

import httpx

from .threads import (
    ThreadsResource,
    AsyncThreadsResource,
    ThreadsResourceWithRawResponse,
    AsyncThreadsResourceWithRawResponse,
    ThreadsResourceWithStreamingResponse,
    AsyncThreadsResourceWithStreamingResponse,
)
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
from ....types.applications import variant_process_params

__all__ = ["VariantResource", "AsyncVariantResource"]


class VariantResource(SyncAPIResource):
    @cached_property
    def threads(self) -> ThreadsResource:
        return ThreadsResource(self._client)

    @cached_property
    def with_raw_response(self) -> VariantResourceWithRawResponse:
        return VariantResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> VariantResourceWithStreamingResponse:
        return VariantResourceWithStreamingResponse(self)

    def process(
        self,
        application_variant_id: str,
        *,
        inputs: Dict[str, object],
        history: Iterable[variant_process_params.History] | NotGiven = NOT_GIVEN,
        overrides: Dict[str, variant_process_params.Overrides] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Process Application By Id

        Args:
          inputs: Input data for the application.

        You must provide inputs for each input node

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
        return self._post(
            f"/v4/applications/{application_variant_id}/process",
            body=maybe_transform(
                {
                    "inputs": inputs,
                    "history": history,
                    "overrides": overrides,
                },
                variant_process_params.VariantProcessParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncVariantResource(AsyncAPIResource):
    @cached_property
    def threads(self) -> AsyncThreadsResource:
        return AsyncThreadsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncVariantResourceWithRawResponse:
        return AsyncVariantResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncVariantResourceWithStreamingResponse:
        return AsyncVariantResourceWithStreamingResponse(self)

    async def process(
        self,
        application_variant_id: str,
        *,
        inputs: Dict[str, object],
        history: Iterable[variant_process_params.History] | NotGiven = NOT_GIVEN,
        overrides: Dict[str, variant_process_params.Overrides] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Process Application By Id

        Args:
          inputs: Input data for the application.

        You must provide inputs for each input node

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
        return await self._post(
            f"/v4/applications/{application_variant_id}/process",
            body=await async_maybe_transform(
                {
                    "inputs": inputs,
                    "history": history,
                    "overrides": overrides,
                },
                variant_process_params.VariantProcessParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class VariantResourceWithRawResponse:
    def __init__(self, variant: VariantResource) -> None:
        self._variant = variant

        self.process = to_raw_response_wrapper(
            variant.process,
        )

    @cached_property
    def threads(self) -> ThreadsResourceWithRawResponse:
        return ThreadsResourceWithRawResponse(self._variant.threads)


class AsyncVariantResourceWithRawResponse:
    def __init__(self, variant: AsyncVariantResource) -> None:
        self._variant = variant

        self.process = async_to_raw_response_wrapper(
            variant.process,
        )

    @cached_property
    def threads(self) -> AsyncThreadsResourceWithRawResponse:
        return AsyncThreadsResourceWithRawResponse(self._variant.threads)


class VariantResourceWithStreamingResponse:
    def __init__(self, variant: VariantResource) -> None:
        self._variant = variant

        self.process = to_streamed_response_wrapper(
            variant.process,
        )

    @cached_property
    def threads(self) -> ThreadsResourceWithStreamingResponse:
        return ThreadsResourceWithStreamingResponse(self._variant.threads)


class AsyncVariantResourceWithStreamingResponse:
    def __init__(self, variant: AsyncVariantResource) -> None:
        self._variant = variant

        self.process = async_to_streamed_response_wrapper(
            variant.process,
        )

    @cached_property
    def threads(self) -> AsyncThreadsResourceWithStreamingResponse:
        return AsyncThreadsResourceWithStreamingResponse(self._variant.threads)
