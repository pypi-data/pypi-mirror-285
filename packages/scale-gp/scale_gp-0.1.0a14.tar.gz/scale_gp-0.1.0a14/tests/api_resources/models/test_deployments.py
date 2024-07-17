# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from scale_gp import SGPClient, AsyncSGPClient
from tests.utils import assert_matches_type
from scale_gp.types.models import (
    EmbeddingResponse,
    RerankingResponse,
    CompletionResponse,
    ModelDeploymentResponse,
)
from scale_gp.types.shared import DeleteResponse, PaginationResponseModelDeployment

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDeployments:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: SGPClient) -> None:
        deployment = client.models.deployments.create(
            model_instance_id="model_instance_id",
            name="name",
        )
        assert_matches_type(ModelDeploymentResponse, deployment, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: SGPClient) -> None:
        deployment = client.models.deployments.create(
            model_instance_id="model_instance_id",
            name="name",
            account_id="account_id",
            deployment_metadata={},
            model_creation_parameters={},
            vendor_configuration={
                "min_workers": 0,
                "max_workers": 0,
                "per_worker": 0,
                "vendor": "LAUNCH",
            },
        )
        assert_matches_type(ModelDeploymentResponse, deployment, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: SGPClient) -> None:
        response = client.models.deployments.with_raw_response.create(
            model_instance_id="model_instance_id",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(ModelDeploymentResponse, deployment, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: SGPClient) -> None:
        with client.models.deployments.with_streaming_response.create(
            model_instance_id="model_instance_id",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(ModelDeploymentResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: SGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_instance_id` but received ''"):
            client.models.deployments.with_raw_response.create(
                model_instance_id="",
                name="name",
            )

    @parametrize
    def test_method_retrieve(self, client: SGPClient) -> None:
        deployment = client.models.deployments.retrieve(
            deployment_id="deployment_id",
            model_instance_id="model_instance_id",
        )
        assert_matches_type(ModelDeploymentResponse, deployment, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: SGPClient) -> None:
        response = client.models.deployments.with_raw_response.retrieve(
            deployment_id="deployment_id",
            model_instance_id="model_instance_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(ModelDeploymentResponse, deployment, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: SGPClient) -> None:
        with client.models.deployments.with_streaming_response.retrieve(
            deployment_id="deployment_id",
            model_instance_id="model_instance_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(ModelDeploymentResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: SGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_instance_id` but received ''"):
            client.models.deployments.with_raw_response.retrieve(
                deployment_id="deployment_id",
                model_instance_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_id` but received ''"):
            client.models.deployments.with_raw_response.retrieve(
                deployment_id="",
                model_instance_id="model_instance_id",
            )

    @parametrize
    def test_method_update(self, client: SGPClient) -> None:
        deployment = client.models.deployments.update(
            deployment_id="deployment_id",
            model_instance_id="model_instance_id",
        )
        assert_matches_type(ModelDeploymentResponse, deployment, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: SGPClient) -> None:
        deployment = client.models.deployments.update(
            deployment_id="deployment_id",
            model_instance_id="model_instance_id",
            deployment_metadata={},
            model_creation_parameters={},
            name="name",
            vendor_configuration={
                "min_workers": 0,
                "max_workers": 0,
                "per_worker": 0,
                "vendor": "LAUNCH",
            },
        )
        assert_matches_type(ModelDeploymentResponse, deployment, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: SGPClient) -> None:
        response = client.models.deployments.with_raw_response.update(
            deployment_id="deployment_id",
            model_instance_id="model_instance_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(ModelDeploymentResponse, deployment, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: SGPClient) -> None:
        with client.models.deployments.with_streaming_response.update(
            deployment_id="deployment_id",
            model_instance_id="model_instance_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(ModelDeploymentResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: SGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_instance_id` but received ''"):
            client.models.deployments.with_raw_response.update(
                deployment_id="deployment_id",
                model_instance_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_id` but received ''"):
            client.models.deployments.with_raw_response.update(
                deployment_id="",
                model_instance_id="model_instance_id",
            )

    @parametrize
    def test_method_list(self, client: SGPClient) -> None:
        deployment = client.models.deployments.list(
            model_instance_id="model_instance_id",
        )
        assert_matches_type(PaginationResponseModelDeployment, deployment, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: SGPClient) -> None:
        deployment = client.models.deployments.list(
            model_instance_id="model_instance_id",
            account_id="account_id",
            limit=1,
            page=1,
            sort_by=["model_creation_parameters:asc", "model_creation_parameters:desc", "model_endpoint_id:asc"],
        )
        assert_matches_type(PaginationResponseModelDeployment, deployment, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: SGPClient) -> None:
        response = client.models.deployments.with_raw_response.list(
            model_instance_id="model_instance_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(PaginationResponseModelDeployment, deployment, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: SGPClient) -> None:
        with client.models.deployments.with_streaming_response.list(
            model_instance_id="model_instance_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(PaginationResponseModelDeployment, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: SGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_instance_id` but received ''"):
            client.models.deployments.with_raw_response.list(
                model_instance_id="",
            )

    @parametrize
    def test_method_delete(self, client: SGPClient) -> None:
        deployment = client.models.deployments.delete(
            deployment_id="deployment_id",
            model_instance_id="model_instance_id",
        )
        assert_matches_type(DeleteResponse, deployment, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: SGPClient) -> None:
        response = client.models.deployments.with_raw_response.delete(
            deployment_id="deployment_id",
            model_instance_id="model_instance_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(DeleteResponse, deployment, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: SGPClient) -> None:
        with client.models.deployments.with_streaming_response.delete(
            deployment_id="deployment_id",
            model_instance_id="model_instance_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(DeleteResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: SGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_instance_id` but received ''"):
            client.models.deployments.with_raw_response.delete(
                deployment_id="deployment_id",
                model_instance_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_id` but received ''"):
            client.models.deployments.with_raw_response.delete(
                deployment_id="",
                model_instance_id="model_instance_id",
            )

    @parametrize
    def test_method_chat_completions(self, client: SGPClient) -> None:
        deployment = client.models.deployments.chat_completions(
            model_deployment_id="model_deployment_id",
            chat_history=[{"content": "content"}, {"content": "content"}, {"content": "content"}],
            prompt="prompt",
        )
        assert_matches_type(CompletionResponse, deployment, path=["response"])

    @parametrize
    def test_method_chat_completions_with_all_params(self, client: SGPClient) -> None:
        deployment = client.models.deployments.chat_completions(
            model_deployment_id="model_deployment_id",
            chat_history=[
                {
                    "role": "user",
                    "content": "content",
                },
                {
                    "role": "user",
                    "content": "content",
                },
                {
                    "role": "user",
                    "content": "content",
                },
            ],
            prompt="prompt",
            frequency_penalty=0,
            max_tokens=0,
            model_request_parameters={"bindings": {"foo": "string"}},
            presence_penalty=0,
            stop_sequences=["string", "string", "string"],
            temperature=0,
            top_k=0,
            top_p=0,
        )
        assert_matches_type(CompletionResponse, deployment, path=["response"])

    @parametrize
    def test_raw_response_chat_completions(self, client: SGPClient) -> None:
        response = client.models.deployments.with_raw_response.chat_completions(
            model_deployment_id="model_deployment_id",
            chat_history=[{"content": "content"}, {"content": "content"}, {"content": "content"}],
            prompt="prompt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(CompletionResponse, deployment, path=["response"])

    @parametrize
    def test_streaming_response_chat_completions(self, client: SGPClient) -> None:
        with client.models.deployments.with_streaming_response.chat_completions(
            model_deployment_id="model_deployment_id",
            chat_history=[{"content": "content"}, {"content": "content"}, {"content": "content"}],
            prompt="prompt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(CompletionResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_chat_completions(self, client: SGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_deployment_id` but received ''"):
            client.models.deployments.with_raw_response.chat_completions(
                model_deployment_id="",
                chat_history=[{"content": "content"}, {"content": "content"}, {"content": "content"}],
                prompt="prompt",
            )

    @parametrize
    def test_method_completions(self, client: SGPClient) -> None:
        deployment = client.models.deployments.completions(
            model_deployment_id="model_deployment_id",
            prompt="prompt",
        )
        assert_matches_type(CompletionResponse, deployment, path=["response"])

    @parametrize
    def test_method_completions_with_all_params(self, client: SGPClient) -> None:
        deployment = client.models.deployments.completions(
            model_deployment_id="model_deployment_id",
            prompt="prompt",
            frequency_penalty=0,
            max_tokens=0,
            model_request_parameters={"bindings": {"foo": "string"}},
            presence_penalty=0,
            stop_sequences=["string", "string", "string"],
            temperature=0,
            top_k=0,
            top_p=0,
        )
        assert_matches_type(CompletionResponse, deployment, path=["response"])

    @parametrize
    def test_raw_response_completions(self, client: SGPClient) -> None:
        response = client.models.deployments.with_raw_response.completions(
            model_deployment_id="model_deployment_id",
            prompt="prompt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(CompletionResponse, deployment, path=["response"])

    @parametrize
    def test_streaming_response_completions(self, client: SGPClient) -> None:
        with client.models.deployments.with_streaming_response.completions(
            model_deployment_id="model_deployment_id",
            prompt="prompt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(CompletionResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_completions(self, client: SGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_deployment_id` but received ''"):
            client.models.deployments.with_raw_response.completions(
                model_deployment_id="",
                prompt="prompt",
            )

    @parametrize
    def test_method_embeddings(self, client: SGPClient) -> None:
        deployment = client.models.deployments.embeddings(
            model_deployment_id="model_deployment_id",
            texts=["string", "string", "string"],
        )
        assert_matches_type(EmbeddingResponse, deployment, path=["response"])

    @parametrize
    def test_method_embeddings_with_all_params(self, client: SGPClient) -> None:
        deployment = client.models.deployments.embeddings(
            model_deployment_id="model_deployment_id",
            texts=["string", "string", "string"],
            model_request_parameters={"bindings": {"foo": "string"}},
        )
        assert_matches_type(EmbeddingResponse, deployment, path=["response"])

    @parametrize
    def test_raw_response_embeddings(self, client: SGPClient) -> None:
        response = client.models.deployments.with_raw_response.embeddings(
            model_deployment_id="model_deployment_id",
            texts=["string", "string", "string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(EmbeddingResponse, deployment, path=["response"])

    @parametrize
    def test_streaming_response_embeddings(self, client: SGPClient) -> None:
        with client.models.deployments.with_streaming_response.embeddings(
            model_deployment_id="model_deployment_id",
            texts=["string", "string", "string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(EmbeddingResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_embeddings(self, client: SGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_deployment_id` but received ''"):
            client.models.deployments.with_raw_response.embeddings(
                model_deployment_id="",
                texts=["string", "string", "string"],
            )

    @parametrize
    def test_method_execute(self, client: SGPClient) -> None:
        deployment = client.models.deployments.execute(
            model_deployment_id="model_deployment_id",
            model_instance_id="model_instance_id",
        )
        assert_matches_type(object, deployment, path=["response"])

    @parametrize
    def test_raw_response_execute(self, client: SGPClient) -> None:
        response = client.models.deployments.with_raw_response.execute(
            model_deployment_id="model_deployment_id",
            model_instance_id="model_instance_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(object, deployment, path=["response"])

    @parametrize
    def test_streaming_response_execute(self, client: SGPClient) -> None:
        with client.models.deployments.with_streaming_response.execute(
            model_deployment_id="model_deployment_id",
            model_instance_id="model_instance_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(object, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_execute(self, client: SGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_instance_id` but received ''"):
            client.models.deployments.with_raw_response.execute(
                model_deployment_id="model_deployment_id",
                model_instance_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_deployment_id` but received ''"):
            client.models.deployments.with_raw_response.execute(
                model_deployment_id="",
                model_instance_id="model_instance_id",
            )

    @parametrize
    def test_method_rerankings(self, client: SGPClient) -> None:
        deployment = client.models.deployments.rerankings(
            model_deployment_id="model_deployment_id",
            chunks=["string", "string", "string"],
            query="query",
        )
        assert_matches_type(RerankingResponse, deployment, path=["response"])

    @parametrize
    def test_method_rerankings_with_all_params(self, client: SGPClient) -> None:
        deployment = client.models.deployments.rerankings(
            model_deployment_id="model_deployment_id",
            chunks=["string", "string", "string"],
            query="query",
            model_request_parameters={"bindings": {"foo": "string"}},
        )
        assert_matches_type(RerankingResponse, deployment, path=["response"])

    @parametrize
    def test_raw_response_rerankings(self, client: SGPClient) -> None:
        response = client.models.deployments.with_raw_response.rerankings(
            model_deployment_id="model_deployment_id",
            chunks=["string", "string", "string"],
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(RerankingResponse, deployment, path=["response"])

    @parametrize
    def test_streaming_response_rerankings(self, client: SGPClient) -> None:
        with client.models.deployments.with_streaming_response.rerankings(
            model_deployment_id="model_deployment_id",
            chunks=["string", "string", "string"],
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(RerankingResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_rerankings(self, client: SGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_deployment_id` but received ''"):
            client.models.deployments.with_raw_response.rerankings(
                model_deployment_id="",
                chunks=["string", "string", "string"],
                query="query",
            )


class TestAsyncDeployments:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncSGPClient) -> None:
        deployment = await async_client.models.deployments.create(
            model_instance_id="model_instance_id",
            name="name",
        )
        assert_matches_type(ModelDeploymentResponse, deployment, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncSGPClient) -> None:
        deployment = await async_client.models.deployments.create(
            model_instance_id="model_instance_id",
            name="name",
            account_id="account_id",
            deployment_metadata={},
            model_creation_parameters={},
            vendor_configuration={
                "min_workers": 0,
                "max_workers": 0,
                "per_worker": 0,
                "vendor": "LAUNCH",
            },
        )
        assert_matches_type(ModelDeploymentResponse, deployment, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.models.deployments.with_raw_response.create(
            model_instance_id="model_instance_id",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(ModelDeploymentResponse, deployment, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncSGPClient) -> None:
        async with async_client.models.deployments.with_streaming_response.create(
            model_instance_id="model_instance_id",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(ModelDeploymentResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncSGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_instance_id` but received ''"):
            await async_client.models.deployments.with_raw_response.create(
                model_instance_id="",
                name="name",
            )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncSGPClient) -> None:
        deployment = await async_client.models.deployments.retrieve(
            deployment_id="deployment_id",
            model_instance_id="model_instance_id",
        )
        assert_matches_type(ModelDeploymentResponse, deployment, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.models.deployments.with_raw_response.retrieve(
            deployment_id="deployment_id",
            model_instance_id="model_instance_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(ModelDeploymentResponse, deployment, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncSGPClient) -> None:
        async with async_client.models.deployments.with_streaming_response.retrieve(
            deployment_id="deployment_id",
            model_instance_id="model_instance_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(ModelDeploymentResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncSGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_instance_id` but received ''"):
            await async_client.models.deployments.with_raw_response.retrieve(
                deployment_id="deployment_id",
                model_instance_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_id` but received ''"):
            await async_client.models.deployments.with_raw_response.retrieve(
                deployment_id="",
                model_instance_id="model_instance_id",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncSGPClient) -> None:
        deployment = await async_client.models.deployments.update(
            deployment_id="deployment_id",
            model_instance_id="model_instance_id",
        )
        assert_matches_type(ModelDeploymentResponse, deployment, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncSGPClient) -> None:
        deployment = await async_client.models.deployments.update(
            deployment_id="deployment_id",
            model_instance_id="model_instance_id",
            deployment_metadata={},
            model_creation_parameters={},
            name="name",
            vendor_configuration={
                "min_workers": 0,
                "max_workers": 0,
                "per_worker": 0,
                "vendor": "LAUNCH",
            },
        )
        assert_matches_type(ModelDeploymentResponse, deployment, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.models.deployments.with_raw_response.update(
            deployment_id="deployment_id",
            model_instance_id="model_instance_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(ModelDeploymentResponse, deployment, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncSGPClient) -> None:
        async with async_client.models.deployments.with_streaming_response.update(
            deployment_id="deployment_id",
            model_instance_id="model_instance_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(ModelDeploymentResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncSGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_instance_id` but received ''"):
            await async_client.models.deployments.with_raw_response.update(
                deployment_id="deployment_id",
                model_instance_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_id` but received ''"):
            await async_client.models.deployments.with_raw_response.update(
                deployment_id="",
                model_instance_id="model_instance_id",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncSGPClient) -> None:
        deployment = await async_client.models.deployments.list(
            model_instance_id="model_instance_id",
        )
        assert_matches_type(PaginationResponseModelDeployment, deployment, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncSGPClient) -> None:
        deployment = await async_client.models.deployments.list(
            model_instance_id="model_instance_id",
            account_id="account_id",
            limit=1,
            page=1,
            sort_by=["model_creation_parameters:asc", "model_creation_parameters:desc", "model_endpoint_id:asc"],
        )
        assert_matches_type(PaginationResponseModelDeployment, deployment, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.models.deployments.with_raw_response.list(
            model_instance_id="model_instance_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(PaginationResponseModelDeployment, deployment, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncSGPClient) -> None:
        async with async_client.models.deployments.with_streaming_response.list(
            model_instance_id="model_instance_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(PaginationResponseModelDeployment, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncSGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_instance_id` but received ''"):
            await async_client.models.deployments.with_raw_response.list(
                model_instance_id="",
            )

    @parametrize
    async def test_method_delete(self, async_client: AsyncSGPClient) -> None:
        deployment = await async_client.models.deployments.delete(
            deployment_id="deployment_id",
            model_instance_id="model_instance_id",
        )
        assert_matches_type(DeleteResponse, deployment, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.models.deployments.with_raw_response.delete(
            deployment_id="deployment_id",
            model_instance_id="model_instance_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(DeleteResponse, deployment, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncSGPClient) -> None:
        async with async_client.models.deployments.with_streaming_response.delete(
            deployment_id="deployment_id",
            model_instance_id="model_instance_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(DeleteResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncSGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_instance_id` but received ''"):
            await async_client.models.deployments.with_raw_response.delete(
                deployment_id="deployment_id",
                model_instance_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_id` but received ''"):
            await async_client.models.deployments.with_raw_response.delete(
                deployment_id="",
                model_instance_id="model_instance_id",
            )

    @parametrize
    async def test_method_chat_completions(self, async_client: AsyncSGPClient) -> None:
        deployment = await async_client.models.deployments.chat_completions(
            model_deployment_id="model_deployment_id",
            chat_history=[{"content": "content"}, {"content": "content"}, {"content": "content"}],
            prompt="prompt",
        )
        assert_matches_type(CompletionResponse, deployment, path=["response"])

    @parametrize
    async def test_method_chat_completions_with_all_params(self, async_client: AsyncSGPClient) -> None:
        deployment = await async_client.models.deployments.chat_completions(
            model_deployment_id="model_deployment_id",
            chat_history=[
                {
                    "role": "user",
                    "content": "content",
                },
                {
                    "role": "user",
                    "content": "content",
                },
                {
                    "role": "user",
                    "content": "content",
                },
            ],
            prompt="prompt",
            frequency_penalty=0,
            max_tokens=0,
            model_request_parameters={"bindings": {"foo": "string"}},
            presence_penalty=0,
            stop_sequences=["string", "string", "string"],
            temperature=0,
            top_k=0,
            top_p=0,
        )
        assert_matches_type(CompletionResponse, deployment, path=["response"])

    @parametrize
    async def test_raw_response_chat_completions(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.models.deployments.with_raw_response.chat_completions(
            model_deployment_id="model_deployment_id",
            chat_history=[{"content": "content"}, {"content": "content"}, {"content": "content"}],
            prompt="prompt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(CompletionResponse, deployment, path=["response"])

    @parametrize
    async def test_streaming_response_chat_completions(self, async_client: AsyncSGPClient) -> None:
        async with async_client.models.deployments.with_streaming_response.chat_completions(
            model_deployment_id="model_deployment_id",
            chat_history=[{"content": "content"}, {"content": "content"}, {"content": "content"}],
            prompt="prompt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(CompletionResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_chat_completions(self, async_client: AsyncSGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_deployment_id` but received ''"):
            await async_client.models.deployments.with_raw_response.chat_completions(
                model_deployment_id="",
                chat_history=[{"content": "content"}, {"content": "content"}, {"content": "content"}],
                prompt="prompt",
            )

    @parametrize
    async def test_method_completions(self, async_client: AsyncSGPClient) -> None:
        deployment = await async_client.models.deployments.completions(
            model_deployment_id="model_deployment_id",
            prompt="prompt",
        )
        assert_matches_type(CompletionResponse, deployment, path=["response"])

    @parametrize
    async def test_method_completions_with_all_params(self, async_client: AsyncSGPClient) -> None:
        deployment = await async_client.models.deployments.completions(
            model_deployment_id="model_deployment_id",
            prompt="prompt",
            frequency_penalty=0,
            max_tokens=0,
            model_request_parameters={"bindings": {"foo": "string"}},
            presence_penalty=0,
            stop_sequences=["string", "string", "string"],
            temperature=0,
            top_k=0,
            top_p=0,
        )
        assert_matches_type(CompletionResponse, deployment, path=["response"])

    @parametrize
    async def test_raw_response_completions(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.models.deployments.with_raw_response.completions(
            model_deployment_id="model_deployment_id",
            prompt="prompt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(CompletionResponse, deployment, path=["response"])

    @parametrize
    async def test_streaming_response_completions(self, async_client: AsyncSGPClient) -> None:
        async with async_client.models.deployments.with_streaming_response.completions(
            model_deployment_id="model_deployment_id",
            prompt="prompt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(CompletionResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_completions(self, async_client: AsyncSGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_deployment_id` but received ''"):
            await async_client.models.deployments.with_raw_response.completions(
                model_deployment_id="",
                prompt="prompt",
            )

    @parametrize
    async def test_method_embeddings(self, async_client: AsyncSGPClient) -> None:
        deployment = await async_client.models.deployments.embeddings(
            model_deployment_id="model_deployment_id",
            texts=["string", "string", "string"],
        )
        assert_matches_type(EmbeddingResponse, deployment, path=["response"])

    @parametrize
    async def test_method_embeddings_with_all_params(self, async_client: AsyncSGPClient) -> None:
        deployment = await async_client.models.deployments.embeddings(
            model_deployment_id="model_deployment_id",
            texts=["string", "string", "string"],
            model_request_parameters={"bindings": {"foo": "string"}},
        )
        assert_matches_type(EmbeddingResponse, deployment, path=["response"])

    @parametrize
    async def test_raw_response_embeddings(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.models.deployments.with_raw_response.embeddings(
            model_deployment_id="model_deployment_id",
            texts=["string", "string", "string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(EmbeddingResponse, deployment, path=["response"])

    @parametrize
    async def test_streaming_response_embeddings(self, async_client: AsyncSGPClient) -> None:
        async with async_client.models.deployments.with_streaming_response.embeddings(
            model_deployment_id="model_deployment_id",
            texts=["string", "string", "string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(EmbeddingResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_embeddings(self, async_client: AsyncSGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_deployment_id` but received ''"):
            await async_client.models.deployments.with_raw_response.embeddings(
                model_deployment_id="",
                texts=["string", "string", "string"],
            )

    @parametrize
    async def test_method_execute(self, async_client: AsyncSGPClient) -> None:
        deployment = await async_client.models.deployments.execute(
            model_deployment_id="model_deployment_id",
            model_instance_id="model_instance_id",
        )
        assert_matches_type(object, deployment, path=["response"])

    @parametrize
    async def test_raw_response_execute(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.models.deployments.with_raw_response.execute(
            model_deployment_id="model_deployment_id",
            model_instance_id="model_instance_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(object, deployment, path=["response"])

    @parametrize
    async def test_streaming_response_execute(self, async_client: AsyncSGPClient) -> None:
        async with async_client.models.deployments.with_streaming_response.execute(
            model_deployment_id="model_deployment_id",
            model_instance_id="model_instance_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(object, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_execute(self, async_client: AsyncSGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_instance_id` but received ''"):
            await async_client.models.deployments.with_raw_response.execute(
                model_deployment_id="model_deployment_id",
                model_instance_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_deployment_id` but received ''"):
            await async_client.models.deployments.with_raw_response.execute(
                model_deployment_id="",
                model_instance_id="model_instance_id",
            )

    @parametrize
    async def test_method_rerankings(self, async_client: AsyncSGPClient) -> None:
        deployment = await async_client.models.deployments.rerankings(
            model_deployment_id="model_deployment_id",
            chunks=["string", "string", "string"],
            query="query",
        )
        assert_matches_type(RerankingResponse, deployment, path=["response"])

    @parametrize
    async def test_method_rerankings_with_all_params(self, async_client: AsyncSGPClient) -> None:
        deployment = await async_client.models.deployments.rerankings(
            model_deployment_id="model_deployment_id",
            chunks=["string", "string", "string"],
            query="query",
            model_request_parameters={"bindings": {"foo": "string"}},
        )
        assert_matches_type(RerankingResponse, deployment, path=["response"])

    @parametrize
    async def test_raw_response_rerankings(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.models.deployments.with_raw_response.rerankings(
            model_deployment_id="model_deployment_id",
            chunks=["string", "string", "string"],
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(RerankingResponse, deployment, path=["response"])

    @parametrize
    async def test_streaming_response_rerankings(self, async_client: AsyncSGPClient) -> None:
        async with async_client.models.deployments.with_streaming_response.rerankings(
            model_deployment_id="model_deployment_id",
            chunks=["string", "string", "string"],
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(RerankingResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_rerankings(self, async_client: AsyncSGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_deployment_id` but received ''"):
            await async_client.models.deployments.with_raw_response.rerankings(
                model_deployment_id="",
                chunks=["string", "string", "string"],
                query="query",
            )
