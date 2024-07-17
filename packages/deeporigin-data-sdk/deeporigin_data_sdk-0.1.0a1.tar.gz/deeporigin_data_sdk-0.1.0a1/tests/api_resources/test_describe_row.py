# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deeporigin_data import DeeporiginData, AsyncDeeporiginData
from deeporigin_data.types import DescribeRowResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDescribeRow:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_describe(self, client: DeeporiginData) -> None:
        describe_row = client.describe_row.describe(
            row_id="rowId",
        )
        assert_matches_type(DescribeRowResponse, describe_row, path=["response"])

    @parametrize
    def test_method_describe_with_all_params(self, client: DeeporiginData) -> None:
        describe_row = client.describe_row.describe(
            row_id="rowId",
            column_selection={
                "include": ["string"],
                "exclude": ["string"],
            },
            fields=True,
        )
        assert_matches_type(DescribeRowResponse, describe_row, path=["response"])

    @parametrize
    def test_raw_response_describe(self, client: DeeporiginData) -> None:
        response = client.describe_row.with_raw_response.describe(
            row_id="rowId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        describe_row = response.parse()
        assert_matches_type(DescribeRowResponse, describe_row, path=["response"])

    @parametrize
    def test_streaming_response_describe(self, client: DeeporiginData) -> None:
        with client.describe_row.with_streaming_response.describe(
            row_id="rowId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            describe_row = response.parse()
            assert_matches_type(DescribeRowResponse, describe_row, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncDescribeRow:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_describe(self, async_client: AsyncDeeporiginData) -> None:
        describe_row = await async_client.describe_row.describe(
            row_id="rowId",
        )
        assert_matches_type(DescribeRowResponse, describe_row, path=["response"])

    @parametrize
    async def test_method_describe_with_all_params(self, async_client: AsyncDeeporiginData) -> None:
        describe_row = await async_client.describe_row.describe(
            row_id="rowId",
            column_selection={
                "include": ["string"],
                "exclude": ["string"],
            },
            fields=True,
        )
        assert_matches_type(DescribeRowResponse, describe_row, path=["response"])

    @parametrize
    async def test_raw_response_describe(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.describe_row.with_raw_response.describe(
            row_id="rowId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        describe_row = await response.parse()
        assert_matches_type(DescribeRowResponse, describe_row, path=["response"])

    @parametrize
    async def test_streaming_response_describe(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.describe_row.with_streaming_response.describe(
            row_id="rowId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            describe_row = await response.parse()
            assert_matches_type(DescribeRowResponse, describe_row, path=["response"])

        assert cast(Any, response.is_closed) is True
