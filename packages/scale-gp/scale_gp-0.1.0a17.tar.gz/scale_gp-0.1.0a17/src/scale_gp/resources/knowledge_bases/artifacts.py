# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import (
    maybe_transform,
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
from ...types.knowledge_bases import artifact_list_params, artifact_retrieve_params
from ...types.knowledge_bases.artifact_info_list import ArtifactInfoList
from ...types.knowledge_bases.get_knowledge_base_v2_artifact_response import GetKnowledgeBaseV2ArtifactResponse

__all__ = ["ArtifactsResource", "AsyncArtifactsResource"]


class ArtifactsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ArtifactsResourceWithRawResponse:
        return ArtifactsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ArtifactsResourceWithStreamingResponse:
        return ArtifactsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        artifact_id: str,
        *,
        knowledge_base_id: str,
        status_filter: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GetKnowledgeBaseV2ArtifactResponse:
        """
        ### Description

        Gets the details of an artifact tracked by a knowledge base.

        ### Details

        This API can be used to get information about a single artifact by ID. This
        response will contain much more detail about the artifact than show in the
        [List Artifacts API](https://scale-egp.readme.io/reference/list_knowledge_base_artifacts_v2)
        call. To use this API, pass in the `knowledge_base_id` and `artifact_id` that
        were returned from your
        [List Artifacts API](https://scale-egp.readme.io/reference/list_knowledge_base_artifacts_v2)
        call as path parameters.

        #### Compatibility with V1

        V2 and V1 Knowledge Bases are entirely separate and not backwards compatible.
        Users who have existing V1 knowledge bases will need to migrate their data to V2
        knowledge bases.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not knowledge_base_id:
            raise ValueError(f"Expected a non-empty value for `knowledge_base_id` but received {knowledge_base_id!r}")
        if not artifact_id:
            raise ValueError(f"Expected a non-empty value for `artifact_id` but received {artifact_id!r}")
        return self._get(
            f"/v4/knowledge-bases/{knowledge_base_id}/artifacts/{artifact_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"status_filter": status_filter}, artifact_retrieve_params.ArtifactRetrieveParams
                ),
            ),
            cast_to=GetKnowledgeBaseV2ArtifactResponse,
        )

    def list(
        self,
        knowledge_base_id: str,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        status: Literal["Pending", "Completed", "Failed", "Uploading", "Deleting"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ArtifactInfoList:
        """
        ### Description

        List all artifacts tracked by a knowledge base.

        ### Details

        This API can be used to list all artifacts that are currently tracked in a
        knowledge base. This API will return the details of all artifacts including
        their IDs, names, the source they originated from, their current upload
        statuses, and the timestamps for their creation and last-updated time.

        This list should be consistent with the state of the data source at the time of
        start of the latest upload. If the state is not consistent, create a new upload
        to update the knowledge base to reflect the latest state of the data source.

        Args:
          limit: Maximum number of artifacts to be returned by the given endpoint. Defaults to
              100 and cannot be greater than 10k.

          page: Page number for pagination to be returned by the given endpoint. Starts at page
              1

          status: An enumeration.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not knowledge_base_id:
            raise ValueError(f"Expected a non-empty value for `knowledge_base_id` but received {knowledge_base_id!r}")
        return self._get(
            f"/v4/knowledge-bases/{knowledge_base_id}/artifacts",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "page": page,
                        "status": status,
                    },
                    artifact_list_params.ArtifactListParams,
                ),
            ),
            cast_to=ArtifactInfoList,
        )


class AsyncArtifactsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncArtifactsResourceWithRawResponse:
        return AsyncArtifactsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncArtifactsResourceWithStreamingResponse:
        return AsyncArtifactsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        artifact_id: str,
        *,
        knowledge_base_id: str,
        status_filter: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GetKnowledgeBaseV2ArtifactResponse:
        """
        ### Description

        Gets the details of an artifact tracked by a knowledge base.

        ### Details

        This API can be used to get information about a single artifact by ID. This
        response will contain much more detail about the artifact than show in the
        [List Artifacts API](https://scale-egp.readme.io/reference/list_knowledge_base_artifacts_v2)
        call. To use this API, pass in the `knowledge_base_id` and `artifact_id` that
        were returned from your
        [List Artifacts API](https://scale-egp.readme.io/reference/list_knowledge_base_artifacts_v2)
        call as path parameters.

        #### Compatibility with V1

        V2 and V1 Knowledge Bases are entirely separate and not backwards compatible.
        Users who have existing V1 knowledge bases will need to migrate their data to V2
        knowledge bases.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not knowledge_base_id:
            raise ValueError(f"Expected a non-empty value for `knowledge_base_id` but received {knowledge_base_id!r}")
        if not artifact_id:
            raise ValueError(f"Expected a non-empty value for `artifact_id` but received {artifact_id!r}")
        return await self._get(
            f"/v4/knowledge-bases/{knowledge_base_id}/artifacts/{artifact_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"status_filter": status_filter}, artifact_retrieve_params.ArtifactRetrieveParams
                ),
            ),
            cast_to=GetKnowledgeBaseV2ArtifactResponse,
        )

    async def list(
        self,
        knowledge_base_id: str,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        status: Literal["Pending", "Completed", "Failed", "Uploading", "Deleting"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ArtifactInfoList:
        """
        ### Description

        List all artifacts tracked by a knowledge base.

        ### Details

        This API can be used to list all artifacts that are currently tracked in a
        knowledge base. This API will return the details of all artifacts including
        their IDs, names, the source they originated from, their current upload
        statuses, and the timestamps for their creation and last-updated time.

        This list should be consistent with the state of the data source at the time of
        start of the latest upload. If the state is not consistent, create a new upload
        to update the knowledge base to reflect the latest state of the data source.

        Args:
          limit: Maximum number of artifacts to be returned by the given endpoint. Defaults to
              100 and cannot be greater than 10k.

          page: Page number for pagination to be returned by the given endpoint. Starts at page
              1

          status: An enumeration.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not knowledge_base_id:
            raise ValueError(f"Expected a non-empty value for `knowledge_base_id` but received {knowledge_base_id!r}")
        return await self._get(
            f"/v4/knowledge-bases/{knowledge_base_id}/artifacts",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "limit": limit,
                        "page": page,
                        "status": status,
                    },
                    artifact_list_params.ArtifactListParams,
                ),
            ),
            cast_to=ArtifactInfoList,
        )


class ArtifactsResourceWithRawResponse:
    def __init__(self, artifacts: ArtifactsResource) -> None:
        self._artifacts = artifacts

        self.retrieve = to_raw_response_wrapper(
            artifacts.retrieve,
        )
        self.list = to_raw_response_wrapper(
            artifacts.list,
        )


class AsyncArtifactsResourceWithRawResponse:
    def __init__(self, artifacts: AsyncArtifactsResource) -> None:
        self._artifacts = artifacts

        self.retrieve = async_to_raw_response_wrapper(
            artifacts.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            artifacts.list,
        )


class ArtifactsResourceWithStreamingResponse:
    def __init__(self, artifacts: ArtifactsResource) -> None:
        self._artifacts = artifacts

        self.retrieve = to_streamed_response_wrapper(
            artifacts.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            artifacts.list,
        )


class AsyncArtifactsResourceWithStreamingResponse:
    def __init__(self, artifacts: AsyncArtifactsResource) -> None:
        self._artifacts = artifacts

        self.retrieve = async_to_streamed_response_wrapper(
            artifacts.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            artifacts.list,
        )
