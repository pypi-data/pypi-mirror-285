# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from scale_gp import SGPClient, AsyncSGPClient
from tests.utils import assert_matches_type
from scale_gp.types.applications import UploadFileCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUploadFiles:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: SGPClient) -> None:
        upload_file = client.applications.upload_files.create(
            files=[b"raw file contents", b"raw file contents", b"raw file contents"],
        )
        assert_matches_type(UploadFileCreateResponse, upload_file, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: SGPClient) -> None:
        upload_file = client.applications.upload_files.create(
            files=[b"raw file contents", b"raw file contents", b"raw file contents"],
            account_id="account_id",
        )
        assert_matches_type(UploadFileCreateResponse, upload_file, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: SGPClient) -> None:
        response = client.applications.upload_files.with_raw_response.create(
            files=[b"raw file contents", b"raw file contents", b"raw file contents"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload_file = response.parse()
        assert_matches_type(UploadFileCreateResponse, upload_file, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: SGPClient) -> None:
        with client.applications.upload_files.with_streaming_response.create(
            files=[b"raw file contents", b"raw file contents", b"raw file contents"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload_file = response.parse()
            assert_matches_type(UploadFileCreateResponse, upload_file, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncUploadFiles:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncSGPClient) -> None:
        upload_file = await async_client.applications.upload_files.create(
            files=[b"raw file contents", b"raw file contents", b"raw file contents"],
        )
        assert_matches_type(UploadFileCreateResponse, upload_file, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncSGPClient) -> None:
        upload_file = await async_client.applications.upload_files.create(
            files=[b"raw file contents", b"raw file contents", b"raw file contents"],
            account_id="account_id",
        )
        assert_matches_type(UploadFileCreateResponse, upload_file, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncSGPClient) -> None:
        response = await async_client.applications.upload_files.with_raw_response.create(
            files=[b"raw file contents", b"raw file contents", b"raw file contents"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload_file = await response.parse()
        assert_matches_type(UploadFileCreateResponse, upload_file, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncSGPClient) -> None:
        async with async_client.applications.upload_files.with_streaming_response.create(
            files=[b"raw file contents", b"raw file contents", b"raw file contents"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload_file = await response.parse()
            assert_matches_type(UploadFileCreateResponse, upload_file, path=["response"])

        assert cast(Any, response.is_closed) is True
