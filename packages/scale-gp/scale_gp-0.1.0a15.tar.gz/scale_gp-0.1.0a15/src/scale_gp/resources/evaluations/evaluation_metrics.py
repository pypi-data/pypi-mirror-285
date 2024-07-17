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
from ...types.evaluations.evaluation_metrics_response import EvaluationMetricsResponse

__all__ = ["EvaluationMetricsResource", "AsyncEvaluationMetricsResource"]


class EvaluationMetricsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> EvaluationMetricsResourceWithRawResponse:
        return EvaluationMetricsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EvaluationMetricsResourceWithStreamingResponse:
        return EvaluationMetricsResourceWithStreamingResponse(self)

    def list(
        self,
        evaluation_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EvaluationMetricsResponse:
        """
        Get Evaluation Metrics

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not evaluation_id:
            raise ValueError(f"Expected a non-empty value for `evaluation_id` but received {evaluation_id!r}")
        return self._get(
            f"/v4/evaluations/{evaluation_id}/evaluation-metrics",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluationMetricsResponse,
        )


class AsyncEvaluationMetricsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncEvaluationMetricsResourceWithRawResponse:
        return AsyncEvaluationMetricsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEvaluationMetricsResourceWithStreamingResponse:
        return AsyncEvaluationMetricsResourceWithStreamingResponse(self)

    async def list(
        self,
        evaluation_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EvaluationMetricsResponse:
        """
        Get Evaluation Metrics

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not evaluation_id:
            raise ValueError(f"Expected a non-empty value for `evaluation_id` but received {evaluation_id!r}")
        return await self._get(
            f"/v4/evaluations/{evaluation_id}/evaluation-metrics",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluationMetricsResponse,
        )


class EvaluationMetricsResourceWithRawResponse:
    def __init__(self, evaluation_metrics: EvaluationMetricsResource) -> None:
        self._evaluation_metrics = evaluation_metrics

        self.list = to_raw_response_wrapper(
            evaluation_metrics.list,
        )


class AsyncEvaluationMetricsResourceWithRawResponse:
    def __init__(self, evaluation_metrics: AsyncEvaluationMetricsResource) -> None:
        self._evaluation_metrics = evaluation_metrics

        self.list = async_to_raw_response_wrapper(
            evaluation_metrics.list,
        )


class EvaluationMetricsResourceWithStreamingResponse:
    def __init__(self, evaluation_metrics: EvaluationMetricsResource) -> None:
        self._evaluation_metrics = evaluation_metrics

        self.list = to_streamed_response_wrapper(
            evaluation_metrics.list,
        )


class AsyncEvaluationMetricsResourceWithStreamingResponse:
    def __init__(self, evaluation_metrics: AsyncEvaluationMetricsResource) -> None:
        self._evaluation_metrics = evaluation_metrics

        self.list = async_to_streamed_response_wrapper(
            evaluation_metrics.list,
        )
