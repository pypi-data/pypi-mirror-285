# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deeporigin_data import DeeporiginData, AsyncDeeporiginData
from deeporigin_data.types.chat_threads import MessageListResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMessages:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: DeeporiginData) -> None:
        message = client.chat_threads.messages.list(
            thread_id="threadId",
        )
        assert_matches_type(MessageListResponse, message, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: DeeporiginData) -> None:
        response = client.chat_threads.messages.with_raw_response.list(
            thread_id="threadId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(MessageListResponse, message, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: DeeporiginData) -> None:
        with client.chat_threads.messages.with_streaming_response.list(
            thread_id="threadId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = response.parse()
            assert_matches_type(MessageListResponse, message, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncMessages:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_list(self, async_client: AsyncDeeporiginData) -> None:
        message = await async_client.chat_threads.messages.list(
            thread_id="threadId",
        )
        assert_matches_type(MessageListResponse, message, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.chat_threads.messages.with_raw_response.list(
            thread_id="threadId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = await response.parse()
        assert_matches_type(MessageListResponse, message, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.chat_threads.messages.with_streaming_response.list(
            thread_id="threadId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = await response.parse()
            assert_matches_type(MessageListResponse, message, path=["response"])

        assert cast(Any, response.is_closed) is True
