# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, Union, cast, overload
from typing_extensions import Literal

import httpx

from ..types import application_variant_list_params, application_variant_create_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import (
    required_args,
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
from ..types.application_variant_list_response import ApplicationVariantListResponse
from ..types.application_variant_create_response import ApplicationVariantCreateResponse
from ..types.application_variant_retrieve_response import ApplicationVariantRetrieveResponse

__all__ = ["ApplicationVariantsResource", "AsyncApplicationVariantsResource"]


class ApplicationVariantsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ApplicationVariantsResourceWithRawResponse:
        return ApplicationVariantsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ApplicationVariantsResourceWithStreamingResponse:
        return ApplicationVariantsResourceWithStreamingResponse(self)

    @overload
    def create(
        self,
        *,
        account_id: str,
        application_spec_id: str,
        configuration: application_variant_create_params.OnlineApplicationVariantRequestConfiguration,
        name: str,
        version: Literal["V0"],
        description: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationVariantCreateResponse:
        """
        ### Description

        Creates a application variant

        ### Details

        This API can be used to create a application variant. To use this API, review
        the request schema and pass in all fields that are required to create a
        application variant.

        Args:
          account_id: The ID of the account that owns the given entity.

          description: Optional description of the application variant

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        *,
        account_id: str,
        application_spec_id: str,
        configuration: application_variant_create_params.OfflineApplicationVariantRequestConfiguration,
        name: str,
        version: Literal["OFFLINE"],
        description: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationVariantCreateResponse:
        """
        ### Description

        Creates a application variant

        ### Details

        This API can be used to create a application variant. To use this API, review
        the request schema and pass in all fields that are required to create a
        application variant.

        Args:
          account_id: The ID of the account that owns the given entity.

          description: Optional description of the application variant

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["account_id", "application_spec_id", "configuration", "name", "version"])
    def create(
        self,
        *,
        account_id: str,
        application_spec_id: str,
        configuration: application_variant_create_params.OnlineApplicationVariantRequestConfiguration
        | application_variant_create_params.OfflineApplicationVariantRequestConfiguration,
        name: str,
        version: Literal["V0"] | Literal["OFFLINE"],
        description: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationVariantCreateResponse:
        return cast(
            ApplicationVariantCreateResponse,
            self._post(
                "/v4/application-variants",
                body=maybe_transform(
                    {
                        "account_id": account_id,
                        "application_spec_id": application_spec_id,
                        "configuration": configuration,
                        "name": name,
                        "version": version,
                        "description": description,
                    },
                    application_variant_create_params.ApplicationVariantCreateParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ApplicationVariantCreateResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def retrieve(
        self,
        application_variant_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationVariantRetrieveResponse:
        """
        ### Description

        Gets the details of a application variant

        ### Details

        This API can be used to get information about a single application variant by
        ID. To use this API, pass in the `id` that was returned from your Create
        Application Variant API call as a path parameter.

        Review the response schema to see the fields that will be returned.

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
        return cast(
            ApplicationVariantRetrieveResponse,
            self._get(
                f"/v4/application-variants/{application_variant_id}",
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ApplicationVariantRetrieveResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def list(
        self,
        *,
        account_id: str | NotGiven = NOT_GIVEN,
        application_spec_id: Union[int, str] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationVariantListResponse:
        """
        ### Description

        Lists all application variants accessible to the user.

        ### Details

        This API can be used to list application variants. If a user has access to
        multiple accounts, all application variants from all accounts the user is
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
            "/v4/application-variants",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "account_id": account_id,
                        "application_spec_id": application_spec_id,
                        "limit": limit,
                        "page": page,
                    },
                    application_variant_list_params.ApplicationVariantListParams,
                ),
            ),
            cast_to=ApplicationVariantListResponse,
        )

    def delete(
        self,
        application_variant_id: str,
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

        Deletes a application variant

        ### Details

        This API can be used to delete a application variant by ID. To use this API,
        pass in the `id` that was returned from your Create Application Variant API call
        as a path parameter.

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
        return self._delete(
            f"/v4/application-variants/{application_variant_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )


class AsyncApplicationVariantsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncApplicationVariantsResourceWithRawResponse:
        return AsyncApplicationVariantsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncApplicationVariantsResourceWithStreamingResponse:
        return AsyncApplicationVariantsResourceWithStreamingResponse(self)

    @overload
    async def create(
        self,
        *,
        account_id: str,
        application_spec_id: str,
        configuration: application_variant_create_params.OnlineApplicationVariantRequestConfiguration,
        name: str,
        version: Literal["V0"],
        description: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationVariantCreateResponse:
        """
        ### Description

        Creates a application variant

        ### Details

        This API can be used to create a application variant. To use this API, review
        the request schema and pass in all fields that are required to create a
        application variant.

        Args:
          account_id: The ID of the account that owns the given entity.

          description: Optional description of the application variant

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        *,
        account_id: str,
        application_spec_id: str,
        configuration: application_variant_create_params.OfflineApplicationVariantRequestConfiguration,
        name: str,
        version: Literal["OFFLINE"],
        description: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationVariantCreateResponse:
        """
        ### Description

        Creates a application variant

        ### Details

        This API can be used to create a application variant. To use this API, review
        the request schema and pass in all fields that are required to create a
        application variant.

        Args:
          account_id: The ID of the account that owns the given entity.

          description: Optional description of the application variant

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["account_id", "application_spec_id", "configuration", "name", "version"])
    async def create(
        self,
        *,
        account_id: str,
        application_spec_id: str,
        configuration: application_variant_create_params.OnlineApplicationVariantRequestConfiguration
        | application_variant_create_params.OfflineApplicationVariantRequestConfiguration,
        name: str,
        version: Literal["V0"] | Literal["OFFLINE"],
        description: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationVariantCreateResponse:
        return cast(
            ApplicationVariantCreateResponse,
            await self._post(
                "/v4/application-variants",
                body=await async_maybe_transform(
                    {
                        "account_id": account_id,
                        "application_spec_id": application_spec_id,
                        "configuration": configuration,
                        "name": name,
                        "version": version,
                        "description": description,
                    },
                    application_variant_create_params.ApplicationVariantCreateParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ApplicationVariantCreateResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def retrieve(
        self,
        application_variant_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationVariantRetrieveResponse:
        """
        ### Description

        Gets the details of a application variant

        ### Details

        This API can be used to get information about a single application variant by
        ID. To use this API, pass in the `id` that was returned from your Create
        Application Variant API call as a path parameter.

        Review the response schema to see the fields that will be returned.

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
        return cast(
            ApplicationVariantRetrieveResponse,
            await self._get(
                f"/v4/application-variants/{application_variant_id}",
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ApplicationVariantRetrieveResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def list(
        self,
        *,
        account_id: str | NotGiven = NOT_GIVEN,
        application_spec_id: Union[int, str] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationVariantListResponse:
        """
        ### Description

        Lists all application variants accessible to the user.

        ### Details

        This API can be used to list application variants. If a user has access to
        multiple accounts, all application variants from all accounts the user is
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
            "/v4/application-variants",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "account_id": account_id,
                        "application_spec_id": application_spec_id,
                        "limit": limit,
                        "page": page,
                    },
                    application_variant_list_params.ApplicationVariantListParams,
                ),
            ),
            cast_to=ApplicationVariantListResponse,
        )

    async def delete(
        self,
        application_variant_id: str,
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

        Deletes a application variant

        ### Details

        This API can be used to delete a application variant by ID. To use this API,
        pass in the `id` that was returned from your Create Application Variant API call
        as a path parameter.

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
        return await self._delete(
            f"/v4/application-variants/{application_variant_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )


class ApplicationVariantsResourceWithRawResponse:
    def __init__(self, application_variants: ApplicationVariantsResource) -> None:
        self._application_variants = application_variants

        self.create = to_raw_response_wrapper(
            application_variants.create,
        )
        self.retrieve = to_raw_response_wrapper(
            application_variants.retrieve,
        )
        self.list = to_raw_response_wrapper(
            application_variants.list,
        )
        self.delete = to_raw_response_wrapper(
            application_variants.delete,
        )


class AsyncApplicationVariantsResourceWithRawResponse:
    def __init__(self, application_variants: AsyncApplicationVariantsResource) -> None:
        self._application_variants = application_variants

        self.create = async_to_raw_response_wrapper(
            application_variants.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            application_variants.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            application_variants.list,
        )
        self.delete = async_to_raw_response_wrapper(
            application_variants.delete,
        )


class ApplicationVariantsResourceWithStreamingResponse:
    def __init__(self, application_variants: ApplicationVariantsResource) -> None:
        self._application_variants = application_variants

        self.create = to_streamed_response_wrapper(
            application_variants.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            application_variants.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            application_variants.list,
        )
        self.delete = to_streamed_response_wrapper(
            application_variants.delete,
        )


class AsyncApplicationVariantsResourceWithStreamingResponse:
    def __init__(self, application_variants: AsyncApplicationVariantsResource) -> None:
        self._application_variants = application_variants

        self.create = async_to_streamed_response_wrapper(
            application_variants.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            application_variants.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            application_variants.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            application_variants.delete,
        )
