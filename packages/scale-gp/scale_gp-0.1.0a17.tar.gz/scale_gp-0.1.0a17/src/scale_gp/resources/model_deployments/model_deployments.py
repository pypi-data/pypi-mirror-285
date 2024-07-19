# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

import httpx

from ...types import model_deployment_list_params
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
from .usage_statistics import (
    UsageStatisticsResource,
    AsyncUsageStatisticsResource,
    UsageStatisticsResourceWithRawResponse,
    AsyncUsageStatisticsResourceWithRawResponse,
    UsageStatisticsResourceWithStreamingResponse,
    AsyncUsageStatisticsResourceWithStreamingResponse,
)
from ...types.shared.pagination_response_model_deployment import PaginationResponseModelDeployment

__all__ = ["ModelDeploymentsResource", "AsyncModelDeploymentsResource"]


class ModelDeploymentsResource(SyncAPIResource):
    @cached_property
    def usage_statistics(self) -> UsageStatisticsResource:
        return UsageStatisticsResource(self._client)

    @cached_property
    def with_raw_response(self) -> ModelDeploymentsResourceWithRawResponse:
        return ModelDeploymentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ModelDeploymentsResourceWithStreamingResponse:
        return ModelDeploymentsResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        account_id: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        sort_by: List[
            Literal[
                "model_creation_parameters:asc",
                "model_creation_parameters:desc",
                "model_endpoint_id:asc",
                "model_endpoint_id:desc",
                "model_instance_id:asc",
                "model_instance_id:desc",
                "vendor_configuration:asc",
                "vendor_configuration:desc",
                "deployment_metadata:asc",
                "deployment_metadata:desc",
                "status:asc",
                "status:desc",
                "id:asc",
                "id:desc",
                "created_at:asc",
                "created_at:desc",
                "account_id:asc",
                "account_id:desc",
                "created_by_user_id:asc",
                "created_by_user_id:desc",
                "created_by_user:asc",
                "created_by_user:desc",
                "name:asc",
                "name:desc",
            ]
        ]
        | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PaginationResponseModelDeployment:
        """
        TODO: Document

        Args:
          account_id: Optional filter by account id

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
            "/v4/model-deployments",
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
                        "sort_by": sort_by,
                    },
                    model_deployment_list_params.ModelDeploymentListParams,
                ),
            ),
            cast_to=PaginationResponseModelDeployment,
        )


class AsyncModelDeploymentsResource(AsyncAPIResource):
    @cached_property
    def usage_statistics(self) -> AsyncUsageStatisticsResource:
        return AsyncUsageStatisticsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncModelDeploymentsResourceWithRawResponse:
        return AsyncModelDeploymentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncModelDeploymentsResourceWithStreamingResponse:
        return AsyncModelDeploymentsResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        account_id: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        sort_by: List[
            Literal[
                "model_creation_parameters:asc",
                "model_creation_parameters:desc",
                "model_endpoint_id:asc",
                "model_endpoint_id:desc",
                "model_instance_id:asc",
                "model_instance_id:desc",
                "vendor_configuration:asc",
                "vendor_configuration:desc",
                "deployment_metadata:asc",
                "deployment_metadata:desc",
                "status:asc",
                "status:desc",
                "id:asc",
                "id:desc",
                "created_at:asc",
                "created_at:desc",
                "account_id:asc",
                "account_id:desc",
                "created_by_user_id:asc",
                "created_by_user_id:desc",
                "created_by_user:asc",
                "created_by_user:desc",
                "name:asc",
                "name:desc",
            ]
        ]
        | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PaginationResponseModelDeployment:
        """
        TODO: Document

        Args:
          account_id: Optional filter by account id

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
            "/v4/model-deployments",
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
                        "sort_by": sort_by,
                    },
                    model_deployment_list_params.ModelDeploymentListParams,
                ),
            ),
            cast_to=PaginationResponseModelDeployment,
        )


class ModelDeploymentsResourceWithRawResponse:
    def __init__(self, model_deployments: ModelDeploymentsResource) -> None:
        self._model_deployments = model_deployments

        self.list = to_raw_response_wrapper(
            model_deployments.list,
        )

    @cached_property
    def usage_statistics(self) -> UsageStatisticsResourceWithRawResponse:
        return UsageStatisticsResourceWithRawResponse(self._model_deployments.usage_statistics)


class AsyncModelDeploymentsResourceWithRawResponse:
    def __init__(self, model_deployments: AsyncModelDeploymentsResource) -> None:
        self._model_deployments = model_deployments

        self.list = async_to_raw_response_wrapper(
            model_deployments.list,
        )

    @cached_property
    def usage_statistics(self) -> AsyncUsageStatisticsResourceWithRawResponse:
        return AsyncUsageStatisticsResourceWithRawResponse(self._model_deployments.usage_statistics)


class ModelDeploymentsResourceWithStreamingResponse:
    def __init__(self, model_deployments: ModelDeploymentsResource) -> None:
        self._model_deployments = model_deployments

        self.list = to_streamed_response_wrapper(
            model_deployments.list,
        )

    @cached_property
    def usage_statistics(self) -> UsageStatisticsResourceWithStreamingResponse:
        return UsageStatisticsResourceWithStreamingResponse(self._model_deployments.usage_statistics)


class AsyncModelDeploymentsResourceWithStreamingResponse:
    def __init__(self, model_deployments: AsyncModelDeploymentsResource) -> None:
        self._model_deployments = model_deployments

        self.list = async_to_streamed_response_wrapper(
            model_deployments.list,
        )

    @cached_property
    def usage_statistics(self) -> AsyncUsageStatisticsResourceWithStreamingResponse:
        return AsyncUsageStatisticsResourceWithStreamingResponse(self._model_deployments.usage_statistics)
