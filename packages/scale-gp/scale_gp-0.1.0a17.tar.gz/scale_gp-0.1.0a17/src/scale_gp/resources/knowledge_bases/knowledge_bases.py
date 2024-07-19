# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

import httpx

from .chunks import (
    ChunksResource,
    AsyncChunksResource,
    ChunksResourceWithRawResponse,
    AsyncChunksResourceWithRawResponse,
    ChunksResourceWithStreamingResponse,
    AsyncChunksResourceWithStreamingResponse,
)
from ...types import (
    knowledge_base_list_params,
    knowledge_base_query_params,
    knowledge_base_create_params,
    knowledge_base_retrieve_params,
)
from .uploads import (
    UploadsResource,
    AsyncUploadsResource,
    UploadsResourceWithRawResponse,
    AsyncUploadsResourceWithRawResponse,
    UploadsResourceWithStreamingResponse,
    AsyncUploadsResourceWithStreamingResponse,
)
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import (
    maybe_transform,
    async_maybe_transform,
)
from ..._compat import cached_property
from .artifacts import (
    ArtifactsResource,
    AsyncArtifactsResource,
    ArtifactsResourceWithRawResponse,
    AsyncArtifactsResourceWithRawResponse,
    ArtifactsResourceWithStreamingResponse,
    AsyncArtifactsResourceWithStreamingResponse,
)
from .async_jobs import (
    AsyncJobsResource,
    AsyncAsyncJobsResource,
    AsyncJobsResourceWithRawResponse,
    AsyncAsyncJobsResourceWithRawResponse,
    AsyncJobsResourceWithStreamingResponse,
    AsyncAsyncJobsResourceWithStreamingResponse,
)
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .upload_files import (
    UploadFilesResource,
    AsyncUploadFilesResource,
    UploadFilesResourceWithRawResponse,
    AsyncUploadFilesResourceWithRawResponse,
    UploadFilesResourceWithStreamingResponse,
    AsyncUploadFilesResourceWithStreamingResponse,
)
from ..._base_client import make_request_options
from .upload_schedules import (
    UploadSchedulesResource,
    AsyncUploadSchedulesResource,
    UploadSchedulesResourceWithRawResponse,
    AsyncUploadSchedulesResourceWithRawResponse,
    UploadSchedulesResourceWithStreamingResponse,
    AsyncUploadSchedulesResourceWithStreamingResponse,
)
from .data_source_connections import (
    DataSourceConnectionsResource,
    AsyncDataSourceConnectionsResource,
    DataSourceConnectionsResourceWithRawResponse,
    AsyncDataSourceConnectionsResourceWithRawResponse,
    DataSourceConnectionsResourceWithStreamingResponse,
    AsyncDataSourceConnectionsResourceWithStreamingResponse,
)
from ...types.knowledge_base_item_v2 import KnowledgeBaseItemV2
from ...types.knowledge_base_item_v2_list import KnowledgeBaseItemV2List
from ...types.create_knowledge_base_response import CreateKnowledgeBaseResponse
from ...types.delete_knowledge_base_response_v2 import DeleteKnowledgeBaseResponseV2

__all__ = ["KnowledgeBasesResource", "AsyncKnowledgeBasesResource"]


class KnowledgeBasesResource(SyncAPIResource):
    @cached_property
    def async_jobs(self) -> AsyncJobsResource:
        return AsyncJobsResource(self._client)

    @cached_property
    def chunks(self) -> ChunksResource:
        return ChunksResource(self._client)

    @cached_property
    def data_source_connections(self) -> DataSourceConnectionsResource:
        return DataSourceConnectionsResource(self._client)

    @cached_property
    def uploads(self) -> UploadsResource:
        return UploadsResource(self._client)

    @cached_property
    def artifacts(self) -> ArtifactsResource:
        return ArtifactsResource(self._client)

    @cached_property
    def upload_schedules(self) -> UploadSchedulesResource:
        return UploadSchedulesResource(self._client)

    @cached_property
    def upload_files(self) -> UploadFilesResource:
        return UploadFilesResource(self._client)

    @cached_property
    def with_raw_response(self) -> KnowledgeBasesResourceWithRawResponse:
        return KnowledgeBasesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> KnowledgeBasesResourceWithStreamingResponse:
        return KnowledgeBasesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        embedding_config: knowledge_base_create_params.EmbeddingConfig,
        knowledge_base_name: str,
        account_id: str | NotGiven = NOT_GIVEN,
        metadata: object | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CreateKnowledgeBaseResponse:
        """
        ### Description

        Creates an EGP knowledge base.

        ### Details

        A knowledge base is a storage device for all data that needs to be accessible to
        EGP models. Users can upload data from a variety of data sources into a
        knowledge base, and then query the knowledge base for chunks that are
        semantically relevant to the query.

        Every knowledge base must be associated with a fixed embedding model. This
        embedding model will be used to embed all data that is stored in the knowledge
        base. The embedding model cannot be changed once the knowledge base is created.
        Only the embedding models in the dropdown menu below are supported.

        #### Differences from V1

        - V1 data ingestion consisted of knowledge bases, vector stores, and data
          connectors. V1 Knowledge bases interacted with natural language, V1 vector
          stores interacted with chunks and embeddings, and V1 data connectors set up
          automatic ingestion pipelines with third party data sources.
        - In V2, all data ingestion is done through knowledge bases. Low level
          configuration such as chunking strategies and data sources are now handled by
          this unified knowledge base v2 upload API.
        - The way data is stores in V2 allows for better observability on the ingestion
          progress and content of the knowledge base.
        - Reliability and scalability is also improved via distributed temporal
          workflows.

        #### Backwards Compatibility

        V2 and V1 Knowledge Bases are entirely separate and not backwards compatible.
        Users who have existing V1 knowledge bases will need to migrate their data to V2
        knowledge bases.

        Args:
          embedding_config: The configuration of the embedding

          knowledge_base_name: A unique name for the knowledge base

          account_id: Account to create knowledge base in. If you have access to more than one
              account, you must specify an account_id

          metadata: Metadata associated with the knowledge base

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v4/knowledge-bases",
            body=maybe_transform(
                {
                    "embedding_config": embedding_config,
                    "knowledge_base_name": knowledge_base_name,
                    "account_id": account_id,
                    "metadata": metadata,
                },
                knowledge_base_create_params.KnowledgeBaseCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CreateKnowledgeBaseResponse,
        )

    def retrieve(
        self,
        knowledge_base_id: str,
        *,
        include_artifacts_status: bool | NotGiven = NOT_GIVEN,
        view: List[Literal["Connections", "ArtifactCount"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> KnowledgeBaseItemV2:
        """
        ### Description

        Gets the details of a knowledge base.

        ### Details

        This API can be used to get information about a single knowledge base by ID. To
        use this API, pass in the `knowledge_base_id` that was returned from your
        [Create Knowledge Base API](https://scale-egp.readme.io/reference/create_knowledge_base_v2)
        call as a path parameter.

        This API will return the details of a knowledge base including its ID, name, the
        embedding model it uses, any metadata associated with the knowledge base, and
        the timestamps for its creation, last-updated time.

        #### Backwards Compatibility

        V2 and V1 Knowledge Bases are entirely separate and not backwards compatible.
        Users who have existing V1 knowledge bases will need to migrate their data to V2
        knowledge bases.

        Args:
          include_artifacts_status: Optional query parameter to include a count of artifacts by status

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not knowledge_base_id:
            raise ValueError(f"Expected a non-empty value for `knowledge_base_id` but received {knowledge_base_id!r}")
        return self._get(
            f"/v4/knowledge-bases/{knowledge_base_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "include_artifacts_status": include_artifacts_status,
                        "view": view,
                    },
                    knowledge_base_retrieve_params.KnowledgeBaseRetrieveParams,
                ),
            ),
            cast_to=KnowledgeBaseItemV2,
        )

    def list(
        self,
        *,
        account_id: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        view: List[Literal["Connections", "ArtifactCount"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> KnowledgeBaseItemV2List:
        """
        ### Description

        Lists all knowledge bases owned by the authorized user.

        ### Details

        This API can be used to list all knowledge bases that have been created by the
        user. This API will return the details of all knowledge bases including their
        IDs, names, the embedding models they use, any metadata associated with the
        knowledge bases, and the timestamps for their creation, last-updated time.

        #### Backwards Compatibility

        V2 and V1 Knowledge Bases are entirely separate and not backwards compatible.
        Users who have existing V1 knowledge bases will need to migrate their data to V2
        knowledge bases.

        Args:
          account_id: Optional search by account_id

          limit: Maximum number of artifacts to be returned by the given endpoint. Defaults to
              100 and cannot be greater than 10k.

          page: Page number for pagination to be returned by the given endpoint. Starts at page
              1

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v4/knowledge-bases",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "account_id": account_id,
                        "limit": limit,
                        "page": page,
                        "view": view,
                    },
                    knowledge_base_list_params.KnowledgeBaseListParams,
                ),
            ),
            cast_to=KnowledgeBaseItemV2List,
        )

    def delete(
        self,
        knowledge_base_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeleteKnowledgeBaseResponseV2:
        """
        ### Description

        Deletes a knowledge base.

        ### Details

        This API can be used to delete a knowledge base by ID. To use this API, pass in
        the `knowledge_base_id` that was returned from your
        [Create Knowledge Base API](https://scale-egp.readme.io/reference/create_knowledge_base_v2)
        call as a path parameter.

        #### Backwards Compatibility

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
        return self._delete(
            f"/v4/knowledge-bases/{knowledge_base_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteKnowledgeBaseResponseV2,
        )

    def query(
        self,
        knowledge_base_id: str,
        *,
        query: str,
        top_k: int,
        include_embeddings: bool | NotGiven = NOT_GIVEN,
        metadata_filters: object | NotGiven = NOT_GIVEN,
        verbose: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        ### Description

        Query a knowledge base for text chunks that are most semantically relevant to
        the query.

        ### Details

        Given a query expressed as an embedding, this API runs a similarity search
        amongst the embeddings indexed in the knowledge base to find the most relevant
        chunk embeddings. To use this API, specify the `knowledge_base_id` of the
        knowledge base you want to query, pass in the natural language `query` that you
        want to search for, specify the value `top_k`, which is the number of similar
        chunks that will be returned, and specify whether you want the returned chunks
        to `include_embeddings`.

        Similarity search is used to efficiently find, retrieve, and rank chunks based
        on their similarity to a given query, which is also expressed as an embedding.
        Similarity scores ( using the cosine similarity metric) are calculated between
        each chunk embedding and the embedded query, and the chunks are ranked based on
        similarity score. The top-ranked chunks are returned as the query results.

        We are using the Hierarchical Navigable Small World (HNSW) algorithm to perform
        a k nearest neighbors search in the vector space. This algorithm returns an
        estimate of the best k nearest neighbors and is optimized for datasets with
        hundreds of thousands of vectors. You can read more about the specifics of this
        algorithm
        [here](https://opensearch.org/docs/1.0/search-plugins/knn/approximate-knn/).

        #### Backwards Compatibility

        V2 and V1 Knowledge Bases are entirely separate and not backwards compatible.
        Users who have existing V1 knowledge bases will need to migrate their data to V2
        knowledge bases.

        Args:
          query: The natural language query to be answered by referencing the data ingested into
              the knowledge base

          top_k: Number of chunks to return. Must be greater than 0 if specified. If not
              specified, all chunks will be returned.

          include_embeddings: Whether or not to include the embeddings for each chunk

          metadata_filters: Optional filter by metadata fields, encoded as a JSON object

          verbose: Enable or disable verbose logging

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not knowledge_base_id:
            raise ValueError(f"Expected a non-empty value for `knowledge_base_id` but received {knowledge_base_id!r}")
        return self._post(
            f"/v4/knowledge-bases/{knowledge_base_id}/query",
            body=maybe_transform(
                {
                    "query": query,
                    "top_k": top_k,
                    "include_embeddings": include_embeddings,
                    "metadata_filters": metadata_filters,
                    "verbose": verbose,
                },
                knowledge_base_query_params.KnowledgeBaseQueryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncKnowledgeBasesResource(AsyncAPIResource):
    @cached_property
    def async_jobs(self) -> AsyncAsyncJobsResource:
        return AsyncAsyncJobsResource(self._client)

    @cached_property
    def chunks(self) -> AsyncChunksResource:
        return AsyncChunksResource(self._client)

    @cached_property
    def data_source_connections(self) -> AsyncDataSourceConnectionsResource:
        return AsyncDataSourceConnectionsResource(self._client)

    @cached_property
    def uploads(self) -> AsyncUploadsResource:
        return AsyncUploadsResource(self._client)

    @cached_property
    def artifacts(self) -> AsyncArtifactsResource:
        return AsyncArtifactsResource(self._client)

    @cached_property
    def upload_schedules(self) -> AsyncUploadSchedulesResource:
        return AsyncUploadSchedulesResource(self._client)

    @cached_property
    def upload_files(self) -> AsyncUploadFilesResource:
        return AsyncUploadFilesResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncKnowledgeBasesResourceWithRawResponse:
        return AsyncKnowledgeBasesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncKnowledgeBasesResourceWithStreamingResponse:
        return AsyncKnowledgeBasesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        embedding_config: knowledge_base_create_params.EmbeddingConfig,
        knowledge_base_name: str,
        account_id: str | NotGiven = NOT_GIVEN,
        metadata: object | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CreateKnowledgeBaseResponse:
        """
        ### Description

        Creates an EGP knowledge base.

        ### Details

        A knowledge base is a storage device for all data that needs to be accessible to
        EGP models. Users can upload data from a variety of data sources into a
        knowledge base, and then query the knowledge base for chunks that are
        semantically relevant to the query.

        Every knowledge base must be associated with a fixed embedding model. This
        embedding model will be used to embed all data that is stored in the knowledge
        base. The embedding model cannot be changed once the knowledge base is created.
        Only the embedding models in the dropdown menu below are supported.

        #### Differences from V1

        - V1 data ingestion consisted of knowledge bases, vector stores, and data
          connectors. V1 Knowledge bases interacted with natural language, V1 vector
          stores interacted with chunks and embeddings, and V1 data connectors set up
          automatic ingestion pipelines with third party data sources.
        - In V2, all data ingestion is done through knowledge bases. Low level
          configuration such as chunking strategies and data sources are now handled by
          this unified knowledge base v2 upload API.
        - The way data is stores in V2 allows for better observability on the ingestion
          progress and content of the knowledge base.
        - Reliability and scalability is also improved via distributed temporal
          workflows.

        #### Backwards Compatibility

        V2 and V1 Knowledge Bases are entirely separate and not backwards compatible.
        Users who have existing V1 knowledge bases will need to migrate their data to V2
        knowledge bases.

        Args:
          embedding_config: The configuration of the embedding

          knowledge_base_name: A unique name for the knowledge base

          account_id: Account to create knowledge base in. If you have access to more than one
              account, you must specify an account_id

          metadata: Metadata associated with the knowledge base

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v4/knowledge-bases",
            body=await async_maybe_transform(
                {
                    "embedding_config": embedding_config,
                    "knowledge_base_name": knowledge_base_name,
                    "account_id": account_id,
                    "metadata": metadata,
                },
                knowledge_base_create_params.KnowledgeBaseCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CreateKnowledgeBaseResponse,
        )

    async def retrieve(
        self,
        knowledge_base_id: str,
        *,
        include_artifacts_status: bool | NotGiven = NOT_GIVEN,
        view: List[Literal["Connections", "ArtifactCount"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> KnowledgeBaseItemV2:
        """
        ### Description

        Gets the details of a knowledge base.

        ### Details

        This API can be used to get information about a single knowledge base by ID. To
        use this API, pass in the `knowledge_base_id` that was returned from your
        [Create Knowledge Base API](https://scale-egp.readme.io/reference/create_knowledge_base_v2)
        call as a path parameter.

        This API will return the details of a knowledge base including its ID, name, the
        embedding model it uses, any metadata associated with the knowledge base, and
        the timestamps for its creation, last-updated time.

        #### Backwards Compatibility

        V2 and V1 Knowledge Bases are entirely separate and not backwards compatible.
        Users who have existing V1 knowledge bases will need to migrate their data to V2
        knowledge bases.

        Args:
          include_artifacts_status: Optional query parameter to include a count of artifacts by status

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not knowledge_base_id:
            raise ValueError(f"Expected a non-empty value for `knowledge_base_id` but received {knowledge_base_id!r}")
        return await self._get(
            f"/v4/knowledge-bases/{knowledge_base_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "include_artifacts_status": include_artifacts_status,
                        "view": view,
                    },
                    knowledge_base_retrieve_params.KnowledgeBaseRetrieveParams,
                ),
            ),
            cast_to=KnowledgeBaseItemV2,
        )

    async def list(
        self,
        *,
        account_id: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        view: List[Literal["Connections", "ArtifactCount"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> KnowledgeBaseItemV2List:
        """
        ### Description

        Lists all knowledge bases owned by the authorized user.

        ### Details

        This API can be used to list all knowledge bases that have been created by the
        user. This API will return the details of all knowledge bases including their
        IDs, names, the embedding models they use, any metadata associated with the
        knowledge bases, and the timestamps for their creation, last-updated time.

        #### Backwards Compatibility

        V2 and V1 Knowledge Bases are entirely separate and not backwards compatible.
        Users who have existing V1 knowledge bases will need to migrate their data to V2
        knowledge bases.

        Args:
          account_id: Optional search by account_id

          limit: Maximum number of artifacts to be returned by the given endpoint. Defaults to
              100 and cannot be greater than 10k.

          page: Page number for pagination to be returned by the given endpoint. Starts at page
              1

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v4/knowledge-bases",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "account_id": account_id,
                        "limit": limit,
                        "page": page,
                        "view": view,
                    },
                    knowledge_base_list_params.KnowledgeBaseListParams,
                ),
            ),
            cast_to=KnowledgeBaseItemV2List,
        )

    async def delete(
        self,
        knowledge_base_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeleteKnowledgeBaseResponseV2:
        """
        ### Description

        Deletes a knowledge base.

        ### Details

        This API can be used to delete a knowledge base by ID. To use this API, pass in
        the `knowledge_base_id` that was returned from your
        [Create Knowledge Base API](https://scale-egp.readme.io/reference/create_knowledge_base_v2)
        call as a path parameter.

        #### Backwards Compatibility

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
        return await self._delete(
            f"/v4/knowledge-bases/{knowledge_base_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteKnowledgeBaseResponseV2,
        )

    async def query(
        self,
        knowledge_base_id: str,
        *,
        query: str,
        top_k: int,
        include_embeddings: bool | NotGiven = NOT_GIVEN,
        metadata_filters: object | NotGiven = NOT_GIVEN,
        verbose: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        ### Description

        Query a knowledge base for text chunks that are most semantically relevant to
        the query.

        ### Details

        Given a query expressed as an embedding, this API runs a similarity search
        amongst the embeddings indexed in the knowledge base to find the most relevant
        chunk embeddings. To use this API, specify the `knowledge_base_id` of the
        knowledge base you want to query, pass in the natural language `query` that you
        want to search for, specify the value `top_k`, which is the number of similar
        chunks that will be returned, and specify whether you want the returned chunks
        to `include_embeddings`.

        Similarity search is used to efficiently find, retrieve, and rank chunks based
        on their similarity to a given query, which is also expressed as an embedding.
        Similarity scores ( using the cosine similarity metric) are calculated between
        each chunk embedding and the embedded query, and the chunks are ranked based on
        similarity score. The top-ranked chunks are returned as the query results.

        We are using the Hierarchical Navigable Small World (HNSW) algorithm to perform
        a k nearest neighbors search in the vector space. This algorithm returns an
        estimate of the best k nearest neighbors and is optimized for datasets with
        hundreds of thousands of vectors. You can read more about the specifics of this
        algorithm
        [here](https://opensearch.org/docs/1.0/search-plugins/knn/approximate-knn/).

        #### Backwards Compatibility

        V2 and V1 Knowledge Bases are entirely separate and not backwards compatible.
        Users who have existing V1 knowledge bases will need to migrate their data to V2
        knowledge bases.

        Args:
          query: The natural language query to be answered by referencing the data ingested into
              the knowledge base

          top_k: Number of chunks to return. Must be greater than 0 if specified. If not
              specified, all chunks will be returned.

          include_embeddings: Whether or not to include the embeddings for each chunk

          metadata_filters: Optional filter by metadata fields, encoded as a JSON object

          verbose: Enable or disable verbose logging

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not knowledge_base_id:
            raise ValueError(f"Expected a non-empty value for `knowledge_base_id` but received {knowledge_base_id!r}")
        return await self._post(
            f"/v4/knowledge-bases/{knowledge_base_id}/query",
            body=await async_maybe_transform(
                {
                    "query": query,
                    "top_k": top_k,
                    "include_embeddings": include_embeddings,
                    "metadata_filters": metadata_filters,
                    "verbose": verbose,
                },
                knowledge_base_query_params.KnowledgeBaseQueryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class KnowledgeBasesResourceWithRawResponse:
    def __init__(self, knowledge_bases: KnowledgeBasesResource) -> None:
        self._knowledge_bases = knowledge_bases

        self.create = to_raw_response_wrapper(
            knowledge_bases.create,
        )
        self.retrieve = to_raw_response_wrapper(
            knowledge_bases.retrieve,
        )
        self.list = to_raw_response_wrapper(
            knowledge_bases.list,
        )
        self.delete = to_raw_response_wrapper(
            knowledge_bases.delete,
        )
        self.query = to_raw_response_wrapper(
            knowledge_bases.query,
        )

    @cached_property
    def async_jobs(self) -> AsyncJobsResourceWithRawResponse:
        return AsyncJobsResourceWithRawResponse(self._knowledge_bases.async_jobs)

    @cached_property
    def chunks(self) -> ChunksResourceWithRawResponse:
        return ChunksResourceWithRawResponse(self._knowledge_bases.chunks)

    @cached_property
    def data_source_connections(self) -> DataSourceConnectionsResourceWithRawResponse:
        return DataSourceConnectionsResourceWithRawResponse(self._knowledge_bases.data_source_connections)

    @cached_property
    def uploads(self) -> UploadsResourceWithRawResponse:
        return UploadsResourceWithRawResponse(self._knowledge_bases.uploads)

    @cached_property
    def artifacts(self) -> ArtifactsResourceWithRawResponse:
        return ArtifactsResourceWithRawResponse(self._knowledge_bases.artifacts)

    @cached_property
    def upload_schedules(self) -> UploadSchedulesResourceWithRawResponse:
        return UploadSchedulesResourceWithRawResponse(self._knowledge_bases.upload_schedules)

    @cached_property
    def upload_files(self) -> UploadFilesResourceWithRawResponse:
        return UploadFilesResourceWithRawResponse(self._knowledge_bases.upload_files)


class AsyncKnowledgeBasesResourceWithRawResponse:
    def __init__(self, knowledge_bases: AsyncKnowledgeBasesResource) -> None:
        self._knowledge_bases = knowledge_bases

        self.create = async_to_raw_response_wrapper(
            knowledge_bases.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            knowledge_bases.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            knowledge_bases.list,
        )
        self.delete = async_to_raw_response_wrapper(
            knowledge_bases.delete,
        )
        self.query = async_to_raw_response_wrapper(
            knowledge_bases.query,
        )

    @cached_property
    def async_jobs(self) -> AsyncAsyncJobsResourceWithRawResponse:
        return AsyncAsyncJobsResourceWithRawResponse(self._knowledge_bases.async_jobs)

    @cached_property
    def chunks(self) -> AsyncChunksResourceWithRawResponse:
        return AsyncChunksResourceWithRawResponse(self._knowledge_bases.chunks)

    @cached_property
    def data_source_connections(self) -> AsyncDataSourceConnectionsResourceWithRawResponse:
        return AsyncDataSourceConnectionsResourceWithRawResponse(self._knowledge_bases.data_source_connections)

    @cached_property
    def uploads(self) -> AsyncUploadsResourceWithRawResponse:
        return AsyncUploadsResourceWithRawResponse(self._knowledge_bases.uploads)

    @cached_property
    def artifacts(self) -> AsyncArtifactsResourceWithRawResponse:
        return AsyncArtifactsResourceWithRawResponse(self._knowledge_bases.artifacts)

    @cached_property
    def upload_schedules(self) -> AsyncUploadSchedulesResourceWithRawResponse:
        return AsyncUploadSchedulesResourceWithRawResponse(self._knowledge_bases.upload_schedules)

    @cached_property
    def upload_files(self) -> AsyncUploadFilesResourceWithRawResponse:
        return AsyncUploadFilesResourceWithRawResponse(self._knowledge_bases.upload_files)


class KnowledgeBasesResourceWithStreamingResponse:
    def __init__(self, knowledge_bases: KnowledgeBasesResource) -> None:
        self._knowledge_bases = knowledge_bases

        self.create = to_streamed_response_wrapper(
            knowledge_bases.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            knowledge_bases.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            knowledge_bases.list,
        )
        self.delete = to_streamed_response_wrapper(
            knowledge_bases.delete,
        )
        self.query = to_streamed_response_wrapper(
            knowledge_bases.query,
        )

    @cached_property
    def async_jobs(self) -> AsyncJobsResourceWithStreamingResponse:
        return AsyncJobsResourceWithStreamingResponse(self._knowledge_bases.async_jobs)

    @cached_property
    def chunks(self) -> ChunksResourceWithStreamingResponse:
        return ChunksResourceWithStreamingResponse(self._knowledge_bases.chunks)

    @cached_property
    def data_source_connections(self) -> DataSourceConnectionsResourceWithStreamingResponse:
        return DataSourceConnectionsResourceWithStreamingResponse(self._knowledge_bases.data_source_connections)

    @cached_property
    def uploads(self) -> UploadsResourceWithStreamingResponse:
        return UploadsResourceWithStreamingResponse(self._knowledge_bases.uploads)

    @cached_property
    def artifacts(self) -> ArtifactsResourceWithStreamingResponse:
        return ArtifactsResourceWithStreamingResponse(self._knowledge_bases.artifacts)

    @cached_property
    def upload_schedules(self) -> UploadSchedulesResourceWithStreamingResponse:
        return UploadSchedulesResourceWithStreamingResponse(self._knowledge_bases.upload_schedules)

    @cached_property
    def upload_files(self) -> UploadFilesResourceWithStreamingResponse:
        return UploadFilesResourceWithStreamingResponse(self._knowledge_bases.upload_files)


class AsyncKnowledgeBasesResourceWithStreamingResponse:
    def __init__(self, knowledge_bases: AsyncKnowledgeBasesResource) -> None:
        self._knowledge_bases = knowledge_bases

        self.create = async_to_streamed_response_wrapper(
            knowledge_bases.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            knowledge_bases.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            knowledge_bases.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            knowledge_bases.delete,
        )
        self.query = async_to_streamed_response_wrapper(
            knowledge_bases.query,
        )

    @cached_property
    def async_jobs(self) -> AsyncAsyncJobsResourceWithStreamingResponse:
        return AsyncAsyncJobsResourceWithStreamingResponse(self._knowledge_bases.async_jobs)

    @cached_property
    def chunks(self) -> AsyncChunksResourceWithStreamingResponse:
        return AsyncChunksResourceWithStreamingResponse(self._knowledge_bases.chunks)

    @cached_property
    def data_source_connections(self) -> AsyncDataSourceConnectionsResourceWithStreamingResponse:
        return AsyncDataSourceConnectionsResourceWithStreamingResponse(self._knowledge_bases.data_source_connections)

    @cached_property
    def uploads(self) -> AsyncUploadsResourceWithStreamingResponse:
        return AsyncUploadsResourceWithStreamingResponse(self._knowledge_bases.uploads)

    @cached_property
    def artifacts(self) -> AsyncArtifactsResourceWithStreamingResponse:
        return AsyncArtifactsResourceWithStreamingResponse(self._knowledge_bases.artifacts)

    @cached_property
    def upload_schedules(self) -> AsyncUploadSchedulesResourceWithStreamingResponse:
        return AsyncUploadSchedulesResourceWithStreamingResponse(self._knowledge_bases.upload_schedules)

    @cached_property
    def upload_files(self) -> AsyncUploadFilesResourceWithStreamingResponse:
        return AsyncUploadFilesResourceWithStreamingResponse(self._knowledge_bases.upload_files)
