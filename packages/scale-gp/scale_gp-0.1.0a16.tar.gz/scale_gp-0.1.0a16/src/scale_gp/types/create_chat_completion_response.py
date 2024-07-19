# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal, Annotated

from .._utils import PropertyInfo
from .._models import BaseModel

__all__ = [
    "CreateChatCompletionResponse",
    "ChatCompletion",
    "ChatCompletionMessage",
    "ChatCompletionMessageEgpAPIBackendServerAPIModelsEgpModelsUserMessage",
    "ChatCompletionMessageEgpAPIBackendServerAPIModelsEgpModelsAssistantMessage",
    "ChatCompletionMessageEgpAPIBackendServerAPIModelsEgpModelsSystemMessage",
    "TokenUsage",
]


class ChatCompletionMessageEgpAPIBackendServerAPIModelsEgpModelsUserMessage(BaseModel):
    content: str
    """Text input from the user"""

    role: Optional[Literal["user"]] = None
    """The role of the message. Must be set to 'user'.

    A user message is a message from the user to the AI. This should be the message
    used to send end user input to the AI.
    """


class ChatCompletionMessageEgpAPIBackendServerAPIModelsEgpModelsAssistantMessage(BaseModel):
    content: str
    """Text response from the assistant"""

    role: Optional[Literal["assistant"]] = None
    """The role of the message. Must be set to 'assistant'.

    An assistant message is a message from the AI to the client. It is different
    from an agent message in that it cannot contain a tool request. It is simply a
    direct response from the AI to the client.
    """


class ChatCompletionMessageEgpAPIBackendServerAPIModelsEgpModelsSystemMessage(BaseModel):
    content: str
    """Text input from the system."""

    role: Optional[Literal["system"]] = None
    """The role of the message. Must be set to 'system'.

    A system message is different from other messages in that it does not originate
    from a party engaged in a user/AI conversation. Instead, it is a message that is
    injected by either the application or system to guide the conversation. For
    example, a system message may be used as initial instructions for an AI entity
    or to tell the AI that it did not do something correctly.
    """


ChatCompletionMessage = Annotated[
    Union[
        ChatCompletionMessageEgpAPIBackendServerAPIModelsEgpModelsUserMessage,
        ChatCompletionMessageEgpAPIBackendServerAPIModelsEgpModelsAssistantMessage,
        ChatCompletionMessageEgpAPIBackendServerAPIModelsEgpModelsSystemMessage,
    ],
    PropertyInfo(discriminator="role"),
]


class ChatCompletion(BaseModel):
    message: ChatCompletionMessage

    finish_reason: Optional[str] = None


class TokenUsage(BaseModel):
    total: int
    """Total number of tokens in both the prompt and the completion."""

    completion: Optional[int] = None
    """Number of tokens in the completion."""

    prompt: Optional[int] = None
    """Number of tokens in the prompt."""


class CreateChatCompletionResponse(BaseModel):
    chat_completion: ChatCompletion

    token_usage: Optional[TokenUsage] = None
