# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union
from typing_extensions import Required, TypedDict

__all__ = ["DeploymentCompletionsParams", "ModelRequestParameters"]


class DeploymentCompletionsParams(TypedDict, total=False):
    prompt: Required[str]

    frequency_penalty: float
    """Penalize tokens based on how much they have already appeared in the text.

    Positive values encourage the model to generate new tokens and negative values
    encourage the model to repeat tokens. Available for models provided by LLM
    Engine and OpenAI.
    """

    max_tokens: int
    """The maximum number of tokens to generate in the completion.

    The token count of your prompt plus max_tokens cannot exceed the model's context
    length. If not, specified, max_tokens will be determined based on the model
    used: | Model API family | Model API default | EGP applied default | | --- | ---
    | --- | | OpenAI Completions |
    [`16`](https://platform.openai.com/docs/api-reference/completions/create#max_tokens)
    | `context window - prompt size` | | OpenAI Chat Completions |
    [`context window - prompt size`](https://platform.openai.com/docs/api-reference/chat/create#max_tokens)
    | `context window - prompt size` | | LLM Engine |
    [`max_new_tokens`](https://github.com/scaleapi/launch-python-client/blob/207adced1c88c1c2907266fa9dd1f1ff3ec0ea5b/launch/client.py#L2910)
    parameter is required | `100` | | Anthropic Claude 2 |
    [`max_tokens_to_sample`](https://docs.anthropic.com/claude/reference/complete_post)
    parameter is required | `10000` |
    """

    model_request_parameters: ModelRequestParameters

    presence_penalty: float
    """Penalize tokens based on if they have already appeared in the text.

    Positive values encourage the model to generate new tokens and negative values
    encourage the model to repeat tokens. Available for models provided by LLM
    Engine and OpenAI.
    """

    stop_sequences: List[str]
    """List of up to 4 sequences where the API will stop generating further tokens.

    The returned text will not contain the stop sequence.
    """

    stream: bool
    """Flag indicating whether to stream the completion response"""

    temperature: float
    """What sampling temperature to use, between [0, 2].

    Higher values like 1.8 will make the output more random, while lower values like
    0.2 will make it more focused and deterministic. Setting temperature=0.0 will
    enable fully deterministic (greedy) sampling.NOTE: The temperature parameter
    range for some model is limited to [0, 1] if the given value is above the
    available range, it defaults to the max value.
    """

    top_k: float
    """Sample from the k most likely next tokens at each step.

    Lower k focuses on higher probability tokens. Available for models provided by
    Google and LLM Engine.
    """

    top_p: float
    """The cumulative probability cutoff for token selection.

    Lower values mean sampling from a smaller, more top-weighted nucleus. Available
    for models provided by Google, LLM Engine, and OpenAI.
    """


class ModelRequestParameters(TypedDict, total=False):
    bindings: Required[Dict[str, Union[str, float, bool]]]
