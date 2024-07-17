# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

import httpx

from ..types import question_set_list_params, question_set_create_params
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
from ..types.question_set_response import QuestionSetResponse
from ..types.question_set_list_response import QuestionSetListResponse
from ..types.question_set_with_questions import QuestionSetWithQuestions

__all__ = ["QuestionSetsResource", "AsyncQuestionSetsResource"]


class QuestionSetsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> QuestionSetsResourceWithRawResponse:
        return QuestionSetsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> QuestionSetsResourceWithStreamingResponse:
        return QuestionSetsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        account_id: str,
        name: str,
        question_ids: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QuestionSetResponse:
        """
        ### Description

        Creates a question set

        ### Details

        This API can be used to create a question set. To use this API, review the
        request schema and pass in all fields that are required to create a question
        set.

        Args:
          account_id: The ID of the account that owns the given entity.

          question_ids: IDs of questions in the question set

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v4/question-sets",
            body=maybe_transform(
                {
                    "account_id": account_id,
                    "name": name,
                    "question_ids": question_ids,
                },
                question_set_create_params.QuestionSetCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuestionSetResponse,
        )

    def retrieve(
        self,
        question_set_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QuestionSetWithQuestions:
        """
        Get Question Set

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not question_set_id:
            raise ValueError(f"Expected a non-empty value for `question_set_id` but received {question_set_id!r}")
        return self._get(
            f"/v4/question-sets/{question_set_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuestionSetWithQuestions,
        )

    def list(
        self,
        *,
        account_id: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        view: List[Literal["Questions"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QuestionSetListResponse:
        """
        ### Description

        Lists all question sets accessible to the user.

        ### Details

        This API can be used to list question sets. If a user has access to multiple
        accounts, all question sets from all accounts the user is associated with will
        be returned.

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
            "/v4/question-sets",
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
                        "view": view,
                    },
                    question_set_list_params.QuestionSetListParams,
                ),
            ),
            cast_to=QuestionSetListResponse,
        )


class AsyncQuestionSetsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncQuestionSetsResourceWithRawResponse:
        return AsyncQuestionSetsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncQuestionSetsResourceWithStreamingResponse:
        return AsyncQuestionSetsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        account_id: str,
        name: str,
        question_ids: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QuestionSetResponse:
        """
        ### Description

        Creates a question set

        ### Details

        This API can be used to create a question set. To use this API, review the
        request schema and pass in all fields that are required to create a question
        set.

        Args:
          account_id: The ID of the account that owns the given entity.

          question_ids: IDs of questions in the question set

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v4/question-sets",
            body=await async_maybe_transform(
                {
                    "account_id": account_id,
                    "name": name,
                    "question_ids": question_ids,
                },
                question_set_create_params.QuestionSetCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuestionSetResponse,
        )

    async def retrieve(
        self,
        question_set_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QuestionSetWithQuestions:
        """
        Get Question Set

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not question_set_id:
            raise ValueError(f"Expected a non-empty value for `question_set_id` but received {question_set_id!r}")
        return await self._get(
            f"/v4/question-sets/{question_set_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuestionSetWithQuestions,
        )

    async def list(
        self,
        *,
        account_id: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        view: List[Literal["Questions"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QuestionSetListResponse:
        """
        ### Description

        Lists all question sets accessible to the user.

        ### Details

        This API can be used to list question sets. If a user has access to multiple
        accounts, all question sets from all accounts the user is associated with will
        be returned.

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
            "/v4/question-sets",
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
                        "view": view,
                    },
                    question_set_list_params.QuestionSetListParams,
                ),
            ),
            cast_to=QuestionSetListResponse,
        )


class QuestionSetsResourceWithRawResponse:
    def __init__(self, question_sets: QuestionSetsResource) -> None:
        self._question_sets = question_sets

        self.create = to_raw_response_wrapper(
            question_sets.create,
        )
        self.retrieve = to_raw_response_wrapper(
            question_sets.retrieve,
        )
        self.list = to_raw_response_wrapper(
            question_sets.list,
        )


class AsyncQuestionSetsResourceWithRawResponse:
    def __init__(self, question_sets: AsyncQuestionSetsResource) -> None:
        self._question_sets = question_sets

        self.create = async_to_raw_response_wrapper(
            question_sets.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            question_sets.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            question_sets.list,
        )


class QuestionSetsResourceWithStreamingResponse:
    def __init__(self, question_sets: QuestionSetsResource) -> None:
        self._question_sets = question_sets

        self.create = to_streamed_response_wrapper(
            question_sets.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            question_sets.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            question_sets.list,
        )


class AsyncQuestionSetsResourceWithStreamingResponse:
    def __init__(self, question_sets: AsyncQuestionSetsResource) -> None:
        self._question_sets = question_sets

        self.create = async_to_streamed_response_wrapper(
            question_sets.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            question_sets.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            question_sets.list,
        )
