# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import evaluation_config_list_params, evaluation_config_create_params
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
from ..types.shared.delete_response import DeleteResponse
from ..types.evaluation_config_response import EvaluationConfigResponse
from ..types.pagination_response_evaluation_config import PaginationResponseEvaluationConfig

__all__ = ["EvaluationConfigsResource", "AsyncEvaluationConfigsResource"]


class EvaluationConfigsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> EvaluationConfigsResourceWithRawResponse:
        return EvaluationConfigsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EvaluationConfigsResourceWithStreamingResponse:
        return EvaluationConfigsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        account_id: str,
        evaluation_type: Literal["studio", "llm_auto", "human", "llm_benchmark"],
        question_set_id: str,
        studio_project_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EvaluationConfigResponse:
        """
        ### Description

        Creates a evaluation config

        ### Details

        This API can be used to create a evaluation config. To use this API, review the
        request schema and pass in all fields that are required to create a evaluation
        config.

        Args:
          account_id: The ID of the account that owns the given entity.

          evaluation_type: An enumeration.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v4/evaluation-configs",
            body=maybe_transform(
                {
                    "account_id": account_id,
                    "evaluation_type": evaluation_type,
                    "question_set_id": question_set_id,
                    "studio_project_id": studio_project_id,
                },
                evaluation_config_create_params.EvaluationConfigCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluationConfigResponse,
        )

    def retrieve(
        self,
        evaluation_config_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EvaluationConfigResponse:
        """
        ### Description

        Gets the details of a evaluation config

        ### Details

        This API can be used to get information about a single evaluation config by ID.
        To use this API, pass in the `id` that was returned from your Create Evaluation
        Config API call as a path parameter.

        Review the response schema to see the fields that will be returned.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not evaluation_config_id:
            raise ValueError(
                f"Expected a non-empty value for `evaluation_config_id` but received {evaluation_config_id!r}"
            )
        return self._get(
            f"/v4/evaluation-configs/{evaluation_config_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluationConfigResponse,
        )

    def list(
        self,
        *,
        account_id: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PaginationResponseEvaluationConfig:
        """
        ### Description

        Lists all evaluation configs accessible to the user.

        ### Details

        This API can be used to list evaluation configs. If a user has access to
        multiple accounts, all evaluation configs from all accounts the user is
        associated with will be returned.

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
            "/v4/evaluation-configs",
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
                    evaluation_config_list_params.EvaluationConfigListParams,
                ),
            ),
            cast_to=PaginationResponseEvaluationConfig,
        )

    def delete(
        self,
        evaluation_config_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeleteResponse:
        """
        ### Description

        Deletes a evaluation config

        ### Details

        This API can be used to delete a evaluation config by ID. To use this API, pass
        in the `id` that was returned from your Create Evaluation Config API call as a
        path parameter.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not evaluation_config_id:
            raise ValueError(
                f"Expected a non-empty value for `evaluation_config_id` but received {evaluation_config_id!r}"
            )
        return self._delete(
            f"/v4/evaluation-configs/{evaluation_config_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )


class AsyncEvaluationConfigsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncEvaluationConfigsResourceWithRawResponse:
        return AsyncEvaluationConfigsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEvaluationConfigsResourceWithStreamingResponse:
        return AsyncEvaluationConfigsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        account_id: str,
        evaluation_type: Literal["studio", "llm_auto", "human", "llm_benchmark"],
        question_set_id: str,
        studio_project_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EvaluationConfigResponse:
        """
        ### Description

        Creates a evaluation config

        ### Details

        This API can be used to create a evaluation config. To use this API, review the
        request schema and pass in all fields that are required to create a evaluation
        config.

        Args:
          account_id: The ID of the account that owns the given entity.

          evaluation_type: An enumeration.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v4/evaluation-configs",
            body=await async_maybe_transform(
                {
                    "account_id": account_id,
                    "evaluation_type": evaluation_type,
                    "question_set_id": question_set_id,
                    "studio_project_id": studio_project_id,
                },
                evaluation_config_create_params.EvaluationConfigCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluationConfigResponse,
        )

    async def retrieve(
        self,
        evaluation_config_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EvaluationConfigResponse:
        """
        ### Description

        Gets the details of a evaluation config

        ### Details

        This API can be used to get information about a single evaluation config by ID.
        To use this API, pass in the `id` that was returned from your Create Evaluation
        Config API call as a path parameter.

        Review the response schema to see the fields that will be returned.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not evaluation_config_id:
            raise ValueError(
                f"Expected a non-empty value for `evaluation_config_id` but received {evaluation_config_id!r}"
            )
        return await self._get(
            f"/v4/evaluation-configs/{evaluation_config_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluationConfigResponse,
        )

    async def list(
        self,
        *,
        account_id: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PaginationResponseEvaluationConfig:
        """
        ### Description

        Lists all evaluation configs accessible to the user.

        ### Details

        This API can be used to list evaluation configs. If a user has access to
        multiple accounts, all evaluation configs from all accounts the user is
        associated with will be returned.

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
            "/v4/evaluation-configs",
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
                    evaluation_config_list_params.EvaluationConfigListParams,
                ),
            ),
            cast_to=PaginationResponseEvaluationConfig,
        )

    async def delete(
        self,
        evaluation_config_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeleteResponse:
        """
        ### Description

        Deletes a evaluation config

        ### Details

        This API can be used to delete a evaluation config by ID. To use this API, pass
        in the `id` that was returned from your Create Evaluation Config API call as a
        path parameter.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not evaluation_config_id:
            raise ValueError(
                f"Expected a non-empty value for `evaluation_config_id` but received {evaluation_config_id!r}"
            )
        return await self._delete(
            f"/v4/evaluation-configs/{evaluation_config_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )


class EvaluationConfigsResourceWithRawResponse:
    def __init__(self, evaluation_configs: EvaluationConfigsResource) -> None:
        self._evaluation_configs = evaluation_configs

        self.create = to_raw_response_wrapper(
            evaluation_configs.create,
        )
        self.retrieve = to_raw_response_wrapper(
            evaluation_configs.retrieve,
        )
        self.list = to_raw_response_wrapper(
            evaluation_configs.list,
        )
        self.delete = to_raw_response_wrapper(
            evaluation_configs.delete,
        )


class AsyncEvaluationConfigsResourceWithRawResponse:
    def __init__(self, evaluation_configs: AsyncEvaluationConfigsResource) -> None:
        self._evaluation_configs = evaluation_configs

        self.create = async_to_raw_response_wrapper(
            evaluation_configs.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            evaluation_configs.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            evaluation_configs.list,
        )
        self.delete = async_to_raw_response_wrapper(
            evaluation_configs.delete,
        )


class EvaluationConfigsResourceWithStreamingResponse:
    def __init__(self, evaluation_configs: EvaluationConfigsResource) -> None:
        self._evaluation_configs = evaluation_configs

        self.create = to_streamed_response_wrapper(
            evaluation_configs.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            evaluation_configs.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            evaluation_configs.list,
        )
        self.delete = to_streamed_response_wrapper(
            evaluation_configs.delete,
        )


class AsyncEvaluationConfigsResourceWithStreamingResponse:
    def __init__(self, evaluation_configs: AsyncEvaluationConfigsResource) -> None:
        self._evaluation_configs = evaluation_configs

        self.create = async_to_streamed_response_wrapper(
            evaluation_configs.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            evaluation_configs.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            evaluation_configs.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            evaluation_configs.delete,
        )
