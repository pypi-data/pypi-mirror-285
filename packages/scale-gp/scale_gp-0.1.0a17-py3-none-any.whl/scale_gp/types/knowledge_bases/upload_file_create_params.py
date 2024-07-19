# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, TypedDict

from ..._types import FileTypes

__all__ = ["UploadFileCreateParams"]


class UploadFileCreateParams(TypedDict, total=False):
    chunking_strategy_config: Required[str]

    data_source_config: Required[str]

    files: Required[List[FileTypes]]

    force_reupload: Required[bool]
