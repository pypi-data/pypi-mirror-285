# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deeporigin_data import DeeporiginData, AsyncDeeporiginData
from deeporigin_data.types import (
    FileListResponse,
    FileUploadResponse,
    FileDescribeResponse,
    FileDownloadResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFiles:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: DeeporiginData) -> None:
        file = client.files.list()
        assert_matches_type(FileListResponse, file, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: DeeporiginData) -> None:
        file = client.files.list(
            filters=[
                {
                    "assigned_row_ids": ["string", "string", "string"],
                    "is_unassigned": True,
                },
                {
                    "assigned_row_ids": ["string", "string", "string"],
                    "is_unassigned": True,
                },
                {
                    "assigned_row_ids": ["string", "string", "string"],
                    "is_unassigned": True,
                },
            ],
        )
        assert_matches_type(FileListResponse, file, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: DeeporiginData) -> None:
        response = client.files.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(FileListResponse, file, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: DeeporiginData) -> None:
        with client.files.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(FileListResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_archive(self, client: DeeporiginData) -> None:
        file = client.files.archive(
            file_ids=["string", "string", "string"],
        )
        assert_matches_type(object, file, path=["response"])

    @parametrize
    def test_raw_response_archive(self, client: DeeporiginData) -> None:
        response = client.files.with_raw_response.archive(
            file_ids=["string", "string", "string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(object, file, path=["response"])

    @parametrize
    def test_streaming_response_archive(self, client: DeeporiginData) -> None:
        with client.files.with_streaming_response.archive(
            file_ids=["string", "string", "string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(object, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_describe(self, client: DeeporiginData) -> None:
        file = client.files.describe(
            file_id="fileId",
        )
        assert_matches_type(FileDescribeResponse, file, path=["response"])

    @parametrize
    def test_raw_response_describe(self, client: DeeporiginData) -> None:
        response = client.files.with_raw_response.describe(
            file_id="fileId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(FileDescribeResponse, file, path=["response"])

    @parametrize
    def test_streaming_response_describe(self, client: DeeporiginData) -> None:
        with client.files.with_streaming_response.describe(
            file_id="fileId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(FileDescribeResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_download(self, client: DeeporiginData) -> None:
        file = client.files.download(
            file_id="fileId",
        )
        assert_matches_type(FileDownloadResponse, file, path=["response"])

    @parametrize
    def test_raw_response_download(self, client: DeeporiginData) -> None:
        response = client.files.with_raw_response.download(
            file_id="fileId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(FileDownloadResponse, file, path=["response"])

    @parametrize
    def test_streaming_response_download(self, client: DeeporiginData) -> None:
        with client.files.with_streaming_response.download(
            file_id="fileId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(FileDownloadResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_upload(self, client: DeeporiginData) -> None:
        file = client.files.upload(
            content_length="contentLength",
            name="name",
        )
        assert_matches_type(FileUploadResponse, file, path=["response"])

    @parametrize
    def test_method_upload_with_all_params(self, client: DeeporiginData) -> None:
        file = client.files.upload(
            content_length="contentLength",
            name="name",
            content_type="contentType",
        )
        assert_matches_type(FileUploadResponse, file, path=["response"])

    @parametrize
    def test_raw_response_upload(self, client: DeeporiginData) -> None:
        response = client.files.with_raw_response.upload(
            content_length="contentLength",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(FileUploadResponse, file, path=["response"])

    @parametrize
    def test_streaming_response_upload(self, client: DeeporiginData) -> None:
        with client.files.with_streaming_response.upload(
            content_length="contentLength",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(FileUploadResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncFiles:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_list(self, async_client: AsyncDeeporiginData) -> None:
        file = await async_client.files.list()
        assert_matches_type(FileListResponse, file, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncDeeporiginData) -> None:
        file = await async_client.files.list(
            filters=[
                {
                    "assigned_row_ids": ["string", "string", "string"],
                    "is_unassigned": True,
                },
                {
                    "assigned_row_ids": ["string", "string", "string"],
                    "is_unassigned": True,
                },
                {
                    "assigned_row_ids": ["string", "string", "string"],
                    "is_unassigned": True,
                },
            ],
        )
        assert_matches_type(FileListResponse, file, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.files.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert_matches_type(FileListResponse, file, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.files.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(FileListResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_archive(self, async_client: AsyncDeeporiginData) -> None:
        file = await async_client.files.archive(
            file_ids=["string", "string", "string"],
        )
        assert_matches_type(object, file, path=["response"])

    @parametrize
    async def test_raw_response_archive(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.files.with_raw_response.archive(
            file_ids=["string", "string", "string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert_matches_type(object, file, path=["response"])

    @parametrize
    async def test_streaming_response_archive(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.files.with_streaming_response.archive(
            file_ids=["string", "string", "string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(object, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_describe(self, async_client: AsyncDeeporiginData) -> None:
        file = await async_client.files.describe(
            file_id="fileId",
        )
        assert_matches_type(FileDescribeResponse, file, path=["response"])

    @parametrize
    async def test_raw_response_describe(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.files.with_raw_response.describe(
            file_id="fileId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert_matches_type(FileDescribeResponse, file, path=["response"])

    @parametrize
    async def test_streaming_response_describe(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.files.with_streaming_response.describe(
            file_id="fileId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(FileDescribeResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_download(self, async_client: AsyncDeeporiginData) -> None:
        file = await async_client.files.download(
            file_id="fileId",
        )
        assert_matches_type(FileDownloadResponse, file, path=["response"])

    @parametrize
    async def test_raw_response_download(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.files.with_raw_response.download(
            file_id="fileId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert_matches_type(FileDownloadResponse, file, path=["response"])

    @parametrize
    async def test_streaming_response_download(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.files.with_streaming_response.download(
            file_id="fileId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(FileDownloadResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_upload(self, async_client: AsyncDeeporiginData) -> None:
        file = await async_client.files.upload(
            content_length="contentLength",
            name="name",
        )
        assert_matches_type(FileUploadResponse, file, path=["response"])

    @parametrize
    async def test_method_upload_with_all_params(self, async_client: AsyncDeeporiginData) -> None:
        file = await async_client.files.upload(
            content_length="contentLength",
            name="name",
            content_type="contentType",
        )
        assert_matches_type(FileUploadResponse, file, path=["response"])

    @parametrize
    async def test_raw_response_upload(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.files.with_raw_response.upload(
            content_length="contentLength",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert_matches_type(FileUploadResponse, file, path=["response"])

    @parametrize
    async def test_streaming_response_upload(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.files.with_streaming_response.upload(
            content_length="contentLength",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(FileUploadResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True
