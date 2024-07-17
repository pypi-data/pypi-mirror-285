# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..types import top_level_update_database_column_params
from .._utils import PropertyInfo

__all__ = ["TopLevelUpdateDatabaseColumnParams"]


class TopLevelUpdateDatabaseColumnParams(TypedDict, total=False):
    column: Required[top_level_update_database_column_params.Column]

    column_id: Required[Annotated[str, PropertyInfo(alias="columnId")]]
