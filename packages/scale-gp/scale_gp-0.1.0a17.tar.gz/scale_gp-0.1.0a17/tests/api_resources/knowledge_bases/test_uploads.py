# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from scale_gp import SGPClient, AsyncSGPClient
from tests.utils import assert_matches_type
from scale_gp.types.knowledge_bases import (
    KnowledgeBaseUploadList,
    GetKnowledgeBaseV2UploadResponse,
    CancelKnowledgeBaseV2UploadResponse,
    CreateKnowledgeBaseV2UploadResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUploads:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create_overload_1(self, client: SGPClient) -> None:
        upload = client.knowledge_bases.uploads.create(
            knowledge_base_id="knowledge_base_id",
            data_source_config={
                "source": "S3",
                "s3_bucket": "s3_bucket",
                "aws_region": "aws_region",
                "aws_account_id": "aws_account_id",
            },
        )
        assert_matches_type(CreateKnowledgeBaseV2UploadResponse, upload, path=["response"])

    @parametrize
    def test_method_create_with_all_params_overload_1(self, client: SGPClient) -> None:
        upload = client.knowledge_bases.uploads.create(
            knowledge_base_id="knowledge_base_id",
            data_source_config={
                "source": "S3",
                "s3_bucket": "s3_bucket",
                "s3_prefix": "s3_prefix",
                "aws_region": "aws_region",
                "aws_account_id": "aws_account_id",
            },
            chunking_strategy_config={
                "strategy": "character",
                "separator": "separator",
                "chunk_size": 1,
                "chunk_overlap": 0,
            },
            data_source_auth_config={
                "encrypted": True,
                "source": "SharePoint",
                "client_secret": "client_secret",
            },
            force_reupload=True,
        )
        assert_matches_type(CreateKnowledgeBaseV2UploadResponse, upload, path=["response"])

    @parametrize
    def test_raw_response_create_overload_1(self, client: SGPClient) -> None:
        response = client.knowledge_bases.uploads.with_raw_response.create(
            knowledge_base_id="knowledge_base_id",
            data_source_config={
                "source": "S3",
                "s3_bucket": "s3_bucket",
                "aws_region": "aws_region",
                "aws_account_id": "aws_account_id",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = response.parse()
        assert_matches_type(CreateKnowledgeBaseV2UploadResponse, upload, path=["response"])

    @parametrize
    def test_streaming_response_create_overload_1(self, client: SGPClient) -> None:
        with client.knowledge_bases.uploads.with_streaming_response.create(
            knowledge_base_id="knowledge_base_id",
            data_source_config={
                "source": "S3",
                "s3_bucket": "s3_bucket",
                "aws_region": "aws_region",
                "aws_account_id": "aws_account_id",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = response.parse()
            assert_matches_type(CreateKnowledgeBaseV2UploadResponse, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create_overload_1(self, client: SGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            client.knowledge_bases.uploads.with_raw_response.create(
                knowledge_base_id="",
                data_source_config={
                    "source": "S3",
                    "s3_bucket": "s3_bucket",
                    "aws_region": "aws_region",
                    "aws_account_id": "aws_account_id",
                },
            )

    @parametrize
    def test_method_create_overload_2(self, client: SGPClient) -> None:
        upload = client.knowledge_bases.uploads.create(
            knowledge_base_id="knowledge_base_id",
            data_source_config={
                "source": "LocalChunks",
                "artifact_name": "artifact_name",
                "artifact_uri": "artifact_uri",
            },
        )
        assert_matches_type(CreateKnowledgeBaseV2UploadResponse, upload, path=["response"])

    @parametrize
    def test_method_create_with_all_params_overload_2(self, client: SGPClient) -> None:
        upload = client.knowledge_bases.uploads.create(
            knowledge_base_id="knowledge_base_id",
            data_source_config={
                "source": "LocalChunks",
                "artifact_name": "artifact_name",
                "artifact_uri": "artifact_uri",
                "deduplication_strategy": "Overwrite",
            },
            chunks=[
                {
                    "text": "text",
                    "chunk_position": 0,
                    "metadata": {},
                },
                {
                    "text": "text",
                    "chunk_position": 0,
                    "metadata": {},
                },
                {
                    "text": "text",
                    "chunk_position": 0,
                    "metadata": {},
                },
            ],
            force_reupload=True,
        )
        assert_matches_type(CreateKnowledgeBaseV2UploadResponse, upload, path=["response"])

    @parametrize
    def test_raw_response_create_overload_2(self, client: SGPClient) -> None:
        response = client.knowledge_bases.uploads.with_raw_response.create(
            knowledge_base_id="knowledge_base_id",
            data_source_config={
                "source": "LocalChunks",
                "artifact_name": "artifact_name",
                "artifact_uri": "artifact_uri",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = response.parse()
        assert_matches_type(CreateKnowledgeBaseV2UploadResponse, upload, path=["response"])

    @parametrize
    def test_streaming_response_create_overload_2(self, client: SGPClient) -> None:
        with client.knowledge_bases.uploads.with_streaming_response.create(
            knowledge_base_id="knowledge_base_id",
            data_source_config={
                "source": "LocalChunks",
                "artifact_name": "artifact_name",
                "artifact_uri": "artifact_uri",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = response.parse()
            assert_matches_type(CreateKnowledgeBaseV2UploadResponse, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create_overload_2(self, client: SGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            client.knowledge_bases.uploads.with_raw_response.create(
                knowledge_base_id="",
                data_source_config={
                    "source": "LocalChunks",
                    "artifact_name": "artifact_name",
                    "artifact_uri": "artifact_uri",
                },
            )

    @parametrize
    def test_method_create_overload_3(self, client: SGPClient) -> None:
        upload = client.knowledge_bases.uploads.create(
            knowledge_base_id="knowledge_base_id",
            chunking_strategy_config={"strategy": "character"},
            data_source_id="data_source_id",
        )
        assert_matches_type(CreateKnowledgeBaseV2UploadResponse, upload, path=["response"])

    @parametrize
    def test_method_create_with_all_params_overload_3(self, client: SGPClient) -> None:
        upload = client.knowledge_bases.uploads.create(
            knowledge_base_id="knowledge_base_id",
            chunking_strategy_config={
                "strategy": "character",
                "separator": "separator",
                "chunk_size": 1,
                "chunk_overlap": 0,
            },
            data_source_id="data_source_id",
            force_reupload=True,
        )
        assert_matches_type(CreateKnowledgeBaseV2UploadResponse, upload, path=["response"])

    @parametrize
    def test_raw_response_create_overload_3(self, client: SGPClient) -> None:
        response = client.knowledge_bases.uploads.with_raw_response.create(
            knowledge_base_id="knowledge_base_id",
            chunking_strategy_config={"strategy": "character"},
            data_source_id="data_source_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = response.parse()
        assert_matches_type(CreateKnowledgeBaseV2UploadResponse, upload, path=["response"])

    @parametrize
    def test_streaming_response_create_overload_3(self, client: SGPClient) -> None:
        with client.knowledge_bases.uploads.with_streaming_response.create(
            knowledge_base_id="knowledge_base_id",
            chunking_strategy_config={"strategy": "character"},
            data_source_id="data_source_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = response.parse()
            assert_matches_type(CreateKnowledgeBaseV2UploadResponse, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create_overload_3(self, client: SGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            client.knowledge_bases.uploads.with_raw_response.create(
                knowledge_base_id="",
                chunking_strategy_config={"strategy": "character"},
                data_source_id="data_source_id",
            )

    @parametrize
    def test_method_retrieve(self, client: SGPClient) -> None:
        upload = client.knowledge_bases.uploads.retrieve(
            upload_id="upload_id",
            knowledge_base_id="knowledge_base_id",
        )
        assert_matches_type(GetKnowledgeBaseV2UploadResponse, upload, path=["response"])

    @parametrize
    def test_method_retrieve_with_all_params(self, client: SGPClient) -> None:
        upload = client.knowledge_bases.uploads.retrieve(
            upload_id="upload_id",
            knowledge_base_id="knowledge_base_id",
            include_artifact_list=True,
        )
        assert_matches_type(GetKnowledgeBaseV2UploadResponse, upload, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: SGPClient) -> None:
        response = client.knowledge_bases.uploads.with_raw_response.retrieve(
            upload_id="upload_id",
            knowledge_base_id="knowledge_base_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = response.parse()
        assert_matches_type(GetKnowledgeBaseV2UploadResponse, upload, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: SGPClient) -> None:
        with client.knowledge_bases.uploads.with_streaming_response.retrieve(
            upload_id="upload_id",
            knowledge_base_id="knowledge_base_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = response.parse()
            assert_matches_type(GetKnowledgeBaseV2UploadResponse, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: SGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            client.knowledge_bases.uploads.with_raw_response.retrieve(
                upload_id="upload_id",
                knowledge_base_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `upload_id` but received ''"):
            client.knowledge_bases.uploads.with_raw_response.retrieve(
                upload_id="",
                knowledge_base_id="knowledge_base_id",
            )

    @parametrize
    def test_method_list(self, client: SGPClient) -> None:
        upload = client.knowledge_bases.uploads.list(
            knowledge_base_id="knowledge_base_id",
        )
        assert_matches_type(KnowledgeBaseUploadList, upload, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: SGPClient) -> None:
        upload = client.knowledge_bases.uploads.list(
            knowledge_base_id="knowledge_base_id",
            limit=1,
            page=1,
            status="Running",
        )
        assert_matches_type(KnowledgeBaseUploadList, upload, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: SGPClient) -> None:
        response = client.knowledge_bases.uploads.with_raw_response.list(
            knowledge_base_id="knowledge_base_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = response.parse()
        assert_matches_type(KnowledgeBaseUploadList, upload, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: SGPClient) -> None:
        with client.knowledge_bases.uploads.with_streaming_response.list(
            knowledge_base_id="knowledge_base_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = response.parse()
            assert_matches_type(KnowledgeBaseUploadList, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: SGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            client.knowledge_bases.uploads.with_raw_response.list(
                knowledge_base_id="",
            )

    @parametrize
    def test_method_cancel(self, client: SGPClient) -> None:
        upload = client.knowledge_bases.uploads.cancel(
            upload_id="upload_id",
            knowledge_base_id="knowledge_base_id",
        )
        assert_matches_type(CancelKnowledgeBaseV2UploadResponse, upload, path=["response"])

    @parametrize
    def test_raw_response_cancel(self, client: SGPClient) -> None:
        response = client.knowledge_bases.uploads.with_raw_response.cancel(
            upload_id="upload_id",
            knowledge_base_id="knowledge_base_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = response.parse()
        assert_matches_type(CancelKnowledgeBaseV2UploadResponse, upload, path=["response"])

    @parametrize
    def test_streaming_response_cancel(self, client: SGPClient) -> None:
        with client.knowledge_bases.uploads.with_streaming_response.cancel(
            upload_id="upload_id",
            knowledge_base_id="knowledge_base_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = response.parse()
            assert_matches_type(CancelKnowledgeBaseV2UploadResponse, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_cancel(self, client: SGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            client.knowledge_bases.uploads.with_raw_response.cancel(
                upload_id="upload_id",
                knowledge_base_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `upload_id` but received ''"):
            client.knowledge_bases.uploads.with_raw_response.cancel(
                upload_id="",
                knowledge_base_id="knowledge_base_id",
            )


class TestAsyncUploads:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create_overload_1(self, async_client: AsyncSGPClient) -> None:
        upload = await async_client.knowledge_bases.uploads.create(
            knowledge_base_id="knowledge_base_id",
            data_source_config={
                "source": "S3",
                "s3_bucket": "s3_bucket",
                "aws_region": "aws_region",
                "aws_account_id": "aws_account_id",
            },
        )
        assert_matches_type(CreateKnowledgeBaseV2UploadResponse, upload, path=["response"])

    @parametrize
    async def test_method_create_with_all_params_overload_1(self, async_client: AsyncSGPClient) -> None:
        upload = await async_client.knowledge_bases.uploads.create(
            knowledge_base_id="knowledge_base_id",
            data_source_config={
                "source": "S3",
                "s3_bucket": "s3_bucket",
                "s3_prefix": "s3_prefix",
                "aws_region": "aws_region",
                "aws_account_id": "aws_account_id",
            },
            chunking_strategy_config={
                "strategy": "character",
                "separator": "separator",
                "chunk_size": 1,
                "chunk_overlap": 0,
            },
            data_source_auth_config={
                "encrypted": True,
                "source": "SharePoint",
                "client_secret": "client_secret",
            },
            force_reupload=True,
        )
        assert_matches_type(CreateKnowledgeBaseV2UploadResponse, upload, path=["response"])

    @parametrize
    async def test_raw_response_create_overload_1(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.knowledge_bases.uploads.with_raw_response.create(
            knowledge_base_id="knowledge_base_id",
            data_source_config={
                "source": "S3",
                "s3_bucket": "s3_bucket",
                "aws_region": "aws_region",
                "aws_account_id": "aws_account_id",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = await response.parse()
        assert_matches_type(CreateKnowledgeBaseV2UploadResponse, upload, path=["response"])

    @parametrize
    async def test_streaming_response_create_overload_1(self, async_client: AsyncSGPClient) -> None:
        async with async_client.knowledge_bases.uploads.with_streaming_response.create(
            knowledge_base_id="knowledge_base_id",
            data_source_config={
                "source": "S3",
                "s3_bucket": "s3_bucket",
                "aws_region": "aws_region",
                "aws_account_id": "aws_account_id",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = await response.parse()
            assert_matches_type(CreateKnowledgeBaseV2UploadResponse, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create_overload_1(self, async_client: AsyncSGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            await async_client.knowledge_bases.uploads.with_raw_response.create(
                knowledge_base_id="",
                data_source_config={
                    "source": "S3",
                    "s3_bucket": "s3_bucket",
                    "aws_region": "aws_region",
                    "aws_account_id": "aws_account_id",
                },
            )

    @parametrize
    async def test_method_create_overload_2(self, async_client: AsyncSGPClient) -> None:
        upload = await async_client.knowledge_bases.uploads.create(
            knowledge_base_id="knowledge_base_id",
            data_source_config={
                "source": "LocalChunks",
                "artifact_name": "artifact_name",
                "artifact_uri": "artifact_uri",
            },
        )
        assert_matches_type(CreateKnowledgeBaseV2UploadResponse, upload, path=["response"])

    @parametrize
    async def test_method_create_with_all_params_overload_2(self, async_client: AsyncSGPClient) -> None:
        upload = await async_client.knowledge_bases.uploads.create(
            knowledge_base_id="knowledge_base_id",
            data_source_config={
                "source": "LocalChunks",
                "artifact_name": "artifact_name",
                "artifact_uri": "artifact_uri",
                "deduplication_strategy": "Overwrite",
            },
            chunks=[
                {
                    "text": "text",
                    "chunk_position": 0,
                    "metadata": {},
                },
                {
                    "text": "text",
                    "chunk_position": 0,
                    "metadata": {},
                },
                {
                    "text": "text",
                    "chunk_position": 0,
                    "metadata": {},
                },
            ],
            force_reupload=True,
        )
        assert_matches_type(CreateKnowledgeBaseV2UploadResponse, upload, path=["response"])

    @parametrize
    async def test_raw_response_create_overload_2(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.knowledge_bases.uploads.with_raw_response.create(
            knowledge_base_id="knowledge_base_id",
            data_source_config={
                "source": "LocalChunks",
                "artifact_name": "artifact_name",
                "artifact_uri": "artifact_uri",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = await response.parse()
        assert_matches_type(CreateKnowledgeBaseV2UploadResponse, upload, path=["response"])

    @parametrize
    async def test_streaming_response_create_overload_2(self, async_client: AsyncSGPClient) -> None:
        async with async_client.knowledge_bases.uploads.with_streaming_response.create(
            knowledge_base_id="knowledge_base_id",
            data_source_config={
                "source": "LocalChunks",
                "artifact_name": "artifact_name",
                "artifact_uri": "artifact_uri",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = await response.parse()
            assert_matches_type(CreateKnowledgeBaseV2UploadResponse, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create_overload_2(self, async_client: AsyncSGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            await async_client.knowledge_bases.uploads.with_raw_response.create(
                knowledge_base_id="",
                data_source_config={
                    "source": "LocalChunks",
                    "artifact_name": "artifact_name",
                    "artifact_uri": "artifact_uri",
                },
            )

    @parametrize
    async def test_method_create_overload_3(self, async_client: AsyncSGPClient) -> None:
        upload = await async_client.knowledge_bases.uploads.create(
            knowledge_base_id="knowledge_base_id",
            chunking_strategy_config={"strategy": "character"},
            data_source_id="data_source_id",
        )
        assert_matches_type(CreateKnowledgeBaseV2UploadResponse, upload, path=["response"])

    @parametrize
    async def test_method_create_with_all_params_overload_3(self, async_client: AsyncSGPClient) -> None:
        upload = await async_client.knowledge_bases.uploads.create(
            knowledge_base_id="knowledge_base_id",
            chunking_strategy_config={
                "strategy": "character",
                "separator": "separator",
                "chunk_size": 1,
                "chunk_overlap": 0,
            },
            data_source_id="data_source_id",
            force_reupload=True,
        )
        assert_matches_type(CreateKnowledgeBaseV2UploadResponse, upload, path=["response"])

    @parametrize
    async def test_raw_response_create_overload_3(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.knowledge_bases.uploads.with_raw_response.create(
            knowledge_base_id="knowledge_base_id",
            chunking_strategy_config={"strategy": "character"},
            data_source_id="data_source_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = await response.parse()
        assert_matches_type(CreateKnowledgeBaseV2UploadResponse, upload, path=["response"])

    @parametrize
    async def test_streaming_response_create_overload_3(self, async_client: AsyncSGPClient) -> None:
        async with async_client.knowledge_bases.uploads.with_streaming_response.create(
            knowledge_base_id="knowledge_base_id",
            chunking_strategy_config={"strategy": "character"},
            data_source_id="data_source_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = await response.parse()
            assert_matches_type(CreateKnowledgeBaseV2UploadResponse, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create_overload_3(self, async_client: AsyncSGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            await async_client.knowledge_bases.uploads.with_raw_response.create(
                knowledge_base_id="",
                chunking_strategy_config={"strategy": "character"},
                data_source_id="data_source_id",
            )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncSGPClient) -> None:
        upload = await async_client.knowledge_bases.uploads.retrieve(
            upload_id="upload_id",
            knowledge_base_id="knowledge_base_id",
        )
        assert_matches_type(GetKnowledgeBaseV2UploadResponse, upload, path=["response"])

    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncSGPClient) -> None:
        upload = await async_client.knowledge_bases.uploads.retrieve(
            upload_id="upload_id",
            knowledge_base_id="knowledge_base_id",
            include_artifact_list=True,
        )
        assert_matches_type(GetKnowledgeBaseV2UploadResponse, upload, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.knowledge_bases.uploads.with_raw_response.retrieve(
            upload_id="upload_id",
            knowledge_base_id="knowledge_base_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = await response.parse()
        assert_matches_type(GetKnowledgeBaseV2UploadResponse, upload, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncSGPClient) -> None:
        async with async_client.knowledge_bases.uploads.with_streaming_response.retrieve(
            upload_id="upload_id",
            knowledge_base_id="knowledge_base_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = await response.parse()
            assert_matches_type(GetKnowledgeBaseV2UploadResponse, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncSGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            await async_client.knowledge_bases.uploads.with_raw_response.retrieve(
                upload_id="upload_id",
                knowledge_base_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `upload_id` but received ''"):
            await async_client.knowledge_bases.uploads.with_raw_response.retrieve(
                upload_id="",
                knowledge_base_id="knowledge_base_id",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncSGPClient) -> None:
        upload = await async_client.knowledge_bases.uploads.list(
            knowledge_base_id="knowledge_base_id",
        )
        assert_matches_type(KnowledgeBaseUploadList, upload, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncSGPClient) -> None:
        upload = await async_client.knowledge_bases.uploads.list(
            knowledge_base_id="knowledge_base_id",
            limit=1,
            page=1,
            status="Running",
        )
        assert_matches_type(KnowledgeBaseUploadList, upload, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.knowledge_bases.uploads.with_raw_response.list(
            knowledge_base_id="knowledge_base_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = await response.parse()
        assert_matches_type(KnowledgeBaseUploadList, upload, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncSGPClient) -> None:
        async with async_client.knowledge_bases.uploads.with_streaming_response.list(
            knowledge_base_id="knowledge_base_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = await response.parse()
            assert_matches_type(KnowledgeBaseUploadList, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncSGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            await async_client.knowledge_bases.uploads.with_raw_response.list(
                knowledge_base_id="",
            )

    @parametrize
    async def test_method_cancel(self, async_client: AsyncSGPClient) -> None:
        upload = await async_client.knowledge_bases.uploads.cancel(
            upload_id="upload_id",
            knowledge_base_id="knowledge_base_id",
        )
        assert_matches_type(CancelKnowledgeBaseV2UploadResponse, upload, path=["response"])

    @parametrize
    async def test_raw_response_cancel(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.knowledge_bases.uploads.with_raw_response.cancel(
            upload_id="upload_id",
            knowledge_base_id="knowledge_base_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = await response.parse()
        assert_matches_type(CancelKnowledgeBaseV2UploadResponse, upload, path=["response"])

    @parametrize
    async def test_streaming_response_cancel(self, async_client: AsyncSGPClient) -> None:
        async with async_client.knowledge_bases.uploads.with_streaming_response.cancel(
            upload_id="upload_id",
            knowledge_base_id="knowledge_base_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = await response.parse()
            assert_matches_type(CancelKnowledgeBaseV2UploadResponse, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_cancel(self, async_client: AsyncSGPClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `knowledge_base_id` but received ''"):
            await async_client.knowledge_bases.uploads.with_raw_response.cancel(
                upload_id="upload_id",
                knowledge_base_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `upload_id` but received ''"):
            await async_client.knowledge_bases.uploads.with_raw_response.cancel(
                upload_id="",
                knowledge_base_id="knowledge_base_id",
            )
