# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deeporigin_data import DeeporiginData, AsyncDeeporiginData
from deeporigin_data.types import ChatThreadCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestChatThreads:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: DeeporiginData) -> None:
        chat_thread = client.chat_threads.create(
            body={},
        )
        assert_matches_type(ChatThreadCreateResponse, chat_thread, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: DeeporiginData) -> None:
        response = client.chat_threads.with_raw_response.create(
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chat_thread = response.parse()
        assert_matches_type(ChatThreadCreateResponse, chat_thread, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: DeeporiginData) -> None:
        with client.chat_threads.with_streaming_response.create(
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chat_thread = response.parse()
            assert_matches_type(ChatThreadCreateResponse, chat_thread, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncChatThreads:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncDeeporiginData) -> None:
        chat_thread = await async_client.chat_threads.create(
            body={},
        )
        assert_matches_type(ChatThreadCreateResponse, chat_thread, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.chat_threads.with_raw_response.create(
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chat_thread = await response.parse()
        assert_matches_type(ChatThreadCreateResponse, chat_thread, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.chat_threads.with_streaming_response.create(
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chat_thread = await response.parse()
            assert_matches_type(ChatThreadCreateResponse, chat_thread, path=["response"])

        assert cast(Any, response.is_closed) is True
