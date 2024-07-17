# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deeporigin_data import DeeporiginData, AsyncDeeporiginData
from deeporigin_data.types import EndpointCreateFileDownloadURLResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEndpoints:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create_file_download_url(self, client: DeeporiginData) -> None:
        endpoint = client.endpoints.create_file_download_url(
            file_id="fileId",
        )
        assert_matches_type(EndpointCreateFileDownloadURLResponse, endpoint, path=["response"])

    @parametrize
    def test_raw_response_create_file_download_url(self, client: DeeporiginData) -> None:
        response = client.endpoints.with_raw_response.create_file_download_url(
            file_id="fileId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = response.parse()
        assert_matches_type(EndpointCreateFileDownloadURLResponse, endpoint, path=["response"])

    @parametrize
    def test_streaming_response_create_file_download_url(self, client: DeeporiginData) -> None:
        with client.endpoints.with_streaming_response.create_file_download_url(
            file_id="fileId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = response.parse()
            assert_matches_type(EndpointCreateFileDownloadURLResponse, endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncEndpoints:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create_file_download_url(self, async_client: AsyncDeeporiginData) -> None:
        endpoint = await async_client.endpoints.create_file_download_url(
            file_id="fileId",
        )
        assert_matches_type(EndpointCreateFileDownloadURLResponse, endpoint, path=["response"])

    @parametrize
    async def test_raw_response_create_file_download_url(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.endpoints.with_raw_response.create_file_download_url(
            file_id="fileId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = await response.parse()
        assert_matches_type(EndpointCreateFileDownloadURLResponse, endpoint, path=["response"])

    @parametrize
    async def test_streaming_response_create_file_download_url(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.endpoints.with_streaming_response.create_file_download_url(
            file_id="fileId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = await response.parse()
            assert_matches_type(EndpointCreateFileDownloadURLResponse, endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True
