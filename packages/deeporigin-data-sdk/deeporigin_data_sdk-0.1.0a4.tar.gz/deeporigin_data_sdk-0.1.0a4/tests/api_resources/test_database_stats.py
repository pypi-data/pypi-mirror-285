# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deeporigin_data import DeeporiginData, AsyncDeeporiginData
from deeporigin_data.types import DatabaseStatDescribeResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDatabaseStats:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_describe(self, client: DeeporiginData) -> None:
        database_stat = client.database_stats.describe(
            database_id="databaseId",
        )
        assert_matches_type(DatabaseStatDescribeResponse, database_stat, path=["response"])

    @parametrize
    def test_raw_response_describe(self, client: DeeporiginData) -> None:
        response = client.database_stats.with_raw_response.describe(
            database_id="databaseId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        database_stat = response.parse()
        assert_matches_type(DatabaseStatDescribeResponse, database_stat, path=["response"])

    @parametrize
    def test_streaming_response_describe(self, client: DeeporiginData) -> None:
        with client.database_stats.with_streaming_response.describe(
            database_id="databaseId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            database_stat = response.parse()
            assert_matches_type(DatabaseStatDescribeResponse, database_stat, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncDatabaseStats:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_describe(self, async_client: AsyncDeeporiginData) -> None:
        database_stat = await async_client.database_stats.describe(
            database_id="databaseId",
        )
        assert_matches_type(DatabaseStatDescribeResponse, database_stat, path=["response"])

    @parametrize
    async def test_raw_response_describe(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.database_stats.with_raw_response.describe(
            database_id="databaseId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        database_stat = await response.parse()
        assert_matches_type(DatabaseStatDescribeResponse, database_stat, path=["response"])

    @parametrize
    async def test_streaming_response_describe(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.database_stats.with_streaming_response.describe(
            database_id="databaseId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            database_stat = await response.parse()
            assert_matches_type(DatabaseStatDescribeResponse, database_stat, path=["response"])

        assert cast(Any, response.is_closed) is True
