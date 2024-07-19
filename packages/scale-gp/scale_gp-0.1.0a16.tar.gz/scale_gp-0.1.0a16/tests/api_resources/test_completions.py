# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from scale_gp import SGPClient, AsyncSGPClient
from tests.utils import assert_matches_type
from scale_gp.types import CreateCompletionResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCompletions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: SGPClient) -> None:
        completion = client.completions.create(
            model="gpt-4",
            prompt="prompt",
        )
        assert_matches_type(CreateCompletionResponse, completion, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: SGPClient) -> None:
        completion = client.completions.create(
            model="gpt-4",
            prompt="prompt",
            account_id="account_id",
            images=[
                {
                    "image_url": "image_url",
                    "detail": "detail",
                },
                {
                    "image_url": "image_url",
                    "detail": "detail",
                },
                {
                    "image_url": "image_url",
                    "detail": "detail",
                },
            ],
            model_parameters={
                "temperature": 0,
                "stop_sequences": ["string", "string", "string"],
                "max_tokens": 0,
                "top_p": 0,
                "top_k": 0,
                "frequency_penalty": 0,
                "presence_penalty": 0,
            },
            stream=True,
        )
        assert_matches_type(CreateCompletionResponse, completion, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: SGPClient) -> None:
        response = client.completions.with_raw_response.create(
            model="gpt-4",
            prompt="prompt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        completion = response.parse()
        assert_matches_type(CreateCompletionResponse, completion, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: SGPClient) -> None:
        with client.completions.with_streaming_response.create(
            model="gpt-4",
            prompt="prompt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            completion = response.parse()
            assert_matches_type(CreateCompletionResponse, completion, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncCompletions:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncSGPClient) -> None:
        completion = await async_client.completions.create(
            model="gpt-4",
            prompt="prompt",
        )
        assert_matches_type(CreateCompletionResponse, completion, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncSGPClient) -> None:
        completion = await async_client.completions.create(
            model="gpt-4",
            prompt="prompt",
            account_id="account_id",
            images=[
                {
                    "image_url": "image_url",
                    "detail": "detail",
                },
                {
                    "image_url": "image_url",
                    "detail": "detail",
                },
                {
                    "image_url": "image_url",
                    "detail": "detail",
                },
            ],
            model_parameters={
                "temperature": 0,
                "stop_sequences": ["string", "string", "string"],
                "max_tokens": 0,
                "top_p": 0,
                "top_k": 0,
                "frequency_penalty": 0,
                "presence_penalty": 0,
            },
            stream=True,
        )
        assert_matches_type(CreateCompletionResponse, completion, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.completions.with_raw_response.create(
            model="gpt-4",
            prompt="prompt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        completion = await response.parse()
        assert_matches_type(CreateCompletionResponse, completion, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncSGPClient) -> None:
        async with async_client.completions.with_streaming_response.create(
            model="gpt-4",
            prompt="prompt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            completion = await response.parse()
            assert_matches_type(CreateCompletionResponse, completion, path=["response"])

        assert cast(Any, response.is_closed) is True
