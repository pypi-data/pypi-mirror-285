# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deeporigin_data import DeeporiginData, AsyncDeeporiginData
from deeporigin_data.types import (
    CodeExecutionDescribeResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCodeExecutions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_describe(self, client: DeeporiginData) -> None:
        code_execution = client.code_executions.describe(
            id="id",
        )
        assert_matches_type(CodeExecutionDescribeResponse, code_execution, path=["response"])

    @parametrize
    def test_raw_response_describe(self, client: DeeporiginData) -> None:
        response = client.code_executions.with_raw_response.describe(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        code_execution = response.parse()
        assert_matches_type(CodeExecutionDescribeResponse, code_execution, path=["response"])

    @parametrize
    def test_streaming_response_describe(self, client: DeeporiginData) -> None:
        with client.code_executions.with_streaming_response.describe(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            code_execution = response.parse()
            assert_matches_type(CodeExecutionDescribeResponse, code_execution, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_result(self, client: DeeporiginData) -> None:
        code_execution = client.code_executions.result(
            id="id",
        )
        assert_matches_type(object, code_execution, path=["response"])

    @parametrize
    def test_raw_response_result(self, client: DeeporiginData) -> None:
        response = client.code_executions.with_raw_response.result(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        code_execution = response.parse()
        assert_matches_type(object, code_execution, path=["response"])

    @parametrize
    def test_streaming_response_result(self, client: DeeporiginData) -> None:
        with client.code_executions.with_streaming_response.result(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            code_execution = response.parse()
            assert_matches_type(object, code_execution, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncCodeExecutions:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_describe(self, async_client: AsyncDeeporiginData) -> None:
        code_execution = await async_client.code_executions.describe(
            id="id",
        )
        assert_matches_type(CodeExecutionDescribeResponse, code_execution, path=["response"])

    @parametrize
    async def test_raw_response_describe(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.code_executions.with_raw_response.describe(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        code_execution = await response.parse()
        assert_matches_type(CodeExecutionDescribeResponse, code_execution, path=["response"])

    @parametrize
    async def test_streaming_response_describe(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.code_executions.with_streaming_response.describe(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            code_execution = await response.parse()
            assert_matches_type(CodeExecutionDescribeResponse, code_execution, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_result(self, async_client: AsyncDeeporiginData) -> None:
        code_execution = await async_client.code_executions.result(
            id="id",
        )
        assert_matches_type(object, code_execution, path=["response"])

    @parametrize
    async def test_raw_response_result(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.code_executions.with_raw_response.result(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        code_execution = await response.parse()
        assert_matches_type(object, code_execution, path=["response"])

    @parametrize
    async def test_streaming_response_result(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.code_executions.with_streaming_response.result(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            code_execution = await response.parse()
            assert_matches_type(object, code_execution, path=["response"])

        assert cast(Any, response.is_closed) is True
