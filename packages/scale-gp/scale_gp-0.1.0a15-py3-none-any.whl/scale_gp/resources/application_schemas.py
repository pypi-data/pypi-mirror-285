# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import application_schema_list_params
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
from ..types.application_schema_list_response import ApplicationSchemaListResponse

__all__ = ["ApplicationSchemasResource", "AsyncApplicationSchemasResource"]


class ApplicationSchemasResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ApplicationSchemasResourceWithRawResponse:
        return ApplicationSchemasResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ApplicationSchemasResourceWithStreamingResponse:
        return ApplicationSchemasResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        version: Literal["OFFLINE", "V0"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationSchemaListResponse:
        """
        Get Application Schemas

        Args:
          version: An enum representing the version states of an application and its nodes'
              schemas. Attributes: V0: The initial version of an application schema.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v4/application-schemas",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"version": version}, application_schema_list_params.ApplicationSchemaListParams),
            ),
            cast_to=ApplicationSchemaListResponse,
        )


class AsyncApplicationSchemasResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncApplicationSchemasResourceWithRawResponse:
        return AsyncApplicationSchemasResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncApplicationSchemasResourceWithStreamingResponse:
        return AsyncApplicationSchemasResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        version: Literal["OFFLINE", "V0"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationSchemaListResponse:
        """
        Get Application Schemas

        Args:
          version: An enum representing the version states of an application and its nodes'
              schemas. Attributes: V0: The initial version of an application schema.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v4/application-schemas",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"version": version}, application_schema_list_params.ApplicationSchemaListParams
                ),
            ),
            cast_to=ApplicationSchemaListResponse,
        )


class ApplicationSchemasResourceWithRawResponse:
    def __init__(self, application_schemas: ApplicationSchemasResource) -> None:
        self._application_schemas = application_schemas

        self.list = to_raw_response_wrapper(
            application_schemas.list,
        )


class AsyncApplicationSchemasResourceWithRawResponse:
    def __init__(self, application_schemas: AsyncApplicationSchemasResource) -> None:
        self._application_schemas = application_schemas

        self.list = async_to_raw_response_wrapper(
            application_schemas.list,
        )


class ApplicationSchemasResourceWithStreamingResponse:
    def __init__(self, application_schemas: ApplicationSchemasResource) -> None:
        self._application_schemas = application_schemas

        self.list = to_streamed_response_wrapper(
            application_schemas.list,
        )


class AsyncApplicationSchemasResourceWithStreamingResponse:
    def __init__(self, application_schemas: AsyncApplicationSchemasResource) -> None:
        self._application_schemas = application_schemas

        self.list = async_to_streamed_response_wrapper(
            application_schemas.list,
        )
