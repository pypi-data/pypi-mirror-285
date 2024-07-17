# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deeporigin_data import DeeporiginData, AsyncDeeporiginData
from deeporigin_data.types import (
    ExecuteCodeSyncExecuteResponse,
    ExecuteCodeAsyncExecuteResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestExecuteCode:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_async_execute(self, client: DeeporiginData) -> None:
        execute_code = client.execute_code.async_execute(
            code="code",
            code_language="python",
        )
        assert_matches_type(ExecuteCodeAsyncExecuteResponse, execute_code, path=["response"])

    @parametrize
    def test_raw_response_async_execute(self, client: DeeporiginData) -> None:
        response = client.execute_code.with_raw_response.async_execute(
            code="code",
            code_language="python",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        execute_code = response.parse()
        assert_matches_type(ExecuteCodeAsyncExecuteResponse, execute_code, path=["response"])

    @parametrize
    def test_streaming_response_async_execute(self, client: DeeporiginData) -> None:
        with client.execute_code.with_streaming_response.async_execute(
            code="code",
            code_language="python",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            execute_code = response.parse()
            assert_matches_type(ExecuteCodeAsyncExecuteResponse, execute_code, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_sync_execute(self, client: DeeporiginData) -> None:
        execute_code = client.execute_code.sync_execute(
            code="code",
            code_language="python",
        )
        assert_matches_type(ExecuteCodeSyncExecuteResponse, execute_code, path=["response"])

    @parametrize
    def test_raw_response_sync_execute(self, client: DeeporiginData) -> None:
        response = client.execute_code.with_raw_response.sync_execute(
            code="code",
            code_language="python",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        execute_code = response.parse()
        assert_matches_type(ExecuteCodeSyncExecuteResponse, execute_code, path=["response"])

    @parametrize
    def test_streaming_response_sync_execute(self, client: DeeporiginData) -> None:
        with client.execute_code.with_streaming_response.sync_execute(
            code="code",
            code_language="python",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            execute_code = response.parse()
            assert_matches_type(ExecuteCodeSyncExecuteResponse, execute_code, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncExecuteCode:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_async_execute(self, async_client: AsyncDeeporiginData) -> None:
        execute_code = await async_client.execute_code.async_execute(
            code="code",
            code_language="python",
        )
        assert_matches_type(ExecuteCodeAsyncExecuteResponse, execute_code, path=["response"])

    @parametrize
    async def test_raw_response_async_execute(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.execute_code.with_raw_response.async_execute(
            code="code",
            code_language="python",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        execute_code = await response.parse()
        assert_matches_type(ExecuteCodeAsyncExecuteResponse, execute_code, path=["response"])

    @parametrize
    async def test_streaming_response_async_execute(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.execute_code.with_streaming_response.async_execute(
            code="code",
            code_language="python",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            execute_code = await response.parse()
            assert_matches_type(ExecuteCodeAsyncExecuteResponse, execute_code, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_sync_execute(self, async_client: AsyncDeeporiginData) -> None:
        execute_code = await async_client.execute_code.sync_execute(
            code="code",
            code_language="python",
        )
        assert_matches_type(ExecuteCodeSyncExecuteResponse, execute_code, path=["response"])

    @parametrize
    async def test_raw_response_sync_execute(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.execute_code.with_raw_response.sync_execute(
            code="code",
            code_language="python",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        execute_code = await response.parse()
        assert_matches_type(ExecuteCodeSyncExecuteResponse, execute_code, path=["response"])

    @parametrize
    async def test_streaming_response_sync_execute(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.execute_code.with_streaming_response.sync_execute(
            code="code",
            code_language="python",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            execute_code = await response.parse()
            assert_matches_type(ExecuteCodeSyncExecuteResponse, execute_code, path=["response"])

        assert cast(Any, response.is_closed) is True
