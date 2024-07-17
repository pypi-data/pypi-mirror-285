# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deeporigin_data import DeeporiginData, AsyncDeeporiginData
from deeporigin_data.types import BaseSequenceParseResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestBaseSequences:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_parse(self, client: DeeporiginData) -> None:
        base_sequence = client.base_sequences.parse(
            file_id="fileId",
        )
        assert_matches_type(BaseSequenceParseResponse, base_sequence, path=["response"])

    @parametrize
    def test_raw_response_parse(self, client: DeeporiginData) -> None:
        response = client.base_sequences.with_raw_response.parse(
            file_id="fileId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        base_sequence = response.parse()
        assert_matches_type(BaseSequenceParseResponse, base_sequence, path=["response"])

    @parametrize
    def test_streaming_response_parse(self, client: DeeporiginData) -> None:
        with client.base_sequences.with_streaming_response.parse(
            file_id="fileId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            base_sequence = response.parse()
            assert_matches_type(BaseSequenceParseResponse, base_sequence, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncBaseSequences:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_parse(self, async_client: AsyncDeeporiginData) -> None:
        base_sequence = await async_client.base_sequences.parse(
            file_id="fileId",
        )
        assert_matches_type(BaseSequenceParseResponse, base_sequence, path=["response"])

    @parametrize
    async def test_raw_response_parse(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.base_sequences.with_raw_response.parse(
            file_id="fileId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        base_sequence = await response.parse()
        assert_matches_type(BaseSequenceParseResponse, base_sequence, path=["response"])

    @parametrize
    async def test_streaming_response_parse(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.base_sequences.with_streaming_response.parse(
            file_id="fileId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            base_sequence = await response.parse()
            assert_matches_type(BaseSequenceParseResponse, base_sequence, path=["response"])

        assert cast(Any, response.is_closed) is True
