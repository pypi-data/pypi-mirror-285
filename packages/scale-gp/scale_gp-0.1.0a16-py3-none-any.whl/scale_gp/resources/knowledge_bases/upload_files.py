# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Mapping, cast

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven, FileTypes
from ..._utils import (
    extract_files,
    maybe_transform,
    deepcopy_minimal,
    async_maybe_transform,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.knowledge_bases import upload_file_create_params
from ...types.knowledge_bases.create_knowledge_base_v2_uploads_from_files_response import (
    CreateKnowledgeBaseV2UploadsFromFilesResponse,
)

__all__ = ["UploadFilesResource", "AsyncUploadFilesResource"]


class UploadFilesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> UploadFilesResourceWithRawResponse:
        return UploadFilesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> UploadFilesResourceWithStreamingResponse:
        return UploadFilesResourceWithStreamingResponse(self)

    def create(
        self,
        knowledge_base_id: str,
        *,
        chunking_strategy_config: str,
        data_source_config: str,
        files: List[FileTypes],
        force_reupload: bool,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CreateKnowledgeBaseV2UploadsFromFilesResponse:
        """
        Submit Upload Job with local files

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not knowledge_base_id:
            raise ValueError(f"Expected a non-empty value for `knowledge_base_id` but received {knowledge_base_id!r}")
        body = deepcopy_minimal(
            {
                "chunking_strategy_config": chunking_strategy_config,
                "data_source_config": data_source_config,
                "files": files,
                "force_reupload": force_reupload,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["files", "<array>"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            f"/v4/knowledge-bases/{knowledge_base_id}/upload_files",
            body=maybe_transform(body, upload_file_create_params.UploadFileCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CreateKnowledgeBaseV2UploadsFromFilesResponse,
        )


class AsyncUploadFilesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncUploadFilesResourceWithRawResponse:
        return AsyncUploadFilesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncUploadFilesResourceWithStreamingResponse:
        return AsyncUploadFilesResourceWithStreamingResponse(self)

    async def create(
        self,
        knowledge_base_id: str,
        *,
        chunking_strategy_config: str,
        data_source_config: str,
        files: List[FileTypes],
        force_reupload: bool,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CreateKnowledgeBaseV2UploadsFromFilesResponse:
        """
        Submit Upload Job with local files

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not knowledge_base_id:
            raise ValueError(f"Expected a non-empty value for `knowledge_base_id` but received {knowledge_base_id!r}")
        body = deepcopy_minimal(
            {
                "chunking_strategy_config": chunking_strategy_config,
                "data_source_config": data_source_config,
                "files": files,
                "force_reupload": force_reupload,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["files", "<array>"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            f"/v4/knowledge-bases/{knowledge_base_id}/upload_files",
            body=await async_maybe_transform(body, upload_file_create_params.UploadFileCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CreateKnowledgeBaseV2UploadsFromFilesResponse,
        )


class UploadFilesResourceWithRawResponse:
    def __init__(self, upload_files: UploadFilesResource) -> None:
        self._upload_files = upload_files

        self.create = to_raw_response_wrapper(
            upload_files.create,
        )


class AsyncUploadFilesResourceWithRawResponse:
    def __init__(self, upload_files: AsyncUploadFilesResource) -> None:
        self._upload_files = upload_files

        self.create = async_to_raw_response_wrapper(
            upload_files.create,
        )


class UploadFilesResourceWithStreamingResponse:
    def __init__(self, upload_files: UploadFilesResource) -> None:
        self._upload_files = upload_files

        self.create = to_streamed_response_wrapper(
            upload_files.create,
        )


class AsyncUploadFilesResourceWithStreamingResponse:
    def __init__(self, upload_files: AsyncUploadFilesResource) -> None:
        self._upload_files = upload_files

        self.create = async_to_streamed_response_wrapper(
            upload_files.create,
        )
