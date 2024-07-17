# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
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
from ...types.models import (
    deployment_list_params,
    deployment_create_params,
    deployment_update_params,
    deployment_embeddings_params,
    deployment_rerankings_params,
    deployment_completions_params,
    deployment_chat_completions_params,
)
from ...types.shared.delete_response import DeleteResponse
from ...types.models.embedding_response import EmbeddingResponse
from ...types.models.reranking_response import RerankingResponse
from ...types.models.completion_response import CompletionResponse
from ...types.models.model_deployment_response import ModelDeploymentResponse
from ...types.shared.pagination_response_model_deployment import PaginationResponseModelDeployment

__all__ = ["DeploymentsResource", "AsyncDeploymentsResource"]


class DeploymentsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DeploymentsResourceWithRawResponse:
        return DeploymentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DeploymentsResourceWithStreamingResponse:
        return DeploymentsResourceWithStreamingResponse(self)

    def create(
        self,
        model_instance_id: str,
        *,
        name: str,
        account_id: str | NotGiven = NOT_GIVEN,
        deployment_metadata: object | NotGiven = NOT_GIVEN,
        model_creation_parameters: object | NotGiven = NOT_GIVEN,
        vendor_configuration: deployment_create_params.VendorConfiguration | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ModelDeploymentResponse:
        """
        ### Description

        Model Deployments are unique endpoints created for custom models in the Scale
        GenAI Platform. They enable users to interact with and utilize specific
        instances of models through the API/SDK. Each deployment is associated with a
        model instance, containing the necessary model template and model-metadata.
        Model templates describe the creation parameters that are configured on the
        deployment. The model deployments provide a means to call upon models for
        inference, logging calls, and monitoring usage.

        Built-in models also have deployments for creating a consistent interface for
        all models. But they don't represent a real deployment, they are just a way to
        interact with the built-in models. These deployments are created automatically
        when the model is created and they are immutable.

        ### Endpoint details

        This endpoint is used to deploy a model instance. The request payload schema
        depends on the `model_request_parameters_schema` of the Model Template that the
        created model was created from.

        Args:
          account_id: The ID of the account that owns the given entity.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_instance_id:
            raise ValueError(f"Expected a non-empty value for `model_instance_id` but received {model_instance_id!r}")
        return self._post(
            f"/v4/models/{model_instance_id}/deployments",
            body=maybe_transform(
                {
                    "name": name,
                    "account_id": account_id,
                    "deployment_metadata": deployment_metadata,
                    "model_creation_parameters": model_creation_parameters,
                    "vendor_configuration": vendor_configuration,
                },
                deployment_create_params.DeploymentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelDeploymentResponse,
        )

    def retrieve(
        self,
        deployment_id: str,
        *,
        model_instance_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ModelDeploymentResponse:
        """
        ### Description

        Gets the details of a deployment

        ### Details

        This API can be used to get information about a single deployment by ID. To use
        this API, pass in the `id` that was returned from your Create Deployment API
        call as a path parameter.

        Review the response schema to see the fields that will be returned.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_instance_id:
            raise ValueError(f"Expected a non-empty value for `model_instance_id` but received {model_instance_id!r}")
        if not deployment_id:
            raise ValueError(f"Expected a non-empty value for `deployment_id` but received {deployment_id!r}")
        return self._get(
            f"/v4/models/{model_instance_id}/deployments/{deployment_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelDeploymentResponse,
        )

    def update(
        self,
        deployment_id: str,
        *,
        model_instance_id: str,
        deployment_metadata: object | NotGiven = NOT_GIVEN,
        model_creation_parameters: object | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        vendor_configuration: deployment_update_params.VendorConfiguration | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ModelDeploymentResponse:
        """
        ### Description

        Updates a deployment

        ### Details

        This API can be used to update the deployment that matches the ID that was
        passed in as a path parameter. To use this API, pass in the `id` that was
        returned from your Create Deployment API call as a path parameter.

        Review the request schema to see the fields that can be updated.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_instance_id:
            raise ValueError(f"Expected a non-empty value for `model_instance_id` but received {model_instance_id!r}")
        if not deployment_id:
            raise ValueError(f"Expected a non-empty value for `deployment_id` but received {deployment_id!r}")
        return self._patch(
            f"/v4/models/{model_instance_id}/deployments/{deployment_id}",
            body=maybe_transform(
                {
                    "deployment_metadata": deployment_metadata,
                    "model_creation_parameters": model_creation_parameters,
                    "name": name,
                    "vendor_configuration": vendor_configuration,
                },
                deployment_update_params.DeploymentUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelDeploymentResponse,
        )

    def list(
        self,
        model_instance_id: str,
        *,
        account_id: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        sort_by: List[
            Literal[
                "model_creation_parameters:asc",
                "model_creation_parameters:desc",
                "model_endpoint_id:asc",
                "model_endpoint_id:desc",
                "model_instance_id:asc",
                "model_instance_id:desc",
                "vendor_configuration:asc",
                "vendor_configuration:desc",
                "deployment_metadata:asc",
                "deployment_metadata:desc",
                "status:asc",
                "status:desc",
                "id:asc",
                "id:desc",
                "created_at:asc",
                "created_at:desc",
                "account_id:asc",
                "account_id:desc",
                "created_by_user_id:asc",
                "created_by_user_id:desc",
                "created_by_user:asc",
                "created_by_user:desc",
                "name:asc",
                "name:desc",
            ]
        ]
        | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PaginationResponseModelDeployment:
        """
        TODO: Document

        Args:
          account_id: Optional filter by account id

          limit: Maximum number of artifacts to be returned by the given endpoint. Defaults to
              100 and cannot be greater than 10k.

          page: Page number for pagination to be returned by the given endpoint. Starts at page
              1

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_instance_id:
            raise ValueError(f"Expected a non-empty value for `model_instance_id` but received {model_instance_id!r}")
        return self._get(
            f"/v4/models/{model_instance_id}/deployments",
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
                        "sort_by": sort_by,
                    },
                    deployment_list_params.DeploymentListParams,
                ),
            ),
            cast_to=PaginationResponseModelDeployment,
        )

    def delete(
        self,
        deployment_id: str,
        *,
        model_instance_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeleteResponse:
        """
        ### Description

        Deletes a deployment

        ### Details

        This API can be used to delete a deployment by ID. To use this API, pass in the
        `id` that was returned from your Create Deployment API call as a path parameter.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_instance_id:
            raise ValueError(f"Expected a non-empty value for `model_instance_id` but received {model_instance_id!r}")
        if not deployment_id:
            raise ValueError(f"Expected a non-empty value for `deployment_id` but received {deployment_id!r}")
        return self._delete(
            f"/v4/models/{model_instance_id}/deployments/{deployment_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )

    def chat_completions(
        self,
        model_deployment_id: str,
        *,
        chat_history: Iterable[deployment_chat_completions_params.ChatHistory],
        prompt: str,
        frequency_penalty: float | NotGiven = NOT_GIVEN,
        max_tokens: int | NotGiven = NOT_GIVEN,
        model_request_parameters: deployment_chat_completions_params.ModelRequestParameters | NotGiven = NOT_GIVEN,
        presence_penalty: float | NotGiven = NOT_GIVEN,
        stop_sequences: List[str] | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        top_k: float | NotGiven = NOT_GIVEN,
        top_p: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CompletionResponse:
        """
        ### Description

        Interact with the LLM model using the specified model_deployment_id. You can
        include a list of messages as the conversation history. The conversation can
        feature multiple messages from the roles user, assistant, and system. If the
        chosen model does not support chat completion, the API will revert to simple
        completion, disregarding the provided history. The endpoint manages context
        length exceedance optimistically: it estimates the token count from the provided
        history and prompt, and if it exceeds the context or approaches 80% of it, the
        exact token count will be calculated, and the history will be trimmed to fit the
        context.

        ```json
        {
          "prompt": "Generate 5 more",
          "chat_history": [
            {
              "role": "system",
              "content": "You are a name generator. Do not generate anything else than names"
            },
            { "role": "user", "content": "Generate 5 names" },
            {
              "role": "assistant",
              "content": "1. Olivia Bennett\n2. Ethan Carter\n3. Sophia Ramirez\n4. Liam Thompson\n5. Ava Mitchell"
            }
          ]
        }
        ```

        Args:
          chat_history: Chat history entries with roles and messages. If there's no history, pass an
              empty list.

          prompt: New user prompt. This will be sent to the model with a user role.

          frequency_penalty: Penalize tokens based on how much they have already appeared in the text.
              Positive values encourage the model to generate new tokens and negative values
              encourage the model to repeat tokens. Available for models provided by LLM
              Engine and OpenAI.

          max_tokens: The maximum number of tokens to generate in the completion. The token count of
              your prompt plus max_tokens cannot exceed the model's context length. If not,
              specified, max_tokens will be determined based on the model used: | Model API
              family | Model API default | EGP applied default | | --- | --- | --- | | OpenAI
              Completions |
              [`16`](https://platform.openai.com/docs/api-reference/completions/create#max_tokens)
              | `context window - prompt size` | | OpenAI Chat Completions |
              [`context window - prompt size`](https://platform.openai.com/docs/api-reference/chat/create#max_tokens)
              | `context window - prompt size` | | LLM Engine |
              [`max_new_tokens`](https://github.com/scaleapi/launch-python-client/blob/207adced1c88c1c2907266fa9dd1f1ff3ec0ea5b/launch/client.py#L2910)
              parameter is required | `100` | | Anthropic Claude 2 |
              [`max_tokens_to_sample`](https://docs.anthropic.com/claude/reference/complete_post)
              parameter is required | `10000` |

          presence_penalty: Penalize tokens based on if they have already appeared in the text. Positive
              values encourage the model to generate new tokens and negative values encourage
              the model to repeat tokens. Available for models provided by LLM Engine and
              OpenAI.

          stop_sequences: List of up to 4 sequences where the API will stop generating further tokens. The
              returned text will not contain the stop sequence.

          temperature: What sampling temperature to use, between [0, 2]. Higher values like 1.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic. Setting temperature=0.0 will enable fully
              deterministic (greedy) sampling.NOTE: The temperature parameter range for some
              model is limited to [0, 1] if the given value is above the available range, it
              defaults to the max value.

          top_k: Sample from the k most likely next tokens at each step. Lower k focuses on
              higher probability tokens. Available for models provided by Google and LLM
              Engine.

          top_p: The cumulative probability cutoff for token selection. Lower values mean
              sampling from a smaller, more top-weighted nucleus. Available for models
              provided by Google, LLM Engine, and OpenAI.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_deployment_id:
            raise ValueError(
                f"Expected a non-empty value for `model_deployment_id` but received {model_deployment_id!r}"
            )
        return self._post(
            f"/v4/models/{model_deployment_id}/chat-completions",
            body=maybe_transform(
                {
                    "chat_history": chat_history,
                    "prompt": prompt,
                    "frequency_penalty": frequency_penalty,
                    "max_tokens": max_tokens,
                    "model_request_parameters": model_request_parameters,
                    "presence_penalty": presence_penalty,
                    "stop_sequences": stop_sequences,
                    "temperature": temperature,
                    "top_k": top_k,
                    "top_p": top_p,
                },
                deployment_chat_completions_params.DeploymentChatCompletionsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CompletionResponse,
        )

    def completions(
        self,
        model_deployment_id: str,
        *,
        prompt: str,
        frequency_penalty: float | NotGiven = NOT_GIVEN,
        max_tokens: int | NotGiven = NOT_GIVEN,
        model_request_parameters: deployment_completions_params.ModelRequestParameters | NotGiven = NOT_GIVEN,
        presence_penalty: float | NotGiven = NOT_GIVEN,
        stop_sequences: List[str] | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        top_k: float | NotGiven = NOT_GIVEN,
        top_p: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CompletionResponse:
        """
        ### Description

        Interact with the LLM model using the specified model_deployment_id. The LLM
        model will generate a text completion based on the provided prompt.

        ```json
        {
          "prompt": "What is the capital of France?"
        }
        ```

        Args:
          frequency_penalty: Penalize tokens based on how much they have already appeared in the text.
              Positive values encourage the model to generate new tokens and negative values
              encourage the model to repeat tokens. Available for models provided by LLM
              Engine and OpenAI.

          max_tokens: The maximum number of tokens to generate in the completion. The token count of
              your prompt plus max_tokens cannot exceed the model's context length. If not,
              specified, max_tokens will be determined based on the model used: | Model API
              family | Model API default | EGP applied default | | --- | --- | --- | | OpenAI
              Completions |
              [`16`](https://platform.openai.com/docs/api-reference/completions/create#max_tokens)
              | `context window - prompt size` | | OpenAI Chat Completions |
              [`context window - prompt size`](https://platform.openai.com/docs/api-reference/chat/create#max_tokens)
              | `context window - prompt size` | | LLM Engine |
              [`max_new_tokens`](https://github.com/scaleapi/launch-python-client/blob/207adced1c88c1c2907266fa9dd1f1ff3ec0ea5b/launch/client.py#L2910)
              parameter is required | `100` | | Anthropic Claude 2 |
              [`max_tokens_to_sample`](https://docs.anthropic.com/claude/reference/complete_post)
              parameter is required | `10000` |

          presence_penalty: Penalize tokens based on if they have already appeared in the text. Positive
              values encourage the model to generate new tokens and negative values encourage
              the model to repeat tokens. Available for models provided by LLM Engine and
              OpenAI.

          stop_sequences: List of up to 4 sequences where the API will stop generating further tokens. The
              returned text will not contain the stop sequence.

          temperature: What sampling temperature to use, between [0, 2]. Higher values like 1.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic. Setting temperature=0.0 will enable fully
              deterministic (greedy) sampling.NOTE: The temperature parameter range for some
              model is limited to [0, 1] if the given value is above the available range, it
              defaults to the max value.

          top_k: Sample from the k most likely next tokens at each step. Lower k focuses on
              higher probability tokens. Available for models provided by Google and LLM
              Engine.

          top_p: The cumulative probability cutoff for token selection. Lower values mean
              sampling from a smaller, more top-weighted nucleus. Available for models
              provided by Google, LLM Engine, and OpenAI.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_deployment_id:
            raise ValueError(
                f"Expected a non-empty value for `model_deployment_id` but received {model_deployment_id!r}"
            )
        return self._post(
            f"/v4/models/{model_deployment_id}/completions",
            body=maybe_transform(
                {
                    "prompt": prompt,
                    "frequency_penalty": frequency_penalty,
                    "max_tokens": max_tokens,
                    "model_request_parameters": model_request_parameters,
                    "presence_penalty": presence_penalty,
                    "stop_sequences": stop_sequences,
                    "temperature": temperature,
                    "top_k": top_k,
                    "top_p": top_p,
                },
                deployment_completions_params.DeploymentCompletionsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CompletionResponse,
        )

    def embeddings(
        self,
        model_deployment_id: str,
        *,
        texts: List[str],
        model_request_parameters: deployment_embeddings_params.ModelRequestParameters | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EmbeddingResponse:
        """
        ### Description

        Computes the text embeddings for text fragments using the model with the given
        model_deployment_id.

        ### Details

        Users can use this API to execute EMBEDDING type EGP model they have access to.
        To use this API, pass in the `id` of a model returned by the V3 Create Model
        API. An example text embedding request

        ```json
        {
          "texts": ["Please compute my embedding vector", "Another text fragment"]
        }
        ```

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_deployment_id:
            raise ValueError(
                f"Expected a non-empty value for `model_deployment_id` but received {model_deployment_id!r}"
            )
        return self._post(
            f"/v4/models/{model_deployment_id}/embeddings",
            body=maybe_transform(
                {
                    "texts": texts,
                    "model_request_parameters": model_request_parameters,
                },
                deployment_embeddings_params.DeploymentEmbeddingsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EmbeddingResponse,
        )

    def execute(
        self,
        model_deployment_id: str,
        *,
        model_instance_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        ### Description

        Executes a model with the given model_deployment_id.

        ### Details

        Users can use this API to execute any EGP model they have access to. To use this
        API, pass in the `id` of a model returned by the V3 Create Model API. The
        request payload schema depends on the `model_request_parameters_schema` of the
        Model Template that the created model was created from.

        For example, if the model was created from a Model Template with the following
        `model_request_parameters_schema`:

        ```json
        {
          "type": "object",
          "properties": {
            "query": {
              "type": "string"
            }
          }
        }
        ```

        Then the request payload schema would be:

        ```json
        {
          "query": "string"
        }
        ```

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_instance_id:
            raise ValueError(f"Expected a non-empty value for `model_instance_id` but received {model_instance_id!r}")
        if not model_deployment_id:
            raise ValueError(
                f"Expected a non-empty value for `model_deployment_id` but received {model_deployment_id!r}"
            )
        return self._post(
            f"/v4/models/{model_instance_id}/deployments/{model_deployment_id}/execute",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def rerankings(
        self,
        model_deployment_id: str,
        *,
        chunks: List[str],
        query: str,
        model_request_parameters: deployment_rerankings_params.ModelRequestParameters | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RerankingResponse:
        """
        ### Description

        TODO: Documentation

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_deployment_id:
            raise ValueError(
                f"Expected a non-empty value for `model_deployment_id` but received {model_deployment_id!r}"
            )
        return self._post(
            f"/v4/models/{model_deployment_id}/rerankings",
            body=maybe_transform(
                {
                    "chunks": chunks,
                    "query": query,
                    "model_request_parameters": model_request_parameters,
                },
                deployment_rerankings_params.DeploymentRerankingsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RerankingResponse,
        )


class AsyncDeploymentsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDeploymentsResourceWithRawResponse:
        return AsyncDeploymentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDeploymentsResourceWithStreamingResponse:
        return AsyncDeploymentsResourceWithStreamingResponse(self)

    async def create(
        self,
        model_instance_id: str,
        *,
        name: str,
        account_id: str | NotGiven = NOT_GIVEN,
        deployment_metadata: object | NotGiven = NOT_GIVEN,
        model_creation_parameters: object | NotGiven = NOT_GIVEN,
        vendor_configuration: deployment_create_params.VendorConfiguration | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ModelDeploymentResponse:
        """
        ### Description

        Model Deployments are unique endpoints created for custom models in the Scale
        GenAI Platform. They enable users to interact with and utilize specific
        instances of models through the API/SDK. Each deployment is associated with a
        model instance, containing the necessary model template and model-metadata.
        Model templates describe the creation parameters that are configured on the
        deployment. The model deployments provide a means to call upon models for
        inference, logging calls, and monitoring usage.

        Built-in models also have deployments for creating a consistent interface for
        all models. But they don't represent a real deployment, they are just a way to
        interact with the built-in models. These deployments are created automatically
        when the model is created and they are immutable.

        ### Endpoint details

        This endpoint is used to deploy a model instance. The request payload schema
        depends on the `model_request_parameters_schema` of the Model Template that the
        created model was created from.

        Args:
          account_id: The ID of the account that owns the given entity.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_instance_id:
            raise ValueError(f"Expected a non-empty value for `model_instance_id` but received {model_instance_id!r}")
        return await self._post(
            f"/v4/models/{model_instance_id}/deployments",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "account_id": account_id,
                    "deployment_metadata": deployment_metadata,
                    "model_creation_parameters": model_creation_parameters,
                    "vendor_configuration": vendor_configuration,
                },
                deployment_create_params.DeploymentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelDeploymentResponse,
        )

    async def retrieve(
        self,
        deployment_id: str,
        *,
        model_instance_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ModelDeploymentResponse:
        """
        ### Description

        Gets the details of a deployment

        ### Details

        This API can be used to get information about a single deployment by ID. To use
        this API, pass in the `id` that was returned from your Create Deployment API
        call as a path parameter.

        Review the response schema to see the fields that will be returned.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_instance_id:
            raise ValueError(f"Expected a non-empty value for `model_instance_id` but received {model_instance_id!r}")
        if not deployment_id:
            raise ValueError(f"Expected a non-empty value for `deployment_id` but received {deployment_id!r}")
        return await self._get(
            f"/v4/models/{model_instance_id}/deployments/{deployment_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelDeploymentResponse,
        )

    async def update(
        self,
        deployment_id: str,
        *,
        model_instance_id: str,
        deployment_metadata: object | NotGiven = NOT_GIVEN,
        model_creation_parameters: object | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        vendor_configuration: deployment_update_params.VendorConfiguration | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ModelDeploymentResponse:
        """
        ### Description

        Updates a deployment

        ### Details

        This API can be used to update the deployment that matches the ID that was
        passed in as a path parameter. To use this API, pass in the `id` that was
        returned from your Create Deployment API call as a path parameter.

        Review the request schema to see the fields that can be updated.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_instance_id:
            raise ValueError(f"Expected a non-empty value for `model_instance_id` but received {model_instance_id!r}")
        if not deployment_id:
            raise ValueError(f"Expected a non-empty value for `deployment_id` but received {deployment_id!r}")
        return await self._patch(
            f"/v4/models/{model_instance_id}/deployments/{deployment_id}",
            body=await async_maybe_transform(
                {
                    "deployment_metadata": deployment_metadata,
                    "model_creation_parameters": model_creation_parameters,
                    "name": name,
                    "vendor_configuration": vendor_configuration,
                },
                deployment_update_params.DeploymentUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelDeploymentResponse,
        )

    async def list(
        self,
        model_instance_id: str,
        *,
        account_id: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        sort_by: List[
            Literal[
                "model_creation_parameters:asc",
                "model_creation_parameters:desc",
                "model_endpoint_id:asc",
                "model_endpoint_id:desc",
                "model_instance_id:asc",
                "model_instance_id:desc",
                "vendor_configuration:asc",
                "vendor_configuration:desc",
                "deployment_metadata:asc",
                "deployment_metadata:desc",
                "status:asc",
                "status:desc",
                "id:asc",
                "id:desc",
                "created_at:asc",
                "created_at:desc",
                "account_id:asc",
                "account_id:desc",
                "created_by_user_id:asc",
                "created_by_user_id:desc",
                "created_by_user:asc",
                "created_by_user:desc",
                "name:asc",
                "name:desc",
            ]
        ]
        | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PaginationResponseModelDeployment:
        """
        TODO: Document

        Args:
          account_id: Optional filter by account id

          limit: Maximum number of artifacts to be returned by the given endpoint. Defaults to
              100 and cannot be greater than 10k.

          page: Page number for pagination to be returned by the given endpoint. Starts at page
              1

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_instance_id:
            raise ValueError(f"Expected a non-empty value for `model_instance_id` but received {model_instance_id!r}")
        return await self._get(
            f"/v4/models/{model_instance_id}/deployments",
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
                        "sort_by": sort_by,
                    },
                    deployment_list_params.DeploymentListParams,
                ),
            ),
            cast_to=PaginationResponseModelDeployment,
        )

    async def delete(
        self,
        deployment_id: str,
        *,
        model_instance_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeleteResponse:
        """
        ### Description

        Deletes a deployment

        ### Details

        This API can be used to delete a deployment by ID. To use this API, pass in the
        `id` that was returned from your Create Deployment API call as a path parameter.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_instance_id:
            raise ValueError(f"Expected a non-empty value for `model_instance_id` but received {model_instance_id!r}")
        if not deployment_id:
            raise ValueError(f"Expected a non-empty value for `deployment_id` but received {deployment_id!r}")
        return await self._delete(
            f"/v4/models/{model_instance_id}/deployments/{deployment_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )

    async def chat_completions(
        self,
        model_deployment_id: str,
        *,
        chat_history: Iterable[deployment_chat_completions_params.ChatHistory],
        prompt: str,
        frequency_penalty: float | NotGiven = NOT_GIVEN,
        max_tokens: int | NotGiven = NOT_GIVEN,
        model_request_parameters: deployment_chat_completions_params.ModelRequestParameters | NotGiven = NOT_GIVEN,
        presence_penalty: float | NotGiven = NOT_GIVEN,
        stop_sequences: List[str] | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        top_k: float | NotGiven = NOT_GIVEN,
        top_p: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CompletionResponse:
        """
        ### Description

        Interact with the LLM model using the specified model_deployment_id. You can
        include a list of messages as the conversation history. The conversation can
        feature multiple messages from the roles user, assistant, and system. If the
        chosen model does not support chat completion, the API will revert to simple
        completion, disregarding the provided history. The endpoint manages context
        length exceedance optimistically: it estimates the token count from the provided
        history and prompt, and if it exceeds the context or approaches 80% of it, the
        exact token count will be calculated, and the history will be trimmed to fit the
        context.

        ```json
        {
          "prompt": "Generate 5 more",
          "chat_history": [
            {
              "role": "system",
              "content": "You are a name generator. Do not generate anything else than names"
            },
            { "role": "user", "content": "Generate 5 names" },
            {
              "role": "assistant",
              "content": "1. Olivia Bennett\n2. Ethan Carter\n3. Sophia Ramirez\n4. Liam Thompson\n5. Ava Mitchell"
            }
          ]
        }
        ```

        Args:
          chat_history: Chat history entries with roles and messages. If there's no history, pass an
              empty list.

          prompt: New user prompt. This will be sent to the model with a user role.

          frequency_penalty: Penalize tokens based on how much they have already appeared in the text.
              Positive values encourage the model to generate new tokens and negative values
              encourage the model to repeat tokens. Available for models provided by LLM
              Engine and OpenAI.

          max_tokens: The maximum number of tokens to generate in the completion. The token count of
              your prompt plus max_tokens cannot exceed the model's context length. If not,
              specified, max_tokens will be determined based on the model used: | Model API
              family | Model API default | EGP applied default | | --- | --- | --- | | OpenAI
              Completions |
              [`16`](https://platform.openai.com/docs/api-reference/completions/create#max_tokens)
              | `context window - prompt size` | | OpenAI Chat Completions |
              [`context window - prompt size`](https://platform.openai.com/docs/api-reference/chat/create#max_tokens)
              | `context window - prompt size` | | LLM Engine |
              [`max_new_tokens`](https://github.com/scaleapi/launch-python-client/blob/207adced1c88c1c2907266fa9dd1f1ff3ec0ea5b/launch/client.py#L2910)
              parameter is required | `100` | | Anthropic Claude 2 |
              [`max_tokens_to_sample`](https://docs.anthropic.com/claude/reference/complete_post)
              parameter is required | `10000` |

          presence_penalty: Penalize tokens based on if they have already appeared in the text. Positive
              values encourage the model to generate new tokens and negative values encourage
              the model to repeat tokens. Available for models provided by LLM Engine and
              OpenAI.

          stop_sequences: List of up to 4 sequences where the API will stop generating further tokens. The
              returned text will not contain the stop sequence.

          temperature: What sampling temperature to use, between [0, 2]. Higher values like 1.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic. Setting temperature=0.0 will enable fully
              deterministic (greedy) sampling.NOTE: The temperature parameter range for some
              model is limited to [0, 1] if the given value is above the available range, it
              defaults to the max value.

          top_k: Sample from the k most likely next tokens at each step. Lower k focuses on
              higher probability tokens. Available for models provided by Google and LLM
              Engine.

          top_p: The cumulative probability cutoff for token selection. Lower values mean
              sampling from a smaller, more top-weighted nucleus. Available for models
              provided by Google, LLM Engine, and OpenAI.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_deployment_id:
            raise ValueError(
                f"Expected a non-empty value for `model_deployment_id` but received {model_deployment_id!r}"
            )
        return await self._post(
            f"/v4/models/{model_deployment_id}/chat-completions",
            body=await async_maybe_transform(
                {
                    "chat_history": chat_history,
                    "prompt": prompt,
                    "frequency_penalty": frequency_penalty,
                    "max_tokens": max_tokens,
                    "model_request_parameters": model_request_parameters,
                    "presence_penalty": presence_penalty,
                    "stop_sequences": stop_sequences,
                    "temperature": temperature,
                    "top_k": top_k,
                    "top_p": top_p,
                },
                deployment_chat_completions_params.DeploymentChatCompletionsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CompletionResponse,
        )

    async def completions(
        self,
        model_deployment_id: str,
        *,
        prompt: str,
        frequency_penalty: float | NotGiven = NOT_GIVEN,
        max_tokens: int | NotGiven = NOT_GIVEN,
        model_request_parameters: deployment_completions_params.ModelRequestParameters | NotGiven = NOT_GIVEN,
        presence_penalty: float | NotGiven = NOT_GIVEN,
        stop_sequences: List[str] | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        top_k: float | NotGiven = NOT_GIVEN,
        top_p: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CompletionResponse:
        """
        ### Description

        Interact with the LLM model using the specified model_deployment_id. The LLM
        model will generate a text completion based on the provided prompt.

        ```json
        {
          "prompt": "What is the capital of France?"
        }
        ```

        Args:
          frequency_penalty: Penalize tokens based on how much they have already appeared in the text.
              Positive values encourage the model to generate new tokens and negative values
              encourage the model to repeat tokens. Available for models provided by LLM
              Engine and OpenAI.

          max_tokens: The maximum number of tokens to generate in the completion. The token count of
              your prompt plus max_tokens cannot exceed the model's context length. If not,
              specified, max_tokens will be determined based on the model used: | Model API
              family | Model API default | EGP applied default | | --- | --- | --- | | OpenAI
              Completions |
              [`16`](https://platform.openai.com/docs/api-reference/completions/create#max_tokens)
              | `context window - prompt size` | | OpenAI Chat Completions |
              [`context window - prompt size`](https://platform.openai.com/docs/api-reference/chat/create#max_tokens)
              | `context window - prompt size` | | LLM Engine |
              [`max_new_tokens`](https://github.com/scaleapi/launch-python-client/blob/207adced1c88c1c2907266fa9dd1f1ff3ec0ea5b/launch/client.py#L2910)
              parameter is required | `100` | | Anthropic Claude 2 |
              [`max_tokens_to_sample`](https://docs.anthropic.com/claude/reference/complete_post)
              parameter is required | `10000` |

          presence_penalty: Penalize tokens based on if they have already appeared in the text. Positive
              values encourage the model to generate new tokens and negative values encourage
              the model to repeat tokens. Available for models provided by LLM Engine and
              OpenAI.

          stop_sequences: List of up to 4 sequences where the API will stop generating further tokens. The
              returned text will not contain the stop sequence.

          temperature: What sampling temperature to use, between [0, 2]. Higher values like 1.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic. Setting temperature=0.0 will enable fully
              deterministic (greedy) sampling.NOTE: The temperature parameter range for some
              model is limited to [0, 1] if the given value is above the available range, it
              defaults to the max value.

          top_k: Sample from the k most likely next tokens at each step. Lower k focuses on
              higher probability tokens. Available for models provided by Google and LLM
              Engine.

          top_p: The cumulative probability cutoff for token selection. Lower values mean
              sampling from a smaller, more top-weighted nucleus. Available for models
              provided by Google, LLM Engine, and OpenAI.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_deployment_id:
            raise ValueError(
                f"Expected a non-empty value for `model_deployment_id` but received {model_deployment_id!r}"
            )
        return await self._post(
            f"/v4/models/{model_deployment_id}/completions",
            body=await async_maybe_transform(
                {
                    "prompt": prompt,
                    "frequency_penalty": frequency_penalty,
                    "max_tokens": max_tokens,
                    "model_request_parameters": model_request_parameters,
                    "presence_penalty": presence_penalty,
                    "stop_sequences": stop_sequences,
                    "temperature": temperature,
                    "top_k": top_k,
                    "top_p": top_p,
                },
                deployment_completions_params.DeploymentCompletionsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CompletionResponse,
        )

    async def embeddings(
        self,
        model_deployment_id: str,
        *,
        texts: List[str],
        model_request_parameters: deployment_embeddings_params.ModelRequestParameters | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EmbeddingResponse:
        """
        ### Description

        Computes the text embeddings for text fragments using the model with the given
        model_deployment_id.

        ### Details

        Users can use this API to execute EMBEDDING type EGP model they have access to.
        To use this API, pass in the `id` of a model returned by the V3 Create Model
        API. An example text embedding request

        ```json
        {
          "texts": ["Please compute my embedding vector", "Another text fragment"]
        }
        ```

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_deployment_id:
            raise ValueError(
                f"Expected a non-empty value for `model_deployment_id` but received {model_deployment_id!r}"
            )
        return await self._post(
            f"/v4/models/{model_deployment_id}/embeddings",
            body=await async_maybe_transform(
                {
                    "texts": texts,
                    "model_request_parameters": model_request_parameters,
                },
                deployment_embeddings_params.DeploymentEmbeddingsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EmbeddingResponse,
        )

    async def execute(
        self,
        model_deployment_id: str,
        *,
        model_instance_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        ### Description

        Executes a model with the given model_deployment_id.

        ### Details

        Users can use this API to execute any EGP model they have access to. To use this
        API, pass in the `id` of a model returned by the V3 Create Model API. The
        request payload schema depends on the `model_request_parameters_schema` of the
        Model Template that the created model was created from.

        For example, if the model was created from a Model Template with the following
        `model_request_parameters_schema`:

        ```json
        {
          "type": "object",
          "properties": {
            "query": {
              "type": "string"
            }
          }
        }
        ```

        Then the request payload schema would be:

        ```json
        {
          "query": "string"
        }
        ```

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_instance_id:
            raise ValueError(f"Expected a non-empty value for `model_instance_id` but received {model_instance_id!r}")
        if not model_deployment_id:
            raise ValueError(
                f"Expected a non-empty value for `model_deployment_id` but received {model_deployment_id!r}"
            )
        return await self._post(
            f"/v4/models/{model_instance_id}/deployments/{model_deployment_id}/execute",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def rerankings(
        self,
        model_deployment_id: str,
        *,
        chunks: List[str],
        query: str,
        model_request_parameters: deployment_rerankings_params.ModelRequestParameters | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RerankingResponse:
        """
        ### Description

        TODO: Documentation

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_deployment_id:
            raise ValueError(
                f"Expected a non-empty value for `model_deployment_id` but received {model_deployment_id!r}"
            )
        return await self._post(
            f"/v4/models/{model_deployment_id}/rerankings",
            body=await async_maybe_transform(
                {
                    "chunks": chunks,
                    "query": query,
                    "model_request_parameters": model_request_parameters,
                },
                deployment_rerankings_params.DeploymentRerankingsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RerankingResponse,
        )


class DeploymentsResourceWithRawResponse:
    def __init__(self, deployments: DeploymentsResource) -> None:
        self._deployments = deployments

        self.create = to_raw_response_wrapper(
            deployments.create,
        )
        self.retrieve = to_raw_response_wrapper(
            deployments.retrieve,
        )
        self.update = to_raw_response_wrapper(
            deployments.update,
        )
        self.list = to_raw_response_wrapper(
            deployments.list,
        )
        self.delete = to_raw_response_wrapper(
            deployments.delete,
        )
        self.chat_completions = to_raw_response_wrapper(
            deployments.chat_completions,
        )
        self.completions = to_raw_response_wrapper(
            deployments.completions,
        )
        self.embeddings = to_raw_response_wrapper(
            deployments.embeddings,
        )
        self.execute = to_raw_response_wrapper(
            deployments.execute,
        )
        self.rerankings = to_raw_response_wrapper(
            deployments.rerankings,
        )


class AsyncDeploymentsResourceWithRawResponse:
    def __init__(self, deployments: AsyncDeploymentsResource) -> None:
        self._deployments = deployments

        self.create = async_to_raw_response_wrapper(
            deployments.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            deployments.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            deployments.update,
        )
        self.list = async_to_raw_response_wrapper(
            deployments.list,
        )
        self.delete = async_to_raw_response_wrapper(
            deployments.delete,
        )
        self.chat_completions = async_to_raw_response_wrapper(
            deployments.chat_completions,
        )
        self.completions = async_to_raw_response_wrapper(
            deployments.completions,
        )
        self.embeddings = async_to_raw_response_wrapper(
            deployments.embeddings,
        )
        self.execute = async_to_raw_response_wrapper(
            deployments.execute,
        )
        self.rerankings = async_to_raw_response_wrapper(
            deployments.rerankings,
        )


class DeploymentsResourceWithStreamingResponse:
    def __init__(self, deployments: DeploymentsResource) -> None:
        self._deployments = deployments

        self.create = to_streamed_response_wrapper(
            deployments.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            deployments.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            deployments.update,
        )
        self.list = to_streamed_response_wrapper(
            deployments.list,
        )
        self.delete = to_streamed_response_wrapper(
            deployments.delete,
        )
        self.chat_completions = to_streamed_response_wrapper(
            deployments.chat_completions,
        )
        self.completions = to_streamed_response_wrapper(
            deployments.completions,
        )
        self.embeddings = to_streamed_response_wrapper(
            deployments.embeddings,
        )
        self.execute = to_streamed_response_wrapper(
            deployments.execute,
        )
        self.rerankings = to_streamed_response_wrapper(
            deployments.rerankings,
        )


class AsyncDeploymentsResourceWithStreamingResponse:
    def __init__(self, deployments: AsyncDeploymentsResource) -> None:
        self._deployments = deployments

        self.create = async_to_streamed_response_wrapper(
            deployments.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            deployments.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            deployments.update,
        )
        self.list = async_to_streamed_response_wrapper(
            deployments.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            deployments.delete,
        )
        self.chat_completions = async_to_streamed_response_wrapper(
            deployments.chat_completions,
        )
        self.completions = async_to_streamed_response_wrapper(
            deployments.completions,
        )
        self.embeddings = async_to_streamed_response_wrapper(
            deployments.embeddings,
        )
        self.execute = async_to_streamed_response_wrapper(
            deployments.execute,
        )
        self.rerankings = async_to_streamed_response_wrapper(
            deployments.rerankings,
        )
