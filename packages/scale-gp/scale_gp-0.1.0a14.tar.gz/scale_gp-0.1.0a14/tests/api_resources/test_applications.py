# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from scale_gp import SGPClient, AsyncSGPClient
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestApplications:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_process(self, client: SGPClient) -> None:
        application = client.applications.process(
            edges=[
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
            ],
            inputs={"foo": {}},
            nodes=[
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
            ],
            version="V0",
        )
        assert_matches_type(object, application, path=["response"])

    @parametrize
    def test_method_process_with_all_params(self, client: SGPClient) -> None:
        application = client.applications.process(
            edges=[
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
            ],
            inputs={"foo": {}},
            nodes=[
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                    "configuration": {"foo": {"value": {}}},
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                    "configuration": {"foo": {"value": {}}},
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                    "configuration": {"foo": {"value": {}}},
                },
            ],
            version="V0",
            history=[
                {
                    "request": "request",
                    "response": "response",
                    "session_data": {},
                },
                {
                    "request": "request",
                    "response": "response",
                    "session_data": {},
                },
                {
                    "request": "request",
                    "response": "response",
                    "session_data": {},
                },
            ],
            overrides={
                "foo": {
                    "type": "knowledge_base_schema",
                    "artifact_ids_filter": ["string", "string", "string"],
                }
            },
        )
        assert_matches_type(object, application, path=["response"])

    @parametrize
    def test_raw_response_process(self, client: SGPClient) -> None:
        response = client.applications.with_raw_response.process(
            edges=[
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
            ],
            inputs={"foo": {}},
            nodes=[
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
            ],
            version="V0",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        application = response.parse()
        assert_matches_type(object, application, path=["response"])

    @parametrize
    def test_streaming_response_process(self, client: SGPClient) -> None:
        with client.applications.with_streaming_response.process(
            edges=[
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
            ],
            inputs={"foo": {}},
            nodes=[
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
            ],
            version="V0",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            application = response.parse()
            assert_matches_type(object, application, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_validate(self, client: SGPClient) -> None:
        application = client.applications.validate(
            edges=[
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
            ],
            nodes=[
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
            ],
            version="V0",
        )
        assert_matches_type(object, application, path=["response"])

    @parametrize
    def test_method_validate_with_all_params(self, client: SGPClient) -> None:
        application = client.applications.validate(
            edges=[
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
            ],
            nodes=[
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                    "configuration": {"foo": {"value": {}}},
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                    "configuration": {"foo": {"value": {}}},
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                    "configuration": {"foo": {"value": {}}},
                },
            ],
            version="V0",
            overrides={
                "foo": {
                    "type": "knowledge_base_schema",
                    "artifact_ids_filter": ["string", "string", "string"],
                }
            },
        )
        assert_matches_type(object, application, path=["response"])

    @parametrize
    def test_raw_response_validate(self, client: SGPClient) -> None:
        response = client.applications.with_raw_response.validate(
            edges=[
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
            ],
            nodes=[
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
            ],
            version="V0",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        application = response.parse()
        assert_matches_type(object, application, path=["response"])

    @parametrize
    def test_streaming_response_validate(self, client: SGPClient) -> None:
        with client.applications.with_streaming_response.validate(
            edges=[
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
            ],
            nodes=[
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
            ],
            version="V0",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            application = response.parse()
            assert_matches_type(object, application, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncApplications:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_process(self, async_client: AsyncSGPClient) -> None:
        application = await async_client.applications.process(
            edges=[
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
            ],
            inputs={"foo": {}},
            nodes=[
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
            ],
            version="V0",
        )
        assert_matches_type(object, application, path=["response"])

    @parametrize
    async def test_method_process_with_all_params(self, async_client: AsyncSGPClient) -> None:
        application = await async_client.applications.process(
            edges=[
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
            ],
            inputs={"foo": {}},
            nodes=[
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                    "configuration": {"foo": {"value": {}}},
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                    "configuration": {"foo": {"value": {}}},
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                    "configuration": {"foo": {"value": {}}},
                },
            ],
            version="V0",
            history=[
                {
                    "request": "request",
                    "response": "response",
                    "session_data": {},
                },
                {
                    "request": "request",
                    "response": "response",
                    "session_data": {},
                },
                {
                    "request": "request",
                    "response": "response",
                    "session_data": {},
                },
            ],
            overrides={
                "foo": {
                    "type": "knowledge_base_schema",
                    "artifact_ids_filter": ["string", "string", "string"],
                }
            },
        )
        assert_matches_type(object, application, path=["response"])

    @parametrize
    async def test_raw_response_process(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.applications.with_raw_response.process(
            edges=[
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
            ],
            inputs={"foo": {}},
            nodes=[
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
            ],
            version="V0",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        application = await response.parse()
        assert_matches_type(object, application, path=["response"])

    @parametrize
    async def test_streaming_response_process(self, async_client: AsyncSGPClient) -> None:
        async with async_client.applications.with_streaming_response.process(
            edges=[
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
            ],
            inputs={"foo": {}},
            nodes=[
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
            ],
            version="V0",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            application = await response.parse()
            assert_matches_type(object, application, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_validate(self, async_client: AsyncSGPClient) -> None:
        application = await async_client.applications.validate(
            edges=[
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
            ],
            nodes=[
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
            ],
            version="V0",
        )
        assert_matches_type(object, application, path=["response"])

    @parametrize
    async def test_method_validate_with_all_params(self, async_client: AsyncSGPClient) -> None:
        application = await async_client.applications.validate(
            edges=[
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
            ],
            nodes=[
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                    "configuration": {"foo": {"value": {}}},
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                    "configuration": {"foo": {"value": {}}},
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                    "configuration": {"foo": {"value": {}}},
                },
            ],
            version="V0",
            overrides={
                "foo": {
                    "type": "knowledge_base_schema",
                    "artifact_ids_filter": ["string", "string", "string"],
                }
            },
        )
        assert_matches_type(object, application, path=["response"])

    @parametrize
    async def test_raw_response_validate(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.applications.with_raw_response.validate(
            edges=[
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
            ],
            nodes=[
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
            ],
            version="V0",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        application = await response.parse()
        assert_matches_type(object, application, path=["response"])

    @parametrize
    async def test_streaming_response_validate(self, async_client: AsyncSGPClient) -> None:
        async with async_client.applications.with_streaming_response.validate(
            edges=[
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
                {
                    "from_node": "from_node",
                    "to_node": "to_node",
                    "from_field": "from_field",
                    "to_field": "to_field",
                },
            ],
            nodes=[
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
                {
                    "id": "id",
                    "application_node_schema_id": "text_input_schema",
                },
            ],
            version="V0",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            application = await response.parse()
            assert_matches_type(object, application, path=["response"])

        assert cast(Any, response.is_closed) is True
