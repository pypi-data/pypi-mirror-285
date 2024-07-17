# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deeporigin_data import DeeporiginData, AsyncDeeporiginData
from deeporigin_data.types import (
    RowListResponse,
    RowDeleteResponse,
    RowEnsureResponse,
    RowImportResponse,
    RowBackReferencesResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRows:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: DeeporiginData) -> None:
        row = client.rows.list(
            filters=[{"parent": {"id": "id"}}, {"parent": {"id": "id"}}, {"parent": {"id": "id"}}],
        )
        assert_matches_type(RowListResponse, row, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: DeeporiginData) -> None:
        response = client.rows.with_raw_response.list(
            filters=[{"parent": {"id": "id"}}, {"parent": {"id": "id"}}, {"parent": {"id": "id"}}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        row = response.parse()
        assert_matches_type(RowListResponse, row, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: DeeporiginData) -> None:
        with client.rows.with_streaming_response.list(
            filters=[{"parent": {"id": "id"}}, {"parent": {"id": "id"}}, {"parent": {"id": "id"}}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            row = response.parse()
            assert_matches_type(RowListResponse, row, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: DeeporiginData) -> None:
        row = client.rows.delete(
            row_ids=["string", "string", "string"],
        )
        assert_matches_type(RowDeleteResponse, row, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: DeeporiginData) -> None:
        response = client.rows.with_raw_response.delete(
            row_ids=["string", "string", "string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        row = response.parse()
        assert_matches_type(RowDeleteResponse, row, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: DeeporiginData) -> None:
        with client.rows.with_streaming_response.delete(
            row_ids=["string", "string", "string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            row = response.parse()
            assert_matches_type(RowDeleteResponse, row, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_back_references(self, client: DeeporiginData) -> None:
        row = client.rows.back_references(
            row_id="rowId",
        )
        assert_matches_type(RowBackReferencesResponse, row, path=["response"])

    @parametrize
    def test_raw_response_back_references(self, client: DeeporiginData) -> None:
        response = client.rows.with_raw_response.back_references(
            row_id="rowId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        row = response.parse()
        assert_matches_type(RowBackReferencesResponse, row, path=["response"])

    @parametrize
    def test_streaming_response_back_references(self, client: DeeporiginData) -> None:
        with client.rows.with_streaming_response.back_references(
            row_id="rowId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            row = response.parse()
            assert_matches_type(RowBackReferencesResponse, row, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_ensure(self, client: DeeporiginData) -> None:
        row = client.rows.ensure(
            database_id="databaseId",
            rows=[{}],
        )
        assert_matches_type(RowEnsureResponse, row, path=["response"])

    @parametrize
    def test_raw_response_ensure(self, client: DeeporiginData) -> None:
        response = client.rows.with_raw_response.ensure(
            database_id="databaseId",
            rows=[{}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        row = response.parse()
        assert_matches_type(RowEnsureResponse, row, path=["response"])

    @parametrize
    def test_streaming_response_ensure(self, client: DeeporiginData) -> None:
        with client.rows.with_streaming_response.ensure(
            database_id="databaseId",
            rows=[{}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            row = response.parse()
            assert_matches_type(RowEnsureResponse, row, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_import(self, client: DeeporiginData) -> None:
        row = client.rows.import_(
            database_id="databaseId",
        )
        assert_matches_type(RowImportResponse, row, path=["response"])

    @parametrize
    def test_raw_response_import(self, client: DeeporiginData) -> None:
        response = client.rows.with_raw_response.import_(
            database_id="databaseId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        row = response.parse()
        assert_matches_type(RowImportResponse, row, path=["response"])

    @parametrize
    def test_streaming_response_import(self, client: DeeporiginData) -> None:
        with client.rows.with_streaming_response.import_(
            database_id="databaseId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            row = response.parse()
            assert_matches_type(RowImportResponse, row, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncRows:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_list(self, async_client: AsyncDeeporiginData) -> None:
        row = await async_client.rows.list(
            filters=[{"parent": {"id": "id"}}, {"parent": {"id": "id"}}, {"parent": {"id": "id"}}],
        )
        assert_matches_type(RowListResponse, row, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.rows.with_raw_response.list(
            filters=[{"parent": {"id": "id"}}, {"parent": {"id": "id"}}, {"parent": {"id": "id"}}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        row = await response.parse()
        assert_matches_type(RowListResponse, row, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.rows.with_streaming_response.list(
            filters=[{"parent": {"id": "id"}}, {"parent": {"id": "id"}}, {"parent": {"id": "id"}}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            row = await response.parse()
            assert_matches_type(RowListResponse, row, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncDeeporiginData) -> None:
        row = await async_client.rows.delete(
            row_ids=["string", "string", "string"],
        )
        assert_matches_type(RowDeleteResponse, row, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.rows.with_raw_response.delete(
            row_ids=["string", "string", "string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        row = await response.parse()
        assert_matches_type(RowDeleteResponse, row, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.rows.with_streaming_response.delete(
            row_ids=["string", "string", "string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            row = await response.parse()
            assert_matches_type(RowDeleteResponse, row, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_back_references(self, async_client: AsyncDeeporiginData) -> None:
        row = await async_client.rows.back_references(
            row_id="rowId",
        )
        assert_matches_type(RowBackReferencesResponse, row, path=["response"])

    @parametrize
    async def test_raw_response_back_references(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.rows.with_raw_response.back_references(
            row_id="rowId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        row = await response.parse()
        assert_matches_type(RowBackReferencesResponse, row, path=["response"])

    @parametrize
    async def test_streaming_response_back_references(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.rows.with_streaming_response.back_references(
            row_id="rowId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            row = await response.parse()
            assert_matches_type(RowBackReferencesResponse, row, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_ensure(self, async_client: AsyncDeeporiginData) -> None:
        row = await async_client.rows.ensure(
            database_id="databaseId",
            rows=[{}],
        )
        assert_matches_type(RowEnsureResponse, row, path=["response"])

    @parametrize
    async def test_raw_response_ensure(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.rows.with_raw_response.ensure(
            database_id="databaseId",
            rows=[{}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        row = await response.parse()
        assert_matches_type(RowEnsureResponse, row, path=["response"])

    @parametrize
    async def test_streaming_response_ensure(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.rows.with_streaming_response.ensure(
            database_id="databaseId",
            rows=[{}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            row = await response.parse()
            assert_matches_type(RowEnsureResponse, row, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_import(self, async_client: AsyncDeeporiginData) -> None:
        row = await async_client.rows.import_(
            database_id="databaseId",
        )
        assert_matches_type(RowImportResponse, row, path=["response"])

    @parametrize
    async def test_raw_response_import(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.rows.with_raw_response.import_(
            database_id="databaseId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        row = await response.parse()
        assert_matches_type(RowImportResponse, row, path=["response"])

    @parametrize
    async def test_streaming_response_import(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.rows.with_streaming_response.import_(
            database_id="databaseId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            row = await response.parse()
            assert_matches_type(RowImportResponse, row, path=["response"])

        assert cast(Any, response.is_closed) is True
