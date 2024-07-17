# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

import httpx

from .spans import (
    SpansResource,
    AsyncSpansResource,
    SpansResourceWithRawResponse,
    AsyncSpansResourceWithRawResponse,
    SpansResourceWithStreamingResponse,
    AsyncSpansResourceWithStreamingResponse,
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
from ....types.applications import interaction_list_params, interaction_export_params
from ....types.applications.interaction_export_response import InteractionExportResponse
from ....types.applications.application_interaction_entry import ApplicationInteractionEntry

__all__ = ["InteractionsResource", "AsyncInteractionsResource"]


class InteractionsResource(SyncAPIResource):
    @cached_property
    def spans(self) -> SpansResource:
        return SpansResource(self._client)

    @cached_property
    def with_raw_response(self) -> InteractionsResourceWithRawResponse:
        return InteractionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> InteractionsResourceWithStreamingResponse:
        return InteractionsResourceWithStreamingResponse(self)

    def list(
        self,
        application_spec_id: str,
        *,
        account_id: str | NotGiven = NOT_GIVEN,
        faithfulness_max_score: float | NotGiven = NOT_GIVEN,
        faithfulness_min_score: float | NotGiven = NOT_GIVEN,
        from_ts: int | NotGiven = NOT_GIVEN,
        has_feedback_response: bool | NotGiven = NOT_GIVEN,
        has_negative_feedback: bool | NotGiven = NOT_GIVEN,
        has_positive_feedback: bool | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        relevance_max_score: float | NotGiven = NOT_GIVEN,
        relevance_min_score: float | NotGiven = NOT_GIVEN,
        search_text: str | NotGiven = NOT_GIVEN,
        sort_key: str | NotGiven = NOT_GIVEN,
        sort_order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        to_ts: int | NotGiven = NOT_GIVEN,
        variants: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationInteractionEntry:
        """
        List Application Interactions

        Args:
          account_id: Account ID used for authorization

          faithfulness_max_score: Return only interactions with a faithfulness score below this value.

          faithfulness_min_score: Return only interactions with a faithfulness score above this value.

          from_ts: The starting (oldest) timestamp window in seconds.

          has_feedback_response: Return only interactions where the user has provided a feedback response.

          has_negative_feedback: Return only interactions with the negative feedback.

          has_positive_feedback: Return only interactions with the positive feedback.

          limit: Maximum number of artifacts to be returned by the given endpoint. Defaults to
              100 and cannot be greater than 10k.

          page: Page number for pagination to be returned by the given endpoint. Starts at page
              1

          relevance_max_score: Return only interactions with a relevance score below this value.

          relevance_min_score: Return only interactions with a relevance score above this value.

          search_text: Return only interactions where either the prompt or the response contain this
              substring.

          sort_key: Sort interactions by this field.

          sort_order: An enumeration.

          to_ts: The ending (most recent) timestamp in seconds.

          variants: Which variants to filter on

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not application_spec_id:
            raise ValueError(
                f"Expected a non-empty value for `application_spec_id` but received {application_spec_id!r}"
            )
        return self._get(
            f"/v4/applications/{application_spec_id}/interactions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "account_id": account_id,
                        "faithfulness_max_score": faithfulness_max_score,
                        "faithfulness_min_score": faithfulness_min_score,
                        "from_ts": from_ts,
                        "has_feedback_response": has_feedback_response,
                        "has_negative_feedback": has_negative_feedback,
                        "has_positive_feedback": has_positive_feedback,
                        "limit": limit,
                        "page": page,
                        "relevance_max_score": relevance_max_score,
                        "relevance_min_score": relevance_min_score,
                        "search_text": search_text,
                        "sort_key": sort_key,
                        "sort_order": sort_order,
                        "to_ts": to_ts,
                        "variants": variants,
                    },
                    interaction_list_params.InteractionListParams,
                ),
            ),
            cast_to=ApplicationInteractionEntry,
        )

    def export(
        self,
        application_spec_id: str,
        *,
        faithfulness_max_score: float | NotGiven = NOT_GIVEN,
        faithfulness_min_score: float | NotGiven = NOT_GIVEN,
        from_ts: int | NotGiven = NOT_GIVEN,
        has_feedback_response: bool | NotGiven = NOT_GIVEN,
        has_negative_feedback: bool | NotGiven = NOT_GIVEN,
        has_positive_feedback: bool | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        relevance_max_score: float | NotGiven = NOT_GIVEN,
        relevance_min_score: float | NotGiven = NOT_GIVEN,
        search_text: str | NotGiven = NOT_GIVEN,
        to_ts: int | NotGiven = NOT_GIVEN,
        variants: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InteractionExportResponse:
        """
        Export Application Interactions

        Args:
          faithfulness_max_score: Return only interactions with a faithfulness score below this value.

          faithfulness_min_score: Return only interactions with a faithfulness score above this value.

          from_ts: The starting (oldest) timestamp window in seconds.

          has_feedback_response: Return only interactions where the user has provided a feedback response.

          has_negative_feedback: Return only interactions with the negative feedback.

          has_positive_feedback: Return only interactions with the positive feedback.

          limit: Maximum number of artifacts to be returned by the given endpoint. Defaults to
              100 and cannot be greater than 10k.

          page: Page number for pagination to be returned by the given endpoint. Starts at page
              1

          relevance_max_score: Return only interactions with a relevance score below this value.

          relevance_min_score: Return only interactions with a relevance score above this value.

          search_text: Return only interactions where either the prompt or the response contain this
              substring.

          to_ts: The ending (most recent) timestamp in seconds.

          variants: Which variants to filter on

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not application_spec_id:
            raise ValueError(
                f"Expected a non-empty value for `application_spec_id` but received {application_spec_id!r}"
            )
        return self._get(
            f"/v4/applications/{application_spec_id}/interactions/export",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "faithfulness_max_score": faithfulness_max_score,
                        "faithfulness_min_score": faithfulness_min_score,
                        "from_ts": from_ts,
                        "has_feedback_response": has_feedback_response,
                        "has_negative_feedback": has_negative_feedback,
                        "has_positive_feedback": has_positive_feedback,
                        "limit": limit,
                        "page": page,
                        "relevance_max_score": relevance_max_score,
                        "relevance_min_score": relevance_min_score,
                        "search_text": search_text,
                        "to_ts": to_ts,
                        "variants": variants,
                    },
                    interaction_export_params.InteractionExportParams,
                ),
            ),
            cast_to=InteractionExportResponse,
        )


class AsyncInteractionsResource(AsyncAPIResource):
    @cached_property
    def spans(self) -> AsyncSpansResource:
        return AsyncSpansResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncInteractionsResourceWithRawResponse:
        return AsyncInteractionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncInteractionsResourceWithStreamingResponse:
        return AsyncInteractionsResourceWithStreamingResponse(self)

    async def list(
        self,
        application_spec_id: str,
        *,
        account_id: str | NotGiven = NOT_GIVEN,
        faithfulness_max_score: float | NotGiven = NOT_GIVEN,
        faithfulness_min_score: float | NotGiven = NOT_GIVEN,
        from_ts: int | NotGiven = NOT_GIVEN,
        has_feedback_response: bool | NotGiven = NOT_GIVEN,
        has_negative_feedback: bool | NotGiven = NOT_GIVEN,
        has_positive_feedback: bool | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        relevance_max_score: float | NotGiven = NOT_GIVEN,
        relevance_min_score: float | NotGiven = NOT_GIVEN,
        search_text: str | NotGiven = NOT_GIVEN,
        sort_key: str | NotGiven = NOT_GIVEN,
        sort_order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        to_ts: int | NotGiven = NOT_GIVEN,
        variants: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationInteractionEntry:
        """
        List Application Interactions

        Args:
          account_id: Account ID used for authorization

          faithfulness_max_score: Return only interactions with a faithfulness score below this value.

          faithfulness_min_score: Return only interactions with a faithfulness score above this value.

          from_ts: The starting (oldest) timestamp window in seconds.

          has_feedback_response: Return only interactions where the user has provided a feedback response.

          has_negative_feedback: Return only interactions with the negative feedback.

          has_positive_feedback: Return only interactions with the positive feedback.

          limit: Maximum number of artifacts to be returned by the given endpoint. Defaults to
              100 and cannot be greater than 10k.

          page: Page number for pagination to be returned by the given endpoint. Starts at page
              1

          relevance_max_score: Return only interactions with a relevance score below this value.

          relevance_min_score: Return only interactions with a relevance score above this value.

          search_text: Return only interactions where either the prompt or the response contain this
              substring.

          sort_key: Sort interactions by this field.

          sort_order: An enumeration.

          to_ts: The ending (most recent) timestamp in seconds.

          variants: Which variants to filter on

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not application_spec_id:
            raise ValueError(
                f"Expected a non-empty value for `application_spec_id` but received {application_spec_id!r}"
            )
        return await self._get(
            f"/v4/applications/{application_spec_id}/interactions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "account_id": account_id,
                        "faithfulness_max_score": faithfulness_max_score,
                        "faithfulness_min_score": faithfulness_min_score,
                        "from_ts": from_ts,
                        "has_feedback_response": has_feedback_response,
                        "has_negative_feedback": has_negative_feedback,
                        "has_positive_feedback": has_positive_feedback,
                        "limit": limit,
                        "page": page,
                        "relevance_max_score": relevance_max_score,
                        "relevance_min_score": relevance_min_score,
                        "search_text": search_text,
                        "sort_key": sort_key,
                        "sort_order": sort_order,
                        "to_ts": to_ts,
                        "variants": variants,
                    },
                    interaction_list_params.InteractionListParams,
                ),
            ),
            cast_to=ApplicationInteractionEntry,
        )

    async def export(
        self,
        application_spec_id: str,
        *,
        faithfulness_max_score: float | NotGiven = NOT_GIVEN,
        faithfulness_min_score: float | NotGiven = NOT_GIVEN,
        from_ts: int | NotGiven = NOT_GIVEN,
        has_feedback_response: bool | NotGiven = NOT_GIVEN,
        has_negative_feedback: bool | NotGiven = NOT_GIVEN,
        has_positive_feedback: bool | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        relevance_max_score: float | NotGiven = NOT_GIVEN,
        relevance_min_score: float | NotGiven = NOT_GIVEN,
        search_text: str | NotGiven = NOT_GIVEN,
        to_ts: int | NotGiven = NOT_GIVEN,
        variants: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InteractionExportResponse:
        """
        Export Application Interactions

        Args:
          faithfulness_max_score: Return only interactions with a faithfulness score below this value.

          faithfulness_min_score: Return only interactions with a faithfulness score above this value.

          from_ts: The starting (oldest) timestamp window in seconds.

          has_feedback_response: Return only interactions where the user has provided a feedback response.

          has_negative_feedback: Return only interactions with the negative feedback.

          has_positive_feedback: Return only interactions with the positive feedback.

          limit: Maximum number of artifacts to be returned by the given endpoint. Defaults to
              100 and cannot be greater than 10k.

          page: Page number for pagination to be returned by the given endpoint. Starts at page
              1

          relevance_max_score: Return only interactions with a relevance score below this value.

          relevance_min_score: Return only interactions with a relevance score above this value.

          search_text: Return only interactions where either the prompt or the response contain this
              substring.

          to_ts: The ending (most recent) timestamp in seconds.

          variants: Which variants to filter on

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not application_spec_id:
            raise ValueError(
                f"Expected a non-empty value for `application_spec_id` but received {application_spec_id!r}"
            )
        return await self._get(
            f"/v4/applications/{application_spec_id}/interactions/export",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "faithfulness_max_score": faithfulness_max_score,
                        "faithfulness_min_score": faithfulness_min_score,
                        "from_ts": from_ts,
                        "has_feedback_response": has_feedback_response,
                        "has_negative_feedback": has_negative_feedback,
                        "has_positive_feedback": has_positive_feedback,
                        "limit": limit,
                        "page": page,
                        "relevance_max_score": relevance_max_score,
                        "relevance_min_score": relevance_min_score,
                        "search_text": search_text,
                        "to_ts": to_ts,
                        "variants": variants,
                    },
                    interaction_export_params.InteractionExportParams,
                ),
            ),
            cast_to=InteractionExportResponse,
        )


class InteractionsResourceWithRawResponse:
    def __init__(self, interactions: InteractionsResource) -> None:
        self._interactions = interactions

        self.list = to_raw_response_wrapper(
            interactions.list,
        )
        self.export = to_raw_response_wrapper(
            interactions.export,
        )

    @cached_property
    def spans(self) -> SpansResourceWithRawResponse:
        return SpansResourceWithRawResponse(self._interactions.spans)


class AsyncInteractionsResourceWithRawResponse:
    def __init__(self, interactions: AsyncInteractionsResource) -> None:
        self._interactions = interactions

        self.list = async_to_raw_response_wrapper(
            interactions.list,
        )
        self.export = async_to_raw_response_wrapper(
            interactions.export,
        )

    @cached_property
    def spans(self) -> AsyncSpansResourceWithRawResponse:
        return AsyncSpansResourceWithRawResponse(self._interactions.spans)


class InteractionsResourceWithStreamingResponse:
    def __init__(self, interactions: InteractionsResource) -> None:
        self._interactions = interactions

        self.list = to_streamed_response_wrapper(
            interactions.list,
        )
        self.export = to_streamed_response_wrapper(
            interactions.export,
        )

    @cached_property
    def spans(self) -> SpansResourceWithStreamingResponse:
        return SpansResourceWithStreamingResponse(self._interactions.spans)


class AsyncInteractionsResourceWithStreamingResponse:
    def __init__(self, interactions: AsyncInteractionsResource) -> None:
        self._interactions = interactions

        self.list = async_to_streamed_response_wrapper(
            interactions.list,
        )
        self.export = async_to_streamed_response_wrapper(
            interactions.export,
        )

    @cached_property
    def spans(self) -> AsyncSpansResourceWithStreamingResponse:
        return AsyncSpansResourceWithStreamingResponse(self._interactions.spans)
