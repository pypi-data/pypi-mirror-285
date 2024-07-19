# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import overload
from typing_extensions import Literal

import httpx

from ..types import (
    application_spec_list_params,
    application_spec_create_params,
    application_spec_update_params,
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
from ..types.application_spec_response import ApplicationSpecResponse
from ..types.application_spec_list_response import ApplicationSpecListResponse

__all__ = ["ApplicationSpecsResource", "AsyncApplicationSpecsResource"]


class ApplicationSpecsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ApplicationSpecsResourceWithRawResponse:
        return ApplicationSpecsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ApplicationSpecsResourceWithStreamingResponse:
        return ApplicationSpecsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        account_id: str,
        description: str,
        name: str,
        run_online_evaluation: bool | NotGiven = NOT_GIVEN,
        theme_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationSpecResponse:
        """
        ### Description

        Creates a application spec

        ### Details

        This API can be used to create a application spec. To use this API, review the
        request schema and pass in all fields that are required to create a application
        spec.

        Args:
          account_id: The ID of the account that owns the given entity.

          description: The description of the Application Spec

          name: The name of the Application Spec

          run_online_evaluation: Whether the application spec should run online evaluation, default is `false`

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v4/application-specs",
            body=maybe_transform(
                {
                    "account_id": account_id,
                    "description": description,
                    "name": name,
                    "run_online_evaluation": run_online_evaluation,
                    "theme_id": theme_id,
                },
                application_spec_create_params.ApplicationSpecCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApplicationSpecResponse,
        )

    def retrieve(
        self,
        application_spec_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationSpecResponse:
        """
        ### Description

        Gets the details of a application spec

        ### Details

        This API can be used to get information about a single application spec by ID.
        To use this API, pass in the `id` that was returned from your Create Application
        Spec API call as a path parameter.

        Review the response schema to see the fields that will be returned.

        Args:
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
            f"/v4/application-specs/{application_spec_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApplicationSpecResponse,
        )

    @overload
    def update(
        self,
        application_spec_id: str,
        *,
        description: str | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        restore: Literal[False] | NotGiven = NOT_GIVEN,
        run_online_evaluation: bool | NotGiven = NOT_GIVEN,
        theme_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationSpecResponse:
        """
        ### Description

        Updates a application spec

        ### Details

        This API can be used to update the application spec that matches the ID that was
        passed in as a path parameter. To use this API, pass in the `id` that was
        returned from your Create Application Spec API call as a path parameter.

        Review the request schema to see the fields that can be updated.

        Args:
          description: The description of the Application Spec

          name: The name of the Application Spec

          restore: Set to true to restore the entity from the database.

          run_online_evaluation: Whether the application spec should run online evaluation, default is `false`

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def update(
        self,
        application_spec_id: str,
        *,
        restore: Literal[True],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationSpecResponse:
        """
        ### Description

        Updates a application spec

        ### Details

        This API can be used to update the application spec that matches the ID that was
        passed in as a path parameter. To use this API, pass in the `id` that was
        returned from your Create Application Spec API call as a path parameter.

        Review the request schema to see the fields that can be updated.

        Args:
          restore: Set to true to restore the entity from the database.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    def update(
        self,
        application_spec_id: str,
        *,
        description: str | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        restore: Literal[False] | Literal[True] | NotGiven = NOT_GIVEN,
        run_online_evaluation: bool | NotGiven = NOT_GIVEN,
        theme_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationSpecResponse:
        if not application_spec_id:
            raise ValueError(
                f"Expected a non-empty value for `application_spec_id` but received {application_spec_id!r}"
            )
        return self._patch(
            f"/v4/application-specs/{application_spec_id}",
            body=maybe_transform(
                {
                    "description": description,
                    "name": name,
                    "restore": restore,
                    "run_online_evaluation": run_online_evaluation,
                    "theme_id": theme_id,
                },
                application_spec_update_params.ApplicationSpecUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApplicationSpecResponse,
        )

    def list(
        self,
        *,
        account_id: str | NotGiven = NOT_GIVEN,
        include_archived: bool | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationSpecListResponse:
        """
        ### Description

        Lists all application specs accessible to the user.

        ### Details

        This API can be used to list application specs. If a user has access to multiple
        accounts, all application specs from all accounts the user is associated with
        will be returned.

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
            "/v4/application-specs",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "account_id": account_id,
                        "include_archived": include_archived,
                        "limit": limit,
                        "page": page,
                    },
                    application_spec_list_params.ApplicationSpecListParams,
                ),
            ),
            cast_to=ApplicationSpecListResponse,
        )

    def delete(
        self,
        application_spec_id: str,
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

        Deletes a application spec

        ### Details

        This API can be used to delete a application spec by ID. To use this API, pass
        in the `id` that was returned from your Create Application Spec API call as a
        path parameter.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not application_spec_id:
            raise ValueError(
                f"Expected a non-empty value for `application_spec_id` but received {application_spec_id!r}"
            )
        return self._delete(
            f"/v4/application-specs/{application_spec_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )


class AsyncApplicationSpecsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncApplicationSpecsResourceWithRawResponse:
        return AsyncApplicationSpecsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncApplicationSpecsResourceWithStreamingResponse:
        return AsyncApplicationSpecsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        account_id: str,
        description: str,
        name: str,
        run_online_evaluation: bool | NotGiven = NOT_GIVEN,
        theme_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationSpecResponse:
        """
        ### Description

        Creates a application spec

        ### Details

        This API can be used to create a application spec. To use this API, review the
        request schema and pass in all fields that are required to create a application
        spec.

        Args:
          account_id: The ID of the account that owns the given entity.

          description: The description of the Application Spec

          name: The name of the Application Spec

          run_online_evaluation: Whether the application spec should run online evaluation, default is `false`

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v4/application-specs",
            body=await async_maybe_transform(
                {
                    "account_id": account_id,
                    "description": description,
                    "name": name,
                    "run_online_evaluation": run_online_evaluation,
                    "theme_id": theme_id,
                },
                application_spec_create_params.ApplicationSpecCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApplicationSpecResponse,
        )

    async def retrieve(
        self,
        application_spec_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationSpecResponse:
        """
        ### Description

        Gets the details of a application spec

        ### Details

        This API can be used to get information about a single application spec by ID.
        To use this API, pass in the `id` that was returned from your Create Application
        Spec API call as a path parameter.

        Review the response schema to see the fields that will be returned.

        Args:
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
            f"/v4/application-specs/{application_spec_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApplicationSpecResponse,
        )

    @overload
    async def update(
        self,
        application_spec_id: str,
        *,
        description: str | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        restore: Literal[False] | NotGiven = NOT_GIVEN,
        run_online_evaluation: bool | NotGiven = NOT_GIVEN,
        theme_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationSpecResponse:
        """
        ### Description

        Updates a application spec

        ### Details

        This API can be used to update the application spec that matches the ID that was
        passed in as a path parameter. To use this API, pass in the `id` that was
        returned from your Create Application Spec API call as a path parameter.

        Review the request schema to see the fields that can be updated.

        Args:
          description: The description of the Application Spec

          name: The name of the Application Spec

          restore: Set to true to restore the entity from the database.

          run_online_evaluation: Whether the application spec should run online evaluation, default is `false`

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def update(
        self,
        application_spec_id: str,
        *,
        restore: Literal[True],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationSpecResponse:
        """
        ### Description

        Updates a application spec

        ### Details

        This API can be used to update the application spec that matches the ID that was
        passed in as a path parameter. To use this API, pass in the `id` that was
        returned from your Create Application Spec API call as a path parameter.

        Review the request schema to see the fields that can be updated.

        Args:
          restore: Set to true to restore the entity from the database.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    async def update(
        self,
        application_spec_id: str,
        *,
        description: str | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        restore: Literal[False] | Literal[True] | NotGiven = NOT_GIVEN,
        run_online_evaluation: bool | NotGiven = NOT_GIVEN,
        theme_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationSpecResponse:
        if not application_spec_id:
            raise ValueError(
                f"Expected a non-empty value for `application_spec_id` but received {application_spec_id!r}"
            )
        return await self._patch(
            f"/v4/application-specs/{application_spec_id}",
            body=await async_maybe_transform(
                {
                    "description": description,
                    "name": name,
                    "restore": restore,
                    "run_online_evaluation": run_online_evaluation,
                    "theme_id": theme_id,
                },
                application_spec_update_params.ApplicationSpecUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApplicationSpecResponse,
        )

    async def list(
        self,
        *,
        account_id: str | NotGiven = NOT_GIVEN,
        include_archived: bool | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationSpecListResponse:
        """
        ### Description

        Lists all application specs accessible to the user.

        ### Details

        This API can be used to list application specs. If a user has access to multiple
        accounts, all application specs from all accounts the user is associated with
        will be returned.

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
            "/v4/application-specs",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "account_id": account_id,
                        "include_archived": include_archived,
                        "limit": limit,
                        "page": page,
                    },
                    application_spec_list_params.ApplicationSpecListParams,
                ),
            ),
            cast_to=ApplicationSpecListResponse,
        )

    async def delete(
        self,
        application_spec_id: str,
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

        Deletes a application spec

        ### Details

        This API can be used to delete a application spec by ID. To use this API, pass
        in the `id` that was returned from your Create Application Spec API call as a
        path parameter.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not application_spec_id:
            raise ValueError(
                f"Expected a non-empty value for `application_spec_id` but received {application_spec_id!r}"
            )
        return await self._delete(
            f"/v4/application-specs/{application_spec_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )


class ApplicationSpecsResourceWithRawResponse:
    def __init__(self, application_specs: ApplicationSpecsResource) -> None:
        self._application_specs = application_specs

        self.create = to_raw_response_wrapper(
            application_specs.create,
        )
        self.retrieve = to_raw_response_wrapper(
            application_specs.retrieve,
        )
        self.update = to_raw_response_wrapper(
            application_specs.update,
        )
        self.list = to_raw_response_wrapper(
            application_specs.list,
        )
        self.delete = to_raw_response_wrapper(
            application_specs.delete,
        )


class AsyncApplicationSpecsResourceWithRawResponse:
    def __init__(self, application_specs: AsyncApplicationSpecsResource) -> None:
        self._application_specs = application_specs

        self.create = async_to_raw_response_wrapper(
            application_specs.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            application_specs.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            application_specs.update,
        )
        self.list = async_to_raw_response_wrapper(
            application_specs.list,
        )
        self.delete = async_to_raw_response_wrapper(
            application_specs.delete,
        )


class ApplicationSpecsResourceWithStreamingResponse:
    def __init__(self, application_specs: ApplicationSpecsResource) -> None:
        self._application_specs = application_specs

        self.create = to_streamed_response_wrapper(
            application_specs.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            application_specs.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            application_specs.update,
        )
        self.list = to_streamed_response_wrapper(
            application_specs.list,
        )
        self.delete = to_streamed_response_wrapper(
            application_specs.delete,
        )


class AsyncApplicationSpecsResourceWithStreamingResponse:
    def __init__(self, application_specs: AsyncApplicationSpecsResource) -> None:
        self._application_specs = application_specs

        self.create = async_to_streamed_response_wrapper(
            application_specs.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            application_specs.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            application_specs.update,
        )
        self.list = async_to_streamed_response_wrapper(
            application_specs.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            application_specs.delete,
        )
