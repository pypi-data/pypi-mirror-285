# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deeporigin_data import DeeporiginData, AsyncDeeporiginData
from deeporigin_data.types import MentionListResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMentions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: DeeporiginData) -> None:
        mention = client.mentions.list(
            query="query",
        )
        assert_matches_type(MentionListResponse, mention, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: DeeporiginData) -> None:
        response = client.mentions.with_raw_response.list(
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        mention = response.parse()
        assert_matches_type(MentionListResponse, mention, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: DeeporiginData) -> None:
        with client.mentions.with_streaming_response.list(
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            mention = response.parse()
            assert_matches_type(MentionListResponse, mention, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncMentions:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_list(self, async_client: AsyncDeeporiginData) -> None:
        mention = await async_client.mentions.list(
            query="query",
        )
        assert_matches_type(MentionListResponse, mention, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.mentions.with_raw_response.list(
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        mention = await response.parse()
        assert_matches_type(MentionListResponse, mention, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.mentions.with_streaming_response.list(
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            mention = await response.parse()
            assert_matches_type(MentionListResponse, mention, path=["response"])

        assert cast(Any, response.is_closed) is True
