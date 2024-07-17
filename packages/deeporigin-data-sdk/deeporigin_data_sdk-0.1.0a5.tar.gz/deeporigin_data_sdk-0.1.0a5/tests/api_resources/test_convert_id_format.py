# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deeporigin_data import DeeporiginData, AsyncDeeporiginData
from deeporigin_data.types import ConvertIDFormatConvertResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestConvertIDFormat:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_convert(self, client: DeeporiginData) -> None:
        convert_id_format = client.convert_id_format.convert(
            conversions=[{"id": "id"}, {"id": "id"}, {"id": "id"}],
        )
        assert_matches_type(ConvertIDFormatConvertResponse, convert_id_format, path=["response"])

    @parametrize
    def test_raw_response_convert(self, client: DeeporiginData) -> None:
        response = client.convert_id_format.with_raw_response.convert(
            conversions=[{"id": "id"}, {"id": "id"}, {"id": "id"}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        convert_id_format = response.parse()
        assert_matches_type(ConvertIDFormatConvertResponse, convert_id_format, path=["response"])

    @parametrize
    def test_streaming_response_convert(self, client: DeeporiginData) -> None:
        with client.convert_id_format.with_streaming_response.convert(
            conversions=[{"id": "id"}, {"id": "id"}, {"id": "id"}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            convert_id_format = response.parse()
            assert_matches_type(ConvertIDFormatConvertResponse, convert_id_format, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncConvertIDFormat:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_convert(self, async_client: AsyncDeeporiginData) -> None:
        convert_id_format = await async_client.convert_id_format.convert(
            conversions=[{"id": "id"}, {"id": "id"}, {"id": "id"}],
        )
        assert_matches_type(ConvertIDFormatConvertResponse, convert_id_format, path=["response"])

    @parametrize
    async def test_raw_response_convert(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.convert_id_format.with_raw_response.convert(
            conversions=[{"id": "id"}, {"id": "id"}, {"id": "id"}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        convert_id_format = await response.parse()
        assert_matches_type(ConvertIDFormatConvertResponse, convert_id_format, path=["response"])

    @parametrize
    async def test_streaming_response_convert(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.convert_id_format.with_streaming_response.convert(
            conversions=[{"id": "id"}, {"id": "id"}, {"id": "id"}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            convert_id_format = await response.parse()
            assert_matches_type(ConvertIDFormatConvertResponse, convert_id_format, path=["response"])

        assert cast(Any, response.is_closed) is True
