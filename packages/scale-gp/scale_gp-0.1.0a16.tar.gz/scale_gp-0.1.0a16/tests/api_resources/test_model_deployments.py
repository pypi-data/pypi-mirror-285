# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from scale_gp import SGPClient, AsyncSGPClient
from tests.utils import assert_matches_type
from scale_gp.types.shared import PaginationResponseModelDeployment

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestModelDeployments:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: SGPClient) -> None:
        model_deployment = client.model_deployments.list()
        assert_matches_type(PaginationResponseModelDeployment, model_deployment, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: SGPClient) -> None:
        model_deployment = client.model_deployments.list(
            account_id="account_id",
            limit=1,
            page=1,
            sort_by=["model_creation_parameters:asc", "model_creation_parameters:desc", "model_endpoint_id:asc"],
        )
        assert_matches_type(PaginationResponseModelDeployment, model_deployment, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: SGPClient) -> None:
        response = client.model_deployments.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model_deployment = response.parse()
        assert_matches_type(PaginationResponseModelDeployment, model_deployment, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: SGPClient) -> None:
        with client.model_deployments.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model_deployment = response.parse()
            assert_matches_type(PaginationResponseModelDeployment, model_deployment, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncModelDeployments:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_list(self, async_client: AsyncSGPClient) -> None:
        model_deployment = await async_client.model_deployments.list()
        assert_matches_type(PaginationResponseModelDeployment, model_deployment, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncSGPClient) -> None:
        model_deployment = await async_client.model_deployments.list(
            account_id="account_id",
            limit=1,
            page=1,
            sort_by=["model_creation_parameters:asc", "model_creation_parameters:desc", "model_endpoint_id:asc"],
        )
        assert_matches_type(PaginationResponseModelDeployment, model_deployment, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.model_deployments.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model_deployment = await response.parse()
        assert_matches_type(PaginationResponseModelDeployment, model_deployment, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncSGPClient) -> None:
        async with async_client.model_deployments.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model_deployment = await response.parse()
            assert_matches_type(PaginationResponseModelDeployment, model_deployment, path=["response"])

        assert cast(Any, response.is_closed) is True
