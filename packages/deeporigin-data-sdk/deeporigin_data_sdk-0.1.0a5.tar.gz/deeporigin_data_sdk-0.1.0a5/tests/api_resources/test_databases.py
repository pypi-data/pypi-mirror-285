# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deeporigin_data import DeeporiginData, AsyncDeeporiginData
from deeporigin_data.types import (
    DatabaseCreateResponse,
    DatabaseUpdateResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDatabases:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: DeeporiginData) -> None:
        database = client.databases.create(
            database={
                "hid": "hid",
                "name": "name",
                "hid_prefix": "hidPrefix",
            },
        )
        assert_matches_type(DatabaseCreateResponse, database, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: DeeporiginData) -> None:
        database = client.databases.create(
            database={
                "hid": "hid",
                "name": "name",
                "parent_id": "parentId",
                "hid_prefix": "hidPrefix",
                "cols": [{}, {}, {}],
            },
        )
        assert_matches_type(DatabaseCreateResponse, database, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: DeeporiginData) -> None:
        response = client.databases.with_raw_response.create(
            database={
                "hid": "hid",
                "name": "name",
                "hid_prefix": "hidPrefix",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        database = response.parse()
        assert_matches_type(DatabaseCreateResponse, database, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: DeeporiginData) -> None:
        with client.databases.with_streaming_response.create(
            database={
                "hid": "hid",
                "name": "name",
                "hid_prefix": "hidPrefix",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            database = response.parse()
            assert_matches_type(DatabaseCreateResponse, database, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_update(self, client: DeeporiginData) -> None:
        database = client.databases.update(
            id="id",
            database={},
        )
        assert_matches_type(DatabaseUpdateResponse, database, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: DeeporiginData) -> None:
        database = client.databases.update(
            id="id",
            database={
                "hid": "hid",
                "name": "name",
                "parent_id": "parentId",
                "hid_prefix": "hidPrefix",
                "editor": {},
            },
        )
        assert_matches_type(DatabaseUpdateResponse, database, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: DeeporiginData) -> None:
        response = client.databases.with_raw_response.update(
            id="id",
            database={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        database = response.parse()
        assert_matches_type(DatabaseUpdateResponse, database, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: DeeporiginData) -> None:
        with client.databases.with_streaming_response.update(
            id="id",
            database={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            database = response.parse()
            assert_matches_type(DatabaseUpdateResponse, database, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncDatabases:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncDeeporiginData) -> None:
        database = await async_client.databases.create(
            database={
                "hid": "hid",
                "name": "name",
                "hid_prefix": "hidPrefix",
            },
        )
        assert_matches_type(DatabaseCreateResponse, database, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncDeeporiginData) -> None:
        database = await async_client.databases.create(
            database={
                "hid": "hid",
                "name": "name",
                "parent_id": "parentId",
                "hid_prefix": "hidPrefix",
                "cols": [{}, {}, {}],
            },
        )
        assert_matches_type(DatabaseCreateResponse, database, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.databases.with_raw_response.create(
            database={
                "hid": "hid",
                "name": "name",
                "hid_prefix": "hidPrefix",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        database = await response.parse()
        assert_matches_type(DatabaseCreateResponse, database, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.databases.with_streaming_response.create(
            database={
                "hid": "hid",
                "name": "name",
                "hid_prefix": "hidPrefix",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            database = await response.parse()
            assert_matches_type(DatabaseCreateResponse, database, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_update(self, async_client: AsyncDeeporiginData) -> None:
        database = await async_client.databases.update(
            id="id",
            database={},
        )
        assert_matches_type(DatabaseUpdateResponse, database, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncDeeporiginData) -> None:
        database = await async_client.databases.update(
            id="id",
            database={
                "hid": "hid",
                "name": "name",
                "parent_id": "parentId",
                "hid_prefix": "hidPrefix",
                "editor": {},
            },
        )
        assert_matches_type(DatabaseUpdateResponse, database, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.databases.with_raw_response.update(
            id="id",
            database={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        database = await response.parse()
        assert_matches_type(DatabaseUpdateResponse, database, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.databases.with_streaming_response.update(
            id="id",
            database={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            database = await response.parse()
            assert_matches_type(DatabaseUpdateResponse, database, path=["response"])

        assert cast(Any, response.is_closed) is True
