# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..types import database_column_update_params
from .._utils import PropertyInfo

__all__ = ["DatabaseColumnUpdateParams"]


class DatabaseColumnUpdateParams(TypedDict, total=False):
    column: Required[database_column_update_params.Column]

    column_id: Required[Annotated[str, PropertyInfo(alias="columnId")]]
