# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["TopLevelCreateFileUploadParams"]


class TopLevelCreateFileUploadParams(TypedDict, total=False):
    content_length: Required[Annotated[str, PropertyInfo(alias="contentLength")]]

    name: Required[str]

    content_type: Annotated[str, PropertyInfo(alias="contentType")]
