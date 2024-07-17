# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deeporigin_data import DeeporiginData, AsyncDeeporiginData
from deeporigin_data.types import DatabaseRowListResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDatabaseRows:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: DeeporiginData) -> None:
        database_row = client.database_rows.list(
            database_row_id="databaseRowId",
        )
        assert_matches_type(DatabaseRowListResponse, database_row, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: DeeporiginData) -> None:
        database_row = client.database_rows.list(
            database_row_id="databaseRowId",
            column_selection={
                "include": ["string"],
                "exclude": ["string"],
            },
            creation_block_id="creationBlockId",
            creation_parent_id="creationParentId",
            filter={
                "filter_type": "text",
                "column_id": "columnId",
                "operator": "equals",
                "filter_value": "filterValue",
            },
        )
        assert_matches_type(DatabaseRowListResponse, database_row, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: DeeporiginData) -> None:
        response = client.database_rows.with_raw_response.list(
            database_row_id="databaseRowId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        database_row = response.parse()
        assert_matches_type(DatabaseRowListResponse, database_row, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: DeeporiginData) -> None:
        with client.database_rows.with_streaming_response.list(
            database_row_id="databaseRowId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            database_row = response.parse()
            assert_matches_type(DatabaseRowListResponse, database_row, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncDatabaseRows:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_list(self, async_client: AsyncDeeporiginData) -> None:
        database_row = await async_client.database_rows.list(
            database_row_id="databaseRowId",
        )
        assert_matches_type(DatabaseRowListResponse, database_row, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncDeeporiginData) -> None:
        database_row = await async_client.database_rows.list(
            database_row_id="databaseRowId",
            column_selection={
                "include": ["string"],
                "exclude": ["string"],
            },
            creation_block_id="creationBlockId",
            creation_parent_id="creationParentId",
            filter={
                "filter_type": "text",
                "column_id": "columnId",
                "operator": "equals",
                "filter_value": "filterValue",
            },
        )
        assert_matches_type(DatabaseRowListResponse, database_row, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.database_rows.with_raw_response.list(
            database_row_id="databaseRowId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        database_row = await response.parse()
        assert_matches_type(DatabaseRowListResponse, database_row, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.database_rows.with_streaming_response.list(
            database_row_id="databaseRowId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            database_row = await response.parse()
            assert_matches_type(DatabaseRowListResponse, database_row, path=["response"])

        assert cast(Any, response.is_closed) is True
