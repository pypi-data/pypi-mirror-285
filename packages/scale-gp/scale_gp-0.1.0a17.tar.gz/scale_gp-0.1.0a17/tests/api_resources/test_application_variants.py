# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from scale_gp import SGPClient, AsyncSGPClient
from tests.utils import assert_matches_type
from scale_gp.types import (
    ApplicationVariantListResponse,
    ApplicationVariantCreateResponse,
    ApplicationVariantRetrieveResponse,
)
from scale_gp.types.shared import DeleteResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestApplicationVariants:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create_overload_1(self, client: SGPClient) -> None:
        application_variant = client.application_variants.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            configuration={
                "nodes": [
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
                "edges": [
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
            },
            name="name",
            version="V0",
        )
        assert_matches_type(ApplicationVariantCreateResponse, application_variant, path=["response"])

    @parametrize
    def test_method_create_with_all_params_overload_1(self, client: SGPClient) -> None:
        application_variant = client.application_variants.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            configuration={
                "nodes": [
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
                "edges": [
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
            },
            name="name",
            version="V0",
            description="description",
        )
        assert_matches_type(ApplicationVariantCreateResponse, application_variant, path=["response"])

    @parametrize
    def test_raw_response_create_overload_1(self, client: SGPClient) -> None:
        response = client.application_variants.with_raw_response.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            configuration={
                "nodes": [
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
                "edges": [
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
            },
            name="name",
            version="V0",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        application_variant = response.parse()
        assert_matches_type(ApplicationVariantCreateResponse, application_variant, path=["response"])

    @parametrize
    def test_streaming_response_create_overload_1(self, client: SGPClient) -> None:
        with client.application_variants.with_streaming_response.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            configuration={
                "nodes": [
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
                "edges": [
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
            },
            name="name",
            version="V0",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            application_variant = response.parse()
            assert_matches_type(ApplicationVariantCreateResponse, application_variant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_create_overload_2(self, client: SGPClient) -> None:
        application_variant = client.application_variants.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            configuration={},
            name="name",
            version="OFFLINE",
        )
        assert_matches_type(ApplicationVariantCreateResponse, application_variant, path=["response"])

    @parametrize
    def test_method_create_with_all_params_overload_2(self, client: SGPClient) -> None:
        application_variant = client.application_variants.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            configuration={
                "output_schema_type": "completion_only",
                "metadata": {},
            },
            name="name",
            version="OFFLINE",
            description="description",
        )
        assert_matches_type(ApplicationVariantCreateResponse, application_variant, path=["response"])

    @parametrize
    def test_raw_response_create_overload_2(self, client: SGPClient) -> None:
        response = client.application_variants.with_raw_response.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            configuration={},
            name="name",
            version="OFFLINE",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        application_variant = response.parse()
        assert_matches_type(ApplicationVariantCreateResponse, application_variant, path=["response"])

    @parametrize
    def test_streaming_response_create_overload_2(self, client: SGPClient) -> None:
        with client.application_variants.with_streaming_response.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            configuration={},
            name="name",
            version="OFFLINE",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            application_variant = response.parse()
            assert_matches_type(ApplicationVariantCreateResponse, application_variant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: SGPClient) -> None:
        application_variant = client.application_variants.retrieve(
            "application_variant_id",
        )
        assert_matches_type(ApplicationVariantRetrieveResponse, application_variant, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: SGPClient) -> None:
        response = client.application_variants.with_raw_response.retrieve(
            "application_variant_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        application_variant = response.parse()
        assert_matches_type(ApplicationVariantRetrieveResponse, application_variant, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: SGPClient) -> None:
        with client.application_variants.with_streaming_response.retrieve(
            "application_variant_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            application_variant = response.parse()
            assert_matches_type(ApplicationVariantRetrieveResponse, application_variant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: SGPClient) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `application_variant_id` but received ''"
        ):
            client.application_variants.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_list(self, client: SGPClient) -> None:
        application_variant = client.application_variants.list()
        assert_matches_type(ApplicationVariantListResponse, application_variant, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: SGPClient) -> None:
        application_variant = client.application_variants.list(
            account_id="account_id",
            application_spec_id=0,
            limit=1,
            page=1,
        )
        assert_matches_type(ApplicationVariantListResponse, application_variant, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: SGPClient) -> None:
        response = client.application_variants.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        application_variant = response.parse()
        assert_matches_type(ApplicationVariantListResponse, application_variant, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: SGPClient) -> None:
        with client.application_variants.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            application_variant = response.parse()
            assert_matches_type(ApplicationVariantListResponse, application_variant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: SGPClient) -> None:
        application_variant = client.application_variants.delete(
            "application_variant_id",
        )
        assert_matches_type(DeleteResponse, application_variant, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: SGPClient) -> None:
        response = client.application_variants.with_raw_response.delete(
            "application_variant_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        application_variant = response.parse()
        assert_matches_type(DeleteResponse, application_variant, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: SGPClient) -> None:
        with client.application_variants.with_streaming_response.delete(
            "application_variant_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            application_variant = response.parse()
            assert_matches_type(DeleteResponse, application_variant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: SGPClient) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `application_variant_id` but received ''"
        ):
            client.application_variants.with_raw_response.delete(
                "",
            )


class TestAsyncApplicationVariants:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create_overload_1(self, async_client: AsyncSGPClient) -> None:
        application_variant = await async_client.application_variants.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            configuration={
                "nodes": [
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
                "edges": [
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
            },
            name="name",
            version="V0",
        )
        assert_matches_type(ApplicationVariantCreateResponse, application_variant, path=["response"])

    @parametrize
    async def test_method_create_with_all_params_overload_1(self, async_client: AsyncSGPClient) -> None:
        application_variant = await async_client.application_variants.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            configuration={
                "nodes": [
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
                "edges": [
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
            },
            name="name",
            version="V0",
            description="description",
        )
        assert_matches_type(ApplicationVariantCreateResponse, application_variant, path=["response"])

    @parametrize
    async def test_raw_response_create_overload_1(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.application_variants.with_raw_response.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            configuration={
                "nodes": [
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
                "edges": [
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
            },
            name="name",
            version="V0",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        application_variant = await response.parse()
        assert_matches_type(ApplicationVariantCreateResponse, application_variant, path=["response"])

    @parametrize
    async def test_streaming_response_create_overload_1(self, async_client: AsyncSGPClient) -> None:
        async with async_client.application_variants.with_streaming_response.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            configuration={
                "nodes": [
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
                "edges": [
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
            },
            name="name",
            version="V0",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            application_variant = await response.parse()
            assert_matches_type(ApplicationVariantCreateResponse, application_variant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_create_overload_2(self, async_client: AsyncSGPClient) -> None:
        application_variant = await async_client.application_variants.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            configuration={},
            name="name",
            version="OFFLINE",
        )
        assert_matches_type(ApplicationVariantCreateResponse, application_variant, path=["response"])

    @parametrize
    async def test_method_create_with_all_params_overload_2(self, async_client: AsyncSGPClient) -> None:
        application_variant = await async_client.application_variants.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            configuration={
                "output_schema_type": "completion_only",
                "metadata": {},
            },
            name="name",
            version="OFFLINE",
            description="description",
        )
        assert_matches_type(ApplicationVariantCreateResponse, application_variant, path=["response"])

    @parametrize
    async def test_raw_response_create_overload_2(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.application_variants.with_raw_response.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            configuration={},
            name="name",
            version="OFFLINE",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        application_variant = await response.parse()
        assert_matches_type(ApplicationVariantCreateResponse, application_variant, path=["response"])

    @parametrize
    async def test_streaming_response_create_overload_2(self, async_client: AsyncSGPClient) -> None:
        async with async_client.application_variants.with_streaming_response.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            configuration={},
            name="name",
            version="OFFLINE",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            application_variant = await response.parse()
            assert_matches_type(ApplicationVariantCreateResponse, application_variant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncSGPClient) -> None:
        application_variant = await async_client.application_variants.retrieve(
            "application_variant_id",
        )
        assert_matches_type(ApplicationVariantRetrieveResponse, application_variant, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.application_variants.with_raw_response.retrieve(
            "application_variant_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        application_variant = await response.parse()
        assert_matches_type(ApplicationVariantRetrieveResponse, application_variant, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncSGPClient) -> None:
        async with async_client.application_variants.with_streaming_response.retrieve(
            "application_variant_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            application_variant = await response.parse()
            assert_matches_type(ApplicationVariantRetrieveResponse, application_variant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncSGPClient) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `application_variant_id` but received ''"
        ):
            await async_client.application_variants.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncSGPClient) -> None:
        application_variant = await async_client.application_variants.list()
        assert_matches_type(ApplicationVariantListResponse, application_variant, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncSGPClient) -> None:
        application_variant = await async_client.application_variants.list(
            account_id="account_id",
            application_spec_id=0,
            limit=1,
            page=1,
        )
        assert_matches_type(ApplicationVariantListResponse, application_variant, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.application_variants.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        application_variant = await response.parse()
        assert_matches_type(ApplicationVariantListResponse, application_variant, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncSGPClient) -> None:
        async with async_client.application_variants.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            application_variant = await response.parse()
            assert_matches_type(ApplicationVariantListResponse, application_variant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncSGPClient) -> None:
        application_variant = await async_client.application_variants.delete(
            "application_variant_id",
        )
        assert_matches_type(DeleteResponse, application_variant, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.application_variants.with_raw_response.delete(
            "application_variant_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        application_variant = await response.parse()
        assert_matches_type(DeleteResponse, application_variant, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncSGPClient) -> None:
        async with async_client.application_variants.with_streaming_response.delete(
            "application_variant_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            application_variant = await response.parse()
            assert_matches_type(DeleteResponse, application_variant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncSGPClient) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `application_variant_id` but received ''"
        ):
            await async_client.application_variants.with_raw_response.delete(
                "",
            )
