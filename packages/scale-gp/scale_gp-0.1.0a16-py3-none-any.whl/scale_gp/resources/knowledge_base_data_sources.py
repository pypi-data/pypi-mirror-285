# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import (
    knowledge_base_data_source_list_params,
    knowledge_base_data_source_create_params,
    knowledge_base_data_source_update_params,
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
from ..types.shared.delete_response import DeleteResponse
from ..types.knowledge_base_data_source_response import KnowledgeBaseDataSourceResponse
from ..types.knowledge_base_data_source_list_response import KnowledgeBaseDataSourceListResponse

__all__ = ["KnowledgeBaseDataSourcesResource", "AsyncKnowledgeBaseDataSourcesResource"]


class KnowledgeBaseDataSourcesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> KnowledgeBaseDataSourcesResourceWithRawResponse:
        return KnowledgeBaseDataSourcesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> KnowledgeBaseDataSourcesResourceWithStreamingResponse:
        return KnowledgeBaseDataSourcesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        account_id: str,
        data_source_config: knowledge_base_data_source_create_params.DataSourceConfig,
        name: str,
        data_source_auth_config: knowledge_base_data_source_create_params.DataSourceAuthConfig | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> KnowledgeBaseDataSourceResponse:
        """
        ### Description

        Creates a knowledge base data source

        ### Details

        This API can be used to create a knowledge base data source. To use this API,
        review the request schema and pass in all fields that are required to create a
        knowledge base data source.

        Args:
          account_id: The ID of the account that owns the given entity.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v4/knowledge-base-data-sources",
            body=maybe_transform(
                {
                    "account_id": account_id,
                    "data_source_config": data_source_config,
                    "name": name,
                    "data_source_auth_config": data_source_auth_config,
                    "description": description,
                },
                knowledge_base_data_source_create_params.KnowledgeBaseDataSourceCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=KnowledgeBaseDataSourceResponse,
        )

    def retrieve(
        self,
        knowledge_base_data_source_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> KnowledgeBaseDataSourceResponse:
        """
        ### Description

        Gets the details of a knowledge base data source

        ### Details

        This API can be used to get information about a single knowledge base data
        source by ID. To use this API, pass in the `id` that was returned from your
        Create Knowledge Base Data Source API call as a path parameter.

        Review the response schema to see the fields that will be returned.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not knowledge_base_data_source_id:
            raise ValueError(
                f"Expected a non-empty value for `knowledge_base_data_source_id` but received {knowledge_base_data_source_id!r}"
            )
        return self._get(
            f"/v4/knowledge-base-data-sources/{knowledge_base_data_source_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=KnowledgeBaseDataSourceResponse,
        )

    def update(
        self,
        knowledge_base_data_source_id: str,
        *,
        data_source_auth_config: knowledge_base_data_source_update_params.DataSourceAuthConfig | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> KnowledgeBaseDataSourceResponse:
        """
        ### Description

        Updates a knowledge base data source

        ### Details

        This API can be used to update the knowledge base data source that matches the
        ID that was passed in as a path parameter. To use this API, pass in the `id`
        that was returned from your Create Knowledge Base Data Source API call as a path
        parameter.

        Review the request schema to see the fields that can be updated.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not knowledge_base_data_source_id:
            raise ValueError(
                f"Expected a non-empty value for `knowledge_base_data_source_id` but received {knowledge_base_data_source_id!r}"
            )
        return self._patch(
            f"/v4/knowledge-base-data-sources/{knowledge_base_data_source_id}",
            body=maybe_transform(
                {
                    "data_source_auth_config": data_source_auth_config,
                    "description": description,
                    "name": name,
                },
                knowledge_base_data_source_update_params.KnowledgeBaseDataSourceUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=KnowledgeBaseDataSourceResponse,
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
    ) -> KnowledgeBaseDataSourceListResponse:
        """
        ### Description

        Lists all knowledge base data sources accessible to the user.

        ### Details

        This API can be used to list knowledge base data sources. If a user has access
        to multiple accounts, all knowledge base data sources from all accounts the user
        is associated with will be returned.

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
            "/v4/knowledge-base-data-sources",
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
                    knowledge_base_data_source_list_params.KnowledgeBaseDataSourceListParams,
                ),
            ),
            cast_to=KnowledgeBaseDataSourceListResponse,
        )

    def delete(
        self,
        knowledge_base_data_source_id: str,
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

        Deletes a knowledge base data source

        ### Details

        This API can be used to delete a knowledge base data source by ID. To use this
        API, pass in the `id` that was returned from your Create Knowledge Base Data
        Source API call as a path parameter.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not knowledge_base_data_source_id:
            raise ValueError(
                f"Expected a non-empty value for `knowledge_base_data_source_id` but received {knowledge_base_data_source_id!r}"
            )
        return self._delete(
            f"/v4/knowledge-base-data-sources/{knowledge_base_data_source_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )

    def verify(
        self,
        knowledge_base_data_source_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Test Knowledge Base Data Source credentials

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not knowledge_base_data_source_id:
            raise ValueError(
                f"Expected a non-empty value for `knowledge_base_data_source_id` but received {knowledge_base_data_source_id!r}"
            )
        return self._post(
            f"/v4/knowledge-base-data-sources/{knowledge_base_data_source_id}/verify",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncKnowledgeBaseDataSourcesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncKnowledgeBaseDataSourcesResourceWithRawResponse:
        return AsyncKnowledgeBaseDataSourcesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncKnowledgeBaseDataSourcesResourceWithStreamingResponse:
        return AsyncKnowledgeBaseDataSourcesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        account_id: str,
        data_source_config: knowledge_base_data_source_create_params.DataSourceConfig,
        name: str,
        data_source_auth_config: knowledge_base_data_source_create_params.DataSourceAuthConfig | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> KnowledgeBaseDataSourceResponse:
        """
        ### Description

        Creates a knowledge base data source

        ### Details

        This API can be used to create a knowledge base data source. To use this API,
        review the request schema and pass in all fields that are required to create a
        knowledge base data source.

        Args:
          account_id: The ID of the account that owns the given entity.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v4/knowledge-base-data-sources",
            body=await async_maybe_transform(
                {
                    "account_id": account_id,
                    "data_source_config": data_source_config,
                    "name": name,
                    "data_source_auth_config": data_source_auth_config,
                    "description": description,
                },
                knowledge_base_data_source_create_params.KnowledgeBaseDataSourceCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=KnowledgeBaseDataSourceResponse,
        )

    async def retrieve(
        self,
        knowledge_base_data_source_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> KnowledgeBaseDataSourceResponse:
        """
        ### Description

        Gets the details of a knowledge base data source

        ### Details

        This API can be used to get information about a single knowledge base data
        source by ID. To use this API, pass in the `id` that was returned from your
        Create Knowledge Base Data Source API call as a path parameter.

        Review the response schema to see the fields that will be returned.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not knowledge_base_data_source_id:
            raise ValueError(
                f"Expected a non-empty value for `knowledge_base_data_source_id` but received {knowledge_base_data_source_id!r}"
            )
        return await self._get(
            f"/v4/knowledge-base-data-sources/{knowledge_base_data_source_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=KnowledgeBaseDataSourceResponse,
        )

    async def update(
        self,
        knowledge_base_data_source_id: str,
        *,
        data_source_auth_config: knowledge_base_data_source_update_params.DataSourceAuthConfig | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> KnowledgeBaseDataSourceResponse:
        """
        ### Description

        Updates a knowledge base data source

        ### Details

        This API can be used to update the knowledge base data source that matches the
        ID that was passed in as a path parameter. To use this API, pass in the `id`
        that was returned from your Create Knowledge Base Data Source API call as a path
        parameter.

        Review the request schema to see the fields that can be updated.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not knowledge_base_data_source_id:
            raise ValueError(
                f"Expected a non-empty value for `knowledge_base_data_source_id` but received {knowledge_base_data_source_id!r}"
            )
        return await self._patch(
            f"/v4/knowledge-base-data-sources/{knowledge_base_data_source_id}",
            body=await async_maybe_transform(
                {
                    "data_source_auth_config": data_source_auth_config,
                    "description": description,
                    "name": name,
                },
                knowledge_base_data_source_update_params.KnowledgeBaseDataSourceUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=KnowledgeBaseDataSourceResponse,
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
    ) -> KnowledgeBaseDataSourceListResponse:
        """
        ### Description

        Lists all knowledge base data sources accessible to the user.

        ### Details

        This API can be used to list knowledge base data sources. If a user has access
        to multiple accounts, all knowledge base data sources from all accounts the user
        is associated with will be returned.

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
            "/v4/knowledge-base-data-sources",
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
                    knowledge_base_data_source_list_params.KnowledgeBaseDataSourceListParams,
                ),
            ),
            cast_to=KnowledgeBaseDataSourceListResponse,
        )

    async def delete(
        self,
        knowledge_base_data_source_id: str,
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

        Deletes a knowledge base data source

        ### Details

        This API can be used to delete a knowledge base data source by ID. To use this
        API, pass in the `id` that was returned from your Create Knowledge Base Data
        Source API call as a path parameter.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not knowledge_base_data_source_id:
            raise ValueError(
                f"Expected a non-empty value for `knowledge_base_data_source_id` but received {knowledge_base_data_source_id!r}"
            )
        return await self._delete(
            f"/v4/knowledge-base-data-sources/{knowledge_base_data_source_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )

    async def verify(
        self,
        knowledge_base_data_source_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Test Knowledge Base Data Source credentials

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not knowledge_base_data_source_id:
            raise ValueError(
                f"Expected a non-empty value for `knowledge_base_data_source_id` but received {knowledge_base_data_source_id!r}"
            )
        return await self._post(
            f"/v4/knowledge-base-data-sources/{knowledge_base_data_source_id}/verify",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class KnowledgeBaseDataSourcesResourceWithRawResponse:
    def __init__(self, knowledge_base_data_sources: KnowledgeBaseDataSourcesResource) -> None:
        self._knowledge_base_data_sources = knowledge_base_data_sources

        self.create = to_raw_response_wrapper(
            knowledge_base_data_sources.create,
        )
        self.retrieve = to_raw_response_wrapper(
            knowledge_base_data_sources.retrieve,
        )
        self.update = to_raw_response_wrapper(
            knowledge_base_data_sources.update,
        )
        self.list = to_raw_response_wrapper(
            knowledge_base_data_sources.list,
        )
        self.delete = to_raw_response_wrapper(
            knowledge_base_data_sources.delete,
        )
        self.verify = to_raw_response_wrapper(
            knowledge_base_data_sources.verify,
        )


class AsyncKnowledgeBaseDataSourcesResourceWithRawResponse:
    def __init__(self, knowledge_base_data_sources: AsyncKnowledgeBaseDataSourcesResource) -> None:
        self._knowledge_base_data_sources = knowledge_base_data_sources

        self.create = async_to_raw_response_wrapper(
            knowledge_base_data_sources.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            knowledge_base_data_sources.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            knowledge_base_data_sources.update,
        )
        self.list = async_to_raw_response_wrapper(
            knowledge_base_data_sources.list,
        )
        self.delete = async_to_raw_response_wrapper(
            knowledge_base_data_sources.delete,
        )
        self.verify = async_to_raw_response_wrapper(
            knowledge_base_data_sources.verify,
        )


class KnowledgeBaseDataSourcesResourceWithStreamingResponse:
    def __init__(self, knowledge_base_data_sources: KnowledgeBaseDataSourcesResource) -> None:
        self._knowledge_base_data_sources = knowledge_base_data_sources

        self.create = to_streamed_response_wrapper(
            knowledge_base_data_sources.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            knowledge_base_data_sources.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            knowledge_base_data_sources.update,
        )
        self.list = to_streamed_response_wrapper(
            knowledge_base_data_sources.list,
        )
        self.delete = to_streamed_response_wrapper(
            knowledge_base_data_sources.delete,
        )
        self.verify = to_streamed_response_wrapper(
            knowledge_base_data_sources.verify,
        )


class AsyncKnowledgeBaseDataSourcesResourceWithStreamingResponse:
    def __init__(self, knowledge_base_data_sources: AsyncKnowledgeBaseDataSourcesResource) -> None:
        self._knowledge_base_data_sources = knowledge_base_data_sources

        self.create = async_to_streamed_response_wrapper(
            knowledge_base_data_sources.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            knowledge_base_data_sources.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            knowledge_base_data_sources.update,
        )
        self.list = async_to_streamed_response_wrapper(
            knowledge_base_data_sources.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            knowledge_base_data_sources.delete,
        )
        self.verify = async_to_streamed_response_wrapper(
            knowledge_base_data_sources.verify,
        )
