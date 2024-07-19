# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from scale_gp import SGPClient, AsyncSGPClient
from tests.utils import assert_matches_type
from scale_gp.types import (
    EvaluationResponse,
    EvaluationListResponse,
    EvaluationResponseWithViews,
)
from scale_gp.types.shared import TaskResponse, DeleteResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEvaluations:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create_overload_1(self, client: SGPClient) -> None:
        evaluation = client.evaluations.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            application_variant_id="application_variant_id",
            description="description",
            evaluation_dataset_id="evaluation_dataset_id",
            name="name",
        )
        assert_matches_type(EvaluationResponse, evaluation, path=["response"])

    @parametrize
    def test_method_create_with_all_params_overload_1(self, client: SGPClient) -> None:
        evaluation = client.evaluations.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            application_variant_id="application_variant_id",
            description="description",
            evaluation_dataset_id="evaluation_dataset_id",
            name="name",
            evaluation_config={},
            evaluation_config_id="evaluation_config_id",
            evaluation_dataset_version=0,
            tags={},
            type="builder",
        )
        assert_matches_type(EvaluationResponse, evaluation, path=["response"])

    @parametrize
    def test_raw_response_create_overload_1(self, client: SGPClient) -> None:
        response = client.evaluations.with_raw_response.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            application_variant_id="application_variant_id",
            description="description",
            evaluation_dataset_id="evaluation_dataset_id",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = response.parse()
        assert_matches_type(EvaluationResponse, evaluation, path=["response"])

    @parametrize
    def test_streaming_response_create_overload_1(self, client: SGPClient) -> None:
        with client.evaluations.with_streaming_response.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            application_variant_id="application_variant_id",
            description="description",
            evaluation_dataset_id="evaluation_dataset_id",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = response.parse()
            assert_matches_type(EvaluationResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_create_overload_2(self, client: SGPClient) -> None:
        evaluation = client.evaluations.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            description="description",
            name="name",
        )
        assert_matches_type(EvaluationResponse, evaluation, path=["response"])

    @parametrize
    def test_method_create_with_all_params_overload_2(self, client: SGPClient) -> None:
        evaluation = client.evaluations.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            description="description",
            name="name",
            application_variant_id="application_variant_id",
            evaluation_config={},
            evaluation_config_id="evaluation_config_id",
            tags={},
            type="default",
        )
        assert_matches_type(EvaluationResponse, evaluation, path=["response"])

    @parametrize
    def test_raw_response_create_overload_2(self, client: SGPClient) -> None:
        response = client.evaluations.with_raw_response.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            description="description",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = response.parse()
        assert_matches_type(EvaluationResponse, evaluation, path=["response"])

    @parametrize
    def test_streaming_response_create_overload_2(self, client: SGPClient) -> None:
        with client.evaluations.with_streaming_response.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            description="description",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = response.parse()
            assert_matches_type(EvaluationResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: SGPClient) -> None:
        evaluation = client.evaluations.retrieve(
            evaluation_id="evaluation_id",
        )
        assert_matches_type(EvaluationResponseWithViews, evaluation, path=["response"])

    @parametrize
    def test_method_retrieve_with_all_params(self, client: SGPClient) -> None:
        evaluation = client.evaluations.retrieve(
            evaluation_id="evaluation_id",
            view=["ApplicationSpec", "AsyncJobs", "EvaluationConfig"],
        )
        assert_matches_type(EvaluationResponseWithViews, evaluation, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: SGPClient) -> None:
        response = client.evaluations.with_raw_response.retrieve(
            evaluation_id="evaluation_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = response.parse()
        assert_matches_type(EvaluationResponseWithViews, evaluation, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: SGPClient) -> None:
        with client.evaluations.with_streaming_response.retrieve(
            evaluation_id="evaluation_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = response.parse()
            assert_matches_type(EvaluationResponseWithViews, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: SGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluation_id` but received ''"):
            client.evaluations.with_raw_response.retrieve(
                evaluation_id="",
            )

    @parametrize
    def test_method_update_overload_1(self, client: SGPClient) -> None:
        evaluation = client.evaluations.update(
            evaluation_id="evaluation_id",
        )
        assert_matches_type(EvaluationResponse, evaluation, path=["response"])

    @parametrize
    def test_method_update_with_all_params_overload_1(self, client: SGPClient) -> None:
        evaluation = client.evaluations.update(
            evaluation_id="evaluation_id",
            application_spec_id="application_spec_id",
            application_variant_id="application_variant_id",
            description="description",
            evaluation_config={},
            evaluation_config_id="evaluation_config_id",
            evaluation_type="llm_benchmark",
            name="name",
            restore=True,
            tags={},
        )
        assert_matches_type(EvaluationResponse, evaluation, path=["response"])

    @parametrize
    def test_raw_response_update_overload_1(self, client: SGPClient) -> None:
        response = client.evaluations.with_raw_response.update(
            evaluation_id="evaluation_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = response.parse()
        assert_matches_type(EvaluationResponse, evaluation, path=["response"])

    @parametrize
    def test_streaming_response_update_overload_1(self, client: SGPClient) -> None:
        with client.evaluations.with_streaming_response.update(
            evaluation_id="evaluation_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = response.parse()
            assert_matches_type(EvaluationResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update_overload_1(self, client: SGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluation_id` but received ''"):
            client.evaluations.with_raw_response.update(
                evaluation_id="",
            )

    @parametrize
    def test_method_update_overload_2(self, client: SGPClient) -> None:
        evaluation = client.evaluations.update(
            evaluation_id="evaluation_id",
            restore=True,
        )
        assert_matches_type(EvaluationResponse, evaluation, path=["response"])

    @parametrize
    def test_raw_response_update_overload_2(self, client: SGPClient) -> None:
        response = client.evaluations.with_raw_response.update(
            evaluation_id="evaluation_id",
            restore=True,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = response.parse()
        assert_matches_type(EvaluationResponse, evaluation, path=["response"])

    @parametrize
    def test_streaming_response_update_overload_2(self, client: SGPClient) -> None:
        with client.evaluations.with_streaming_response.update(
            evaluation_id="evaluation_id",
            restore=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = response.parse()
            assert_matches_type(EvaluationResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update_overload_2(self, client: SGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluation_id` but received ''"):
            client.evaluations.with_raw_response.update(
                evaluation_id="",
                restore=True,
            )

    @parametrize
    def test_method_list(self, client: SGPClient) -> None:
        evaluation = client.evaluations.list()
        assert_matches_type(EvaluationListResponse, evaluation, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: SGPClient) -> None:
        evaluation = client.evaluations.list(
            account_id="account_id",
            include_archived=True,
            limit=1,
            page=1,
            sort_by=["status:asc", "status:desc", "application_spec_id:asc"],
            view=["ApplicationSpec", "AsyncJobs", "EvaluationConfig"],
        )
        assert_matches_type(EvaluationListResponse, evaluation, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: SGPClient) -> None:
        response = client.evaluations.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = response.parse()
        assert_matches_type(EvaluationListResponse, evaluation, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: SGPClient) -> None:
        with client.evaluations.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = response.parse()
            assert_matches_type(EvaluationListResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: SGPClient) -> None:
        evaluation = client.evaluations.delete(
            "evaluation_id",
        )
        assert_matches_type(DeleteResponse, evaluation, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: SGPClient) -> None:
        response = client.evaluations.with_raw_response.delete(
            "evaluation_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = response.parse()
        assert_matches_type(DeleteResponse, evaluation, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: SGPClient) -> None:
        with client.evaluations.with_streaming_response.delete(
            "evaluation_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = response.parse()
            assert_matches_type(DeleteResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: SGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluation_id` but received ''"):
            client.evaluations.with_raw_response.delete(
                "",
            )

    @parametrize
    def test_method_claim_task(self, client: SGPClient) -> None:
        evaluation = client.evaluations.claim_task(
            "evaluation_id",
        )
        assert_matches_type(TaskResponse, evaluation, path=["response"])

    @parametrize
    def test_raw_response_claim_task(self, client: SGPClient) -> None:
        response = client.evaluations.with_raw_response.claim_task(
            "evaluation_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = response.parse()
        assert_matches_type(TaskResponse, evaluation, path=["response"])

    @parametrize
    def test_streaming_response_claim_task(self, client: SGPClient) -> None:
        with client.evaluations.with_streaming_response.claim_task(
            "evaluation_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = response.parse()
            assert_matches_type(TaskResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_claim_task(self, client: SGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluation_id` but received ''"):
            client.evaluations.with_raw_response.claim_task(
                "",
            )


class TestAsyncEvaluations:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create_overload_1(self, async_client: AsyncSGPClient) -> None:
        evaluation = await async_client.evaluations.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            application_variant_id="application_variant_id",
            description="description",
            evaluation_dataset_id="evaluation_dataset_id",
            name="name",
        )
        assert_matches_type(EvaluationResponse, evaluation, path=["response"])

    @parametrize
    async def test_method_create_with_all_params_overload_1(self, async_client: AsyncSGPClient) -> None:
        evaluation = await async_client.evaluations.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            application_variant_id="application_variant_id",
            description="description",
            evaluation_dataset_id="evaluation_dataset_id",
            name="name",
            evaluation_config={},
            evaluation_config_id="evaluation_config_id",
            evaluation_dataset_version=0,
            tags={},
            type="builder",
        )
        assert_matches_type(EvaluationResponse, evaluation, path=["response"])

    @parametrize
    async def test_raw_response_create_overload_1(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.evaluations.with_raw_response.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            application_variant_id="application_variant_id",
            description="description",
            evaluation_dataset_id="evaluation_dataset_id",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = await response.parse()
        assert_matches_type(EvaluationResponse, evaluation, path=["response"])

    @parametrize
    async def test_streaming_response_create_overload_1(self, async_client: AsyncSGPClient) -> None:
        async with async_client.evaluations.with_streaming_response.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            application_variant_id="application_variant_id",
            description="description",
            evaluation_dataset_id="evaluation_dataset_id",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = await response.parse()
            assert_matches_type(EvaluationResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_create_overload_2(self, async_client: AsyncSGPClient) -> None:
        evaluation = await async_client.evaluations.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            description="description",
            name="name",
        )
        assert_matches_type(EvaluationResponse, evaluation, path=["response"])

    @parametrize
    async def test_method_create_with_all_params_overload_2(self, async_client: AsyncSGPClient) -> None:
        evaluation = await async_client.evaluations.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            description="description",
            name="name",
            application_variant_id="application_variant_id",
            evaluation_config={},
            evaluation_config_id="evaluation_config_id",
            tags={},
            type="default",
        )
        assert_matches_type(EvaluationResponse, evaluation, path=["response"])

    @parametrize
    async def test_raw_response_create_overload_2(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.evaluations.with_raw_response.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            description="description",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = await response.parse()
        assert_matches_type(EvaluationResponse, evaluation, path=["response"])

    @parametrize
    async def test_streaming_response_create_overload_2(self, async_client: AsyncSGPClient) -> None:
        async with async_client.evaluations.with_streaming_response.create(
            account_id="account_id",
            application_spec_id="application_spec_id",
            description="description",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = await response.parse()
            assert_matches_type(EvaluationResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncSGPClient) -> None:
        evaluation = await async_client.evaluations.retrieve(
            evaluation_id="evaluation_id",
        )
        assert_matches_type(EvaluationResponseWithViews, evaluation, path=["response"])

    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncSGPClient) -> None:
        evaluation = await async_client.evaluations.retrieve(
            evaluation_id="evaluation_id",
            view=["ApplicationSpec", "AsyncJobs", "EvaluationConfig"],
        )
        assert_matches_type(EvaluationResponseWithViews, evaluation, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.evaluations.with_raw_response.retrieve(
            evaluation_id="evaluation_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = await response.parse()
        assert_matches_type(EvaluationResponseWithViews, evaluation, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncSGPClient) -> None:
        async with async_client.evaluations.with_streaming_response.retrieve(
            evaluation_id="evaluation_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = await response.parse()
            assert_matches_type(EvaluationResponseWithViews, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncSGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluation_id` but received ''"):
            await async_client.evaluations.with_raw_response.retrieve(
                evaluation_id="",
            )

    @parametrize
    async def test_method_update_overload_1(self, async_client: AsyncSGPClient) -> None:
        evaluation = await async_client.evaluations.update(
            evaluation_id="evaluation_id",
        )
        assert_matches_type(EvaluationResponse, evaluation, path=["response"])

    @parametrize
    async def test_method_update_with_all_params_overload_1(self, async_client: AsyncSGPClient) -> None:
        evaluation = await async_client.evaluations.update(
            evaluation_id="evaluation_id",
            application_spec_id="application_spec_id",
            application_variant_id="application_variant_id",
            description="description",
            evaluation_config={},
            evaluation_config_id="evaluation_config_id",
            evaluation_type="llm_benchmark",
            name="name",
            restore=True,
            tags={},
        )
        assert_matches_type(EvaluationResponse, evaluation, path=["response"])

    @parametrize
    async def test_raw_response_update_overload_1(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.evaluations.with_raw_response.update(
            evaluation_id="evaluation_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = await response.parse()
        assert_matches_type(EvaluationResponse, evaluation, path=["response"])

    @parametrize
    async def test_streaming_response_update_overload_1(self, async_client: AsyncSGPClient) -> None:
        async with async_client.evaluations.with_streaming_response.update(
            evaluation_id="evaluation_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = await response.parse()
            assert_matches_type(EvaluationResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update_overload_1(self, async_client: AsyncSGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluation_id` but received ''"):
            await async_client.evaluations.with_raw_response.update(
                evaluation_id="",
            )

    @parametrize
    async def test_method_update_overload_2(self, async_client: AsyncSGPClient) -> None:
        evaluation = await async_client.evaluations.update(
            evaluation_id="evaluation_id",
            restore=True,
        )
        assert_matches_type(EvaluationResponse, evaluation, path=["response"])

    @parametrize
    async def test_raw_response_update_overload_2(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.evaluations.with_raw_response.update(
            evaluation_id="evaluation_id",
            restore=True,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = await response.parse()
        assert_matches_type(EvaluationResponse, evaluation, path=["response"])

    @parametrize
    async def test_streaming_response_update_overload_2(self, async_client: AsyncSGPClient) -> None:
        async with async_client.evaluations.with_streaming_response.update(
            evaluation_id="evaluation_id",
            restore=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = await response.parse()
            assert_matches_type(EvaluationResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update_overload_2(self, async_client: AsyncSGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluation_id` but received ''"):
            await async_client.evaluations.with_raw_response.update(
                evaluation_id="",
                restore=True,
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncSGPClient) -> None:
        evaluation = await async_client.evaluations.list()
        assert_matches_type(EvaluationListResponse, evaluation, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncSGPClient) -> None:
        evaluation = await async_client.evaluations.list(
            account_id="account_id",
            include_archived=True,
            limit=1,
            page=1,
            sort_by=["status:asc", "status:desc", "application_spec_id:asc"],
            view=["ApplicationSpec", "AsyncJobs", "EvaluationConfig"],
        )
        assert_matches_type(EvaluationListResponse, evaluation, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.evaluations.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = await response.parse()
        assert_matches_type(EvaluationListResponse, evaluation, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncSGPClient) -> None:
        async with async_client.evaluations.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = await response.parse()
            assert_matches_type(EvaluationListResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncSGPClient) -> None:
        evaluation = await async_client.evaluations.delete(
            "evaluation_id",
        )
        assert_matches_type(DeleteResponse, evaluation, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.evaluations.with_raw_response.delete(
            "evaluation_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = await response.parse()
        assert_matches_type(DeleteResponse, evaluation, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncSGPClient) -> None:
        async with async_client.evaluations.with_streaming_response.delete(
            "evaluation_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = await response.parse()
            assert_matches_type(DeleteResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncSGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluation_id` but received ''"):
            await async_client.evaluations.with_raw_response.delete(
                "",
            )

    @parametrize
    async def test_method_claim_task(self, async_client: AsyncSGPClient) -> None:
        evaluation = await async_client.evaluations.claim_task(
            "evaluation_id",
        )
        assert_matches_type(TaskResponse, evaluation, path=["response"])

    @parametrize
    async def test_raw_response_claim_task(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.evaluations.with_raw_response.claim_task(
            "evaluation_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = await response.parse()
        assert_matches_type(TaskResponse, evaluation, path=["response"])

    @parametrize
    async def test_streaming_response_claim_task(self, async_client: AsyncSGPClient) -> None:
        async with async_client.evaluations.with_streaming_response.claim_task(
            "evaluation_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = await response.parse()
            assert_matches_type(TaskResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_claim_task(self, async_client: AsyncSGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluation_id` but received ''"):
            await async_client.evaluations.with_raw_response.claim_task(
                "",
            )
