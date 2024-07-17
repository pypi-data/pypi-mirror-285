# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from scale_gp import SGPClient, AsyncSGPClient
from tests.utils import assert_matches_type
from scale_gp.types.applications.variant import ChatThreadHistory, ApplicationInteraction

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMessages:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_update(self, client: SGPClient) -> None:
        message = client.threads.messages.update(
            application_interaction_id="application_interaction_id",
            thread_id="thread_id",
        )
        assert_matches_type(ApplicationInteraction, message, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: SGPClient) -> None:
        message = client.threads.messages.update(
            application_interaction_id="application_interaction_id",
            thread_id="thread_id",
            output_text="output_text",
        )
        assert_matches_type(ApplicationInteraction, message, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: SGPClient) -> None:
        response = client.threads.messages.with_raw_response.update(
            application_interaction_id="application_interaction_id",
            thread_id="thread_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(ApplicationInteraction, message, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: SGPClient) -> None:
        with client.threads.messages.with_streaming_response.update(
            application_interaction_id="application_interaction_id",
            thread_id="thread_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = response.parse()
            assert_matches_type(ApplicationInteraction, message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: SGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            client.threads.messages.with_raw_response.update(
                application_interaction_id="application_interaction_id",
                thread_id="",
            )

        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `application_interaction_id` but received ''"
        ):
            client.threads.messages.with_raw_response.update(
                application_interaction_id="",
                thread_id="thread_id",
            )

    @parametrize
    def test_method_list(self, client: SGPClient) -> None:
        message = client.threads.messages.list(
            "thread_id",
        )
        assert_matches_type(ChatThreadHistory, message, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: SGPClient) -> None:
        response = client.threads.messages.with_raw_response.list(
            "thread_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(ChatThreadHistory, message, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: SGPClient) -> None:
        with client.threads.messages.with_streaming_response.list(
            "thread_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = response.parse()
            assert_matches_type(ChatThreadHistory, message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: SGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            client.threads.messages.with_raw_response.list(
                "",
            )


class TestAsyncMessages:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_update(self, async_client: AsyncSGPClient) -> None:
        message = await async_client.threads.messages.update(
            application_interaction_id="application_interaction_id",
            thread_id="thread_id",
        )
        assert_matches_type(ApplicationInteraction, message, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncSGPClient) -> None:
        message = await async_client.threads.messages.update(
            application_interaction_id="application_interaction_id",
            thread_id="thread_id",
            output_text="output_text",
        )
        assert_matches_type(ApplicationInteraction, message, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.threads.messages.with_raw_response.update(
            application_interaction_id="application_interaction_id",
            thread_id="thread_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = await response.parse()
        assert_matches_type(ApplicationInteraction, message, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncSGPClient) -> None:
        async with async_client.threads.messages.with_streaming_response.update(
            application_interaction_id="application_interaction_id",
            thread_id="thread_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = await response.parse()
            assert_matches_type(ApplicationInteraction, message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncSGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await async_client.threads.messages.with_raw_response.update(
                application_interaction_id="application_interaction_id",
                thread_id="",
            )

        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `application_interaction_id` but received ''"
        ):
            await async_client.threads.messages.with_raw_response.update(
                application_interaction_id="",
                thread_id="thread_id",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncSGPClient) -> None:
        message = await async_client.threads.messages.list(
            "thread_id",
        )
        assert_matches_type(ChatThreadHistory, message, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.threads.messages.with_raw_response.list(
            "thread_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = await response.parse()
        assert_matches_type(ChatThreadHistory, message, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncSGPClient) -> None:
        async with async_client.threads.messages.with_streaming_response.list(
            "thread_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = await response.parse()
            assert_matches_type(ChatThreadHistory, message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncSGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await async_client.threads.messages.with_raw_response.list(
                "",
            )
