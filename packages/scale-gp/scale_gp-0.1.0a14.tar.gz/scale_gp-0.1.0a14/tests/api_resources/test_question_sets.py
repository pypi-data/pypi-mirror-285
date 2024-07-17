# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from scale_gp import SGPClient, AsyncSGPClient
from tests.utils import assert_matches_type
from scale_gp.types import (
    QuestionSetResponse,
    QuestionSetListResponse,
    QuestionSetWithQuestions,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestQuestionSets:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: SGPClient) -> None:
        question_set = client.question_sets.create(
            account_id="account_id",
            name="name",
            question_ids=["string", "string", "string"],
        )
        assert_matches_type(QuestionSetResponse, question_set, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: SGPClient) -> None:
        response = client.question_sets.with_raw_response.create(
            account_id="account_id",
            name="name",
            question_ids=["string", "string", "string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        question_set = response.parse()
        assert_matches_type(QuestionSetResponse, question_set, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: SGPClient) -> None:
        with client.question_sets.with_streaming_response.create(
            account_id="account_id",
            name="name",
            question_ids=["string", "string", "string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            question_set = response.parse()
            assert_matches_type(QuestionSetResponse, question_set, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: SGPClient) -> None:
        question_set = client.question_sets.retrieve(
            "question_set_id",
        )
        assert_matches_type(QuestionSetWithQuestions, question_set, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: SGPClient) -> None:
        response = client.question_sets.with_raw_response.retrieve(
            "question_set_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        question_set = response.parse()
        assert_matches_type(QuestionSetWithQuestions, question_set, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: SGPClient) -> None:
        with client.question_sets.with_streaming_response.retrieve(
            "question_set_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            question_set = response.parse()
            assert_matches_type(QuestionSetWithQuestions, question_set, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: SGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `question_set_id` but received ''"):
            client.question_sets.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_list(self, client: SGPClient) -> None:
        question_set = client.question_sets.list()
        assert_matches_type(QuestionSetListResponse, question_set, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: SGPClient) -> None:
        question_set = client.question_sets.list(
            account_id="account_id",
            limit=1,
            page=1,
            view=["Questions"],
        )
        assert_matches_type(QuestionSetListResponse, question_set, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: SGPClient) -> None:
        response = client.question_sets.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        question_set = response.parse()
        assert_matches_type(QuestionSetListResponse, question_set, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: SGPClient) -> None:
        with client.question_sets.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            question_set = response.parse()
            assert_matches_type(QuestionSetListResponse, question_set, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncQuestionSets:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncSGPClient) -> None:
        question_set = await async_client.question_sets.create(
            account_id="account_id",
            name="name",
            question_ids=["string", "string", "string"],
        )
        assert_matches_type(QuestionSetResponse, question_set, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.question_sets.with_raw_response.create(
            account_id="account_id",
            name="name",
            question_ids=["string", "string", "string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        question_set = await response.parse()
        assert_matches_type(QuestionSetResponse, question_set, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncSGPClient) -> None:
        async with async_client.question_sets.with_streaming_response.create(
            account_id="account_id",
            name="name",
            question_ids=["string", "string", "string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            question_set = await response.parse()
            assert_matches_type(QuestionSetResponse, question_set, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncSGPClient) -> None:
        question_set = await async_client.question_sets.retrieve(
            "question_set_id",
        )
        assert_matches_type(QuestionSetWithQuestions, question_set, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.question_sets.with_raw_response.retrieve(
            "question_set_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        question_set = await response.parse()
        assert_matches_type(QuestionSetWithQuestions, question_set, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncSGPClient) -> None:
        async with async_client.question_sets.with_streaming_response.retrieve(
            "question_set_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            question_set = await response.parse()
            assert_matches_type(QuestionSetWithQuestions, question_set, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncSGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `question_set_id` but received ''"):
            await async_client.question_sets.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncSGPClient) -> None:
        question_set = await async_client.question_sets.list()
        assert_matches_type(QuestionSetListResponse, question_set, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncSGPClient) -> None:
        question_set = await async_client.question_sets.list(
            account_id="account_id",
            limit=1,
            page=1,
            view=["Questions"],
        )
        assert_matches_type(QuestionSetListResponse, question_set, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.question_sets.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        question_set = await response.parse()
        assert_matches_type(QuestionSetListResponse, question_set, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncSGPClient) -> None:
        async with async_client.question_sets.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            question_set = await response.parse()
            assert_matches_type(QuestionSetListResponse, question_set, path=["response"])

        assert cast(Any, response.is_closed) is True
