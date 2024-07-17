# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deeporigin_data import DeeporiginData, AsyncDeeporiginData
from deeporigin_data.types import (
    DatabaseColumnAddResponse,
    DatabaseColumnDeleteResponse,
    DatabaseColumnUpdateResponse,
    DatabaseColumnUniqueValuesResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDatabaseColumns:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_update(self, client: DeeporiginData) -> None:
        database_column = client.database_columns.update(
            column={"type": "boolean"},
            column_id="columnId",
        )
        assert_matches_type(DatabaseColumnUpdateResponse, database_column, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: DeeporiginData) -> None:
        database_column = client.database_columns.update(
            column={
                "type": "boolean",
                "name": "name",
                "key": "key",
                "cardinality": "one",
                "systemType": "name",
                "isRequired": True,
                "enabledViewers": ["code", "html", "image"],
                "cellJsonSchema": {},
            },
            column_id="columnId",
        )
        assert_matches_type(DatabaseColumnUpdateResponse, database_column, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: DeeporiginData) -> None:
        response = client.database_columns.with_raw_response.update(
            column={"type": "boolean"},
            column_id="columnId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        database_column = response.parse()
        assert_matches_type(DatabaseColumnUpdateResponse, database_column, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: DeeporiginData) -> None:
        with client.database_columns.with_streaming_response.update(
            column={"type": "boolean"},
            column_id="columnId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            database_column = response.parse()
            assert_matches_type(DatabaseColumnUpdateResponse, database_column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: DeeporiginData) -> None:
        database_column = client.database_columns.delete(
            column_id="columnId",
        )
        assert_matches_type(DatabaseColumnDeleteResponse, database_column, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: DeeporiginData) -> None:
        response = client.database_columns.with_raw_response.delete(
            column_id="columnId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        database_column = response.parse()
        assert_matches_type(DatabaseColumnDeleteResponse, database_column, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: DeeporiginData) -> None:
        with client.database_columns.with_streaming_response.delete(
            column_id="columnId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            database_column = response.parse()
            assert_matches_type(DatabaseColumnDeleteResponse, database_column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_add(self, client: DeeporiginData) -> None:
        database_column = client.database_columns.add(
            column={
                "type": "boolean",
                "name": "name",
                "key": "key",
                "cardinality": "one",
            },
            database_id="databaseId",
        )
        assert_matches_type(DatabaseColumnAddResponse, database_column, path=["response"])

    @parametrize
    def test_method_add_with_all_params(self, client: DeeporiginData) -> None:
        database_column = client.database_columns.add(
            column={
                "type": "boolean",
                "name": "name",
                "key": "key",
                "cardinality": "one",
                "systemType": "name",
                "isRequired": True,
                "enabledViewers": ["code", "html", "image"],
                "cellJsonSchema": {},
            },
            database_id="databaseId",
        )
        assert_matches_type(DatabaseColumnAddResponse, database_column, path=["response"])

    @parametrize
    def test_raw_response_add(self, client: DeeporiginData) -> None:
        response = client.database_columns.with_raw_response.add(
            column={
                "type": "boolean",
                "name": "name",
                "key": "key",
                "cardinality": "one",
            },
            database_id="databaseId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        database_column = response.parse()
        assert_matches_type(DatabaseColumnAddResponse, database_column, path=["response"])

    @parametrize
    def test_streaming_response_add(self, client: DeeporiginData) -> None:
        with client.database_columns.with_streaming_response.add(
            column={
                "type": "boolean",
                "name": "name",
                "key": "key",
                "cardinality": "one",
            },
            database_id="databaseId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            database_column = response.parse()
            assert_matches_type(DatabaseColumnAddResponse, database_column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_unique_values_overload_1(self, client: DeeporiginData) -> None:
        database_column = client.database_columns.unique_values(
            column_id="columnId",
        )
        assert_matches_type(DatabaseColumnUniqueValuesResponse, database_column, path=["response"])

    @parametrize
    def test_raw_response_unique_values_overload_1(self, client: DeeporiginData) -> None:
        response = client.database_columns.with_raw_response.unique_values(
            column_id="columnId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        database_column = response.parse()
        assert_matches_type(DatabaseColumnUniqueValuesResponse, database_column, path=["response"])

    @parametrize
    def test_streaming_response_unique_values_overload_1(self, client: DeeporiginData) -> None:
        with client.database_columns.with_streaming_response.unique_values(
            column_id="columnId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            database_column = response.parse()
            assert_matches_type(DatabaseColumnUniqueValuesResponse, database_column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_unique_values_overload_2(self, client: DeeporiginData) -> None:
        database_column = client.database_columns.unique_values(
            database_row_id="databaseRowId",
            system_column_name="creationParentId",
        )
        assert_matches_type(DatabaseColumnUniqueValuesResponse, database_column, path=["response"])

    @parametrize
    def test_raw_response_unique_values_overload_2(self, client: DeeporiginData) -> None:
        response = client.database_columns.with_raw_response.unique_values(
            database_row_id="databaseRowId",
            system_column_name="creationParentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        database_column = response.parse()
        assert_matches_type(DatabaseColumnUniqueValuesResponse, database_column, path=["response"])

    @parametrize
    def test_streaming_response_unique_values_overload_2(self, client: DeeporiginData) -> None:
        with client.database_columns.with_streaming_response.unique_values(
            database_row_id="databaseRowId",
            system_column_name="creationParentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            database_column = response.parse()
            assert_matches_type(DatabaseColumnUniqueValuesResponse, database_column, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncDatabaseColumns:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_update(self, async_client: AsyncDeeporiginData) -> None:
        database_column = await async_client.database_columns.update(
            column={"type": "boolean"},
            column_id="columnId",
        )
        assert_matches_type(DatabaseColumnUpdateResponse, database_column, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncDeeporiginData) -> None:
        database_column = await async_client.database_columns.update(
            column={
                "type": "boolean",
                "name": "name",
                "key": "key",
                "cardinality": "one",
                "systemType": "name",
                "isRequired": True,
                "enabledViewers": ["code", "html", "image"],
                "cellJsonSchema": {},
            },
            column_id="columnId",
        )
        assert_matches_type(DatabaseColumnUpdateResponse, database_column, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.database_columns.with_raw_response.update(
            column={"type": "boolean"},
            column_id="columnId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        database_column = await response.parse()
        assert_matches_type(DatabaseColumnUpdateResponse, database_column, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.database_columns.with_streaming_response.update(
            column={"type": "boolean"},
            column_id="columnId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            database_column = await response.parse()
            assert_matches_type(DatabaseColumnUpdateResponse, database_column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncDeeporiginData) -> None:
        database_column = await async_client.database_columns.delete(
            column_id="columnId",
        )
        assert_matches_type(DatabaseColumnDeleteResponse, database_column, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.database_columns.with_raw_response.delete(
            column_id="columnId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        database_column = await response.parse()
        assert_matches_type(DatabaseColumnDeleteResponse, database_column, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.database_columns.with_streaming_response.delete(
            column_id="columnId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            database_column = await response.parse()
            assert_matches_type(DatabaseColumnDeleteResponse, database_column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_add(self, async_client: AsyncDeeporiginData) -> None:
        database_column = await async_client.database_columns.add(
            column={
                "type": "boolean",
                "name": "name",
                "key": "key",
                "cardinality": "one",
            },
            database_id="databaseId",
        )
        assert_matches_type(DatabaseColumnAddResponse, database_column, path=["response"])

    @parametrize
    async def test_method_add_with_all_params(self, async_client: AsyncDeeporiginData) -> None:
        database_column = await async_client.database_columns.add(
            column={
                "type": "boolean",
                "name": "name",
                "key": "key",
                "cardinality": "one",
                "systemType": "name",
                "isRequired": True,
                "enabledViewers": ["code", "html", "image"],
                "cellJsonSchema": {},
            },
            database_id="databaseId",
        )
        assert_matches_type(DatabaseColumnAddResponse, database_column, path=["response"])

    @parametrize
    async def test_raw_response_add(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.database_columns.with_raw_response.add(
            column={
                "type": "boolean",
                "name": "name",
                "key": "key",
                "cardinality": "one",
            },
            database_id="databaseId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        database_column = await response.parse()
        assert_matches_type(DatabaseColumnAddResponse, database_column, path=["response"])

    @parametrize
    async def test_streaming_response_add(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.database_columns.with_streaming_response.add(
            column={
                "type": "boolean",
                "name": "name",
                "key": "key",
                "cardinality": "one",
            },
            database_id="databaseId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            database_column = await response.parse()
            assert_matches_type(DatabaseColumnAddResponse, database_column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_unique_values_overload_1(self, async_client: AsyncDeeporiginData) -> None:
        database_column = await async_client.database_columns.unique_values(
            column_id="columnId",
        )
        assert_matches_type(DatabaseColumnUniqueValuesResponse, database_column, path=["response"])

    @parametrize
    async def test_raw_response_unique_values_overload_1(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.database_columns.with_raw_response.unique_values(
            column_id="columnId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        database_column = await response.parse()
        assert_matches_type(DatabaseColumnUniqueValuesResponse, database_column, path=["response"])

    @parametrize
    async def test_streaming_response_unique_values_overload_1(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.database_columns.with_streaming_response.unique_values(
            column_id="columnId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            database_column = await response.parse()
            assert_matches_type(DatabaseColumnUniqueValuesResponse, database_column, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_unique_values_overload_2(self, async_client: AsyncDeeporiginData) -> None:
        database_column = await async_client.database_columns.unique_values(
            database_row_id="databaseRowId",
            system_column_name="creationParentId",
        )
        assert_matches_type(DatabaseColumnUniqueValuesResponse, database_column, path=["response"])

    @parametrize
    async def test_raw_response_unique_values_overload_2(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.database_columns.with_raw_response.unique_values(
            database_row_id="databaseRowId",
            system_column_name="creationParentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        database_column = await response.parse()
        assert_matches_type(DatabaseColumnUniqueValuesResponse, database_column, path=["response"])

    @parametrize
    async def test_streaming_response_unique_values_overload_2(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.database_columns.with_streaming_response.unique_values(
            database_row_id="databaseRowId",
            system_column_name="creationParentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            database_column = await response.parse()
            assert_matches_type(DatabaseColumnUniqueValuesResponse, database_column, path=["response"])

        assert cast(Any, response.is_closed) is True
