# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Literal

import httpx

from ...types import application_process_params, application_validate_params
from .metrics import (
    MetricsResource,
    AsyncMetricsResource,
    MetricsResourceWithRawResponse,
    AsyncMetricsResourceWithRawResponse,
    MetricsResourceWithStreamingResponse,
    AsyncMetricsResourceWithStreamingResponse,
)
from .variant import (
    VariantResource,
    AsyncVariantResource,
    VariantResourceWithRawResponse,
    AsyncVariantResourceWithRawResponse,
    VariantResourceWithStreamingResponse,
    AsyncVariantResourceWithStreamingResponse,
)
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import (
    maybe_transform,
    async_maybe_transform,
)
from ..._compat import cached_property
from .dashboards import (
    DashboardsResource,
    AsyncDashboardsResource,
    DashboardsResourceWithRawResponse,
    AsyncDashboardsResourceWithRawResponse,
    DashboardsResourceWithStreamingResponse,
    AsyncDashboardsResourceWithStreamingResponse,
)
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .interactions import (
    InteractionsResource,
    AsyncInteractionsResource,
    InteractionsResourceWithRawResponse,
    AsyncInteractionsResourceWithRawResponse,
    InteractionsResourceWithStreamingResponse,
    AsyncInteractionsResourceWithStreamingResponse,
)
from .upload_files import (
    UploadFilesResource,
    AsyncUploadFilesResource,
    UploadFilesResourceWithRawResponse,
    AsyncUploadFilesResourceWithRawResponse,
    UploadFilesResourceWithStreamingResponse,
    AsyncUploadFilesResourceWithStreamingResponse,
)
from ..._base_client import make_request_options
from .metrics.metrics import MetricsResource, AsyncMetricsResource
from .variant.variant import VariantResource, AsyncVariantResource
from .interactions.interactions import InteractionsResource, AsyncInteractionsResource

__all__ = ["ApplicationsResource", "AsyncApplicationsResource"]


class ApplicationsResource(SyncAPIResource):
    @cached_property
    def variant(self) -> VariantResource:
        return VariantResource(self._client)

    @cached_property
    def interactions(self) -> InteractionsResource:
        return InteractionsResource(self._client)

    @cached_property
    def dashboards(self) -> DashboardsResource:
        return DashboardsResource(self._client)

    @cached_property
    def upload_files(self) -> UploadFilesResource:
        return UploadFilesResource(self._client)

    @cached_property
    def metrics(self) -> MetricsResource:
        return MetricsResource(self._client)

    @cached_property
    def with_raw_response(self) -> ApplicationsResourceWithRawResponse:
        return ApplicationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ApplicationsResourceWithStreamingResponse:
        return ApplicationsResourceWithStreamingResponse(self)

    def process(
        self,
        *,
        edges: Iterable[application_process_params.Edge],
        inputs: Dict[str, object],
        nodes: Iterable[application_process_params.Node],
        version: Literal["V0"],
        history: Iterable[application_process_params.History] | NotGiven = NOT_GIVEN,
        overrides: Dict[str, application_process_params.Overrides] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Process Application

        Args:
          edges: List of edges in the application graph

          inputs: Input data for the application. You must provide inputs for each input node

          nodes: List of nodes in the application graph

          version: Version of the application schema

          history: History of the application

          overrides: Optional overrides for the application

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v4/applications/process",
            body=maybe_transform(
                {
                    "edges": edges,
                    "inputs": inputs,
                    "nodes": nodes,
                    "version": version,
                    "history": history,
                    "overrides": overrides,
                },
                application_process_params.ApplicationProcessParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def validate(
        self,
        *,
        edges: Iterable[application_validate_params.Edge],
        nodes: Iterable[application_validate_params.Node],
        version: Literal["V0"],
        overrides: Dict[str, application_validate_params.Overrides] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Validate Application

        Args:
          edges: List of edges in the application graph

          nodes: List of nodes in the application graph

          version: Version of the application schema

          overrides: Optional overrides for the application

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v4/applications/validate",
            body=maybe_transform(
                {
                    "edges": edges,
                    "nodes": nodes,
                    "version": version,
                    "overrides": overrides,
                },
                application_validate_params.ApplicationValidateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncApplicationsResource(AsyncAPIResource):
    @cached_property
    def variant(self) -> AsyncVariantResource:
        return AsyncVariantResource(self._client)

    @cached_property
    def interactions(self) -> AsyncInteractionsResource:
        return AsyncInteractionsResource(self._client)

    @cached_property
    def dashboards(self) -> AsyncDashboardsResource:
        return AsyncDashboardsResource(self._client)

    @cached_property
    def upload_files(self) -> AsyncUploadFilesResource:
        return AsyncUploadFilesResource(self._client)

    @cached_property
    def metrics(self) -> AsyncMetricsResource:
        return AsyncMetricsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncApplicationsResourceWithRawResponse:
        return AsyncApplicationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncApplicationsResourceWithStreamingResponse:
        return AsyncApplicationsResourceWithStreamingResponse(self)

    async def process(
        self,
        *,
        edges: Iterable[application_process_params.Edge],
        inputs: Dict[str, object],
        nodes: Iterable[application_process_params.Node],
        version: Literal["V0"],
        history: Iterable[application_process_params.History] | NotGiven = NOT_GIVEN,
        overrides: Dict[str, application_process_params.Overrides] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Process Application

        Args:
          edges: List of edges in the application graph

          inputs: Input data for the application. You must provide inputs for each input node

          nodes: List of nodes in the application graph

          version: Version of the application schema

          history: History of the application

          overrides: Optional overrides for the application

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v4/applications/process",
            body=await async_maybe_transform(
                {
                    "edges": edges,
                    "inputs": inputs,
                    "nodes": nodes,
                    "version": version,
                    "history": history,
                    "overrides": overrides,
                },
                application_process_params.ApplicationProcessParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def validate(
        self,
        *,
        edges: Iterable[application_validate_params.Edge],
        nodes: Iterable[application_validate_params.Node],
        version: Literal["V0"],
        overrides: Dict[str, application_validate_params.Overrides] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Validate Application

        Args:
          edges: List of edges in the application graph

          nodes: List of nodes in the application graph

          version: Version of the application schema

          overrides: Optional overrides for the application

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v4/applications/validate",
            body=await async_maybe_transform(
                {
                    "edges": edges,
                    "nodes": nodes,
                    "version": version,
                    "overrides": overrides,
                },
                application_validate_params.ApplicationValidateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class ApplicationsResourceWithRawResponse:
    def __init__(self, applications: ApplicationsResource) -> None:
        self._applications = applications

        self.process = to_raw_response_wrapper(
            applications.process,
        )
        self.validate = to_raw_response_wrapper(
            applications.validate,
        )

    @cached_property
    def variant(self) -> VariantResourceWithRawResponse:
        return VariantResourceWithRawResponse(self._applications.variant)

    @cached_property
    def interactions(self) -> InteractionsResourceWithRawResponse:
        return InteractionsResourceWithRawResponse(self._applications.interactions)

    @cached_property
    def dashboards(self) -> DashboardsResourceWithRawResponse:
        return DashboardsResourceWithRawResponse(self._applications.dashboards)

    @cached_property
    def upload_files(self) -> UploadFilesResourceWithRawResponse:
        return UploadFilesResourceWithRawResponse(self._applications.upload_files)

    @cached_property
    def metrics(self) -> MetricsResourceWithRawResponse:
        return MetricsResourceWithRawResponse(self._applications.metrics)


class AsyncApplicationsResourceWithRawResponse:
    def __init__(self, applications: AsyncApplicationsResource) -> None:
        self._applications = applications

        self.process = async_to_raw_response_wrapper(
            applications.process,
        )
        self.validate = async_to_raw_response_wrapper(
            applications.validate,
        )

    @cached_property
    def variant(self) -> AsyncVariantResourceWithRawResponse:
        return AsyncVariantResourceWithRawResponse(self._applications.variant)

    @cached_property
    def interactions(self) -> AsyncInteractionsResourceWithRawResponse:
        return AsyncInteractionsResourceWithRawResponse(self._applications.interactions)

    @cached_property
    def dashboards(self) -> AsyncDashboardsResourceWithRawResponse:
        return AsyncDashboardsResourceWithRawResponse(self._applications.dashboards)

    @cached_property
    def upload_files(self) -> AsyncUploadFilesResourceWithRawResponse:
        return AsyncUploadFilesResourceWithRawResponse(self._applications.upload_files)

    @cached_property
    def metrics(self) -> AsyncMetricsResourceWithRawResponse:
        return AsyncMetricsResourceWithRawResponse(self._applications.metrics)


class ApplicationsResourceWithStreamingResponse:
    def __init__(self, applications: ApplicationsResource) -> None:
        self._applications = applications

        self.process = to_streamed_response_wrapper(
            applications.process,
        )
        self.validate = to_streamed_response_wrapper(
            applications.validate,
        )

    @cached_property
    def variant(self) -> VariantResourceWithStreamingResponse:
        return VariantResourceWithStreamingResponse(self._applications.variant)

    @cached_property
    def interactions(self) -> InteractionsResourceWithStreamingResponse:
        return InteractionsResourceWithStreamingResponse(self._applications.interactions)

    @cached_property
    def dashboards(self) -> DashboardsResourceWithStreamingResponse:
        return DashboardsResourceWithStreamingResponse(self._applications.dashboards)

    @cached_property
    def upload_files(self) -> UploadFilesResourceWithStreamingResponse:
        return UploadFilesResourceWithStreamingResponse(self._applications.upload_files)

    @cached_property
    def metrics(self) -> MetricsResourceWithStreamingResponse:
        return MetricsResourceWithStreamingResponse(self._applications.metrics)


class AsyncApplicationsResourceWithStreamingResponse:
    def __init__(self, applications: AsyncApplicationsResource) -> None:
        self._applications = applications

        self.process = async_to_streamed_response_wrapper(
            applications.process,
        )
        self.validate = async_to_streamed_response_wrapper(
            applications.validate,
        )

    @cached_property
    def variant(self) -> AsyncVariantResourceWithStreamingResponse:
        return AsyncVariantResourceWithStreamingResponse(self._applications.variant)

    @cached_property
    def interactions(self) -> AsyncInteractionsResourceWithStreamingResponse:
        return AsyncInteractionsResourceWithStreamingResponse(self._applications.interactions)

    @cached_property
    def dashboards(self) -> AsyncDashboardsResourceWithStreamingResponse:
        return AsyncDashboardsResourceWithStreamingResponse(self._applications.dashboards)

    @cached_property
    def upload_files(self) -> AsyncUploadFilesResourceWithStreamingResponse:
        return AsyncUploadFilesResourceWithStreamingResponse(self._applications.upload_files)

    @cached_property
    def metrics(self) -> AsyncMetricsResourceWithStreamingResponse:
        return AsyncMetricsResourceWithStreamingResponse(self._applications.metrics)
