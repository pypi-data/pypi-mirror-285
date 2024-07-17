# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["CompletionResponse"]


class CompletionResponse(BaseModel):
    completions: List[List[object]]

    finish_reason: Optional[str] = None

    prompt_tokens: Optional[int] = None

    response_tokens: Optional[int] = None
