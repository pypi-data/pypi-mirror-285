# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable

import httpx

from ..types import (
    file_list_params,
    file_upload_params,
    file_archive_params,
    file_describe_params,
    file_download_params,
)
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import (
    maybe_transform,
    async_maybe_transform,
)
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.file_list_response import FileListResponse
from ..types.file_upload_response import FileUploadResponse
from ..types.file_describe_response import FileDescribeResponse
from ..types.file_download_response import FileDownloadResponse

__all__ = ["FilesResource", "AsyncFilesResource"]


class FilesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FilesResourceWithRawResponse:
        return FilesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FilesResourceWithStreamingResponse:
        return FilesResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        filters: Iterable[file_list_params.Filter] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FileListResponse:
        """
        Returns a list of files using the filters.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/ListFiles",
            body=maybe_transform({"filters": filters}, file_list_params.FileListParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FileListResponse,
        )

    def archive(
        self,
        *,
        file_ids: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Archive files by their ids.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/ArchiveFiles",
            body=maybe_transform({"file_ids": file_ids}, file_archive_params.FileArchiveParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def describe(
        self,
        *,
        file_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FileDescribeResponse:
        """
        Describe a file by its ID.

        Args:
          file_id: Deep Origin system ID.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/DescribeFile",
            body=maybe_transform({"file_id": file_id}, file_describe_params.FileDescribeParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FileDescribeResponse,
        )

    def download(
        self,
        *,
        file_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FileDownloadResponse:
        """
        Returns a pre-signed S3 URL.

        Args:
          file_id: Deep Origin system ID.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/CreateFileDownloadUrl",
            body=maybe_transform({"file_id": file_id}, file_download_params.FileDownloadParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FileDownloadResponse,
        )

    def upload(
        self,
        *,
        content_length: str,
        name: str,
        content_type: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FileUploadResponse:
        """Create a file upload URL.

        Typically this is creating a pre-signed S3 URL.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/CreateFileUpload",
            body=maybe_transform(
                {
                    "content_length": content_length,
                    "name": name,
                    "content_type": content_type,
                },
                file_upload_params.FileUploadParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FileUploadResponse,
        )


class AsyncFilesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFilesResourceWithRawResponse:
        return AsyncFilesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFilesResourceWithStreamingResponse:
        return AsyncFilesResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        filters: Iterable[file_list_params.Filter] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FileListResponse:
        """
        Returns a list of files using the filters.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/ListFiles",
            body=await async_maybe_transform({"filters": filters}, file_list_params.FileListParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FileListResponse,
        )

    async def archive(
        self,
        *,
        file_ids: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Archive files by their ids.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/ArchiveFiles",
            body=await async_maybe_transform({"file_ids": file_ids}, file_archive_params.FileArchiveParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def describe(
        self,
        *,
        file_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FileDescribeResponse:
        """
        Describe a file by its ID.

        Args:
          file_id: Deep Origin system ID.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/DescribeFile",
            body=await async_maybe_transform({"file_id": file_id}, file_describe_params.FileDescribeParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FileDescribeResponse,
        )

    async def download(
        self,
        *,
        file_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FileDownloadResponse:
        """
        Returns a pre-signed S3 URL.

        Args:
          file_id: Deep Origin system ID.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/CreateFileDownloadUrl",
            body=await async_maybe_transform({"file_id": file_id}, file_download_params.FileDownloadParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FileDownloadResponse,
        )

    async def upload(
        self,
        *,
        content_length: str,
        name: str,
        content_type: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FileUploadResponse:
        """Create a file upload URL.

        Typically this is creating a pre-signed S3 URL.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/CreateFileUpload",
            body=await async_maybe_transform(
                {
                    "content_length": content_length,
                    "name": name,
                    "content_type": content_type,
                },
                file_upload_params.FileUploadParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FileUploadResponse,
        )


class FilesResourceWithRawResponse:
    def __init__(self, files: FilesResource) -> None:
        self._files = files

        self.list = to_raw_response_wrapper(
            files.list,
        )
        self.archive = to_raw_response_wrapper(
            files.archive,
        )
        self.describe = to_raw_response_wrapper(
            files.describe,
        )
        self.download = to_raw_response_wrapper(
            files.download,
        )
        self.upload = to_raw_response_wrapper(
            files.upload,
        )


class AsyncFilesResourceWithRawResponse:
    def __init__(self, files: AsyncFilesResource) -> None:
        self._files = files

        self.list = async_to_raw_response_wrapper(
            files.list,
        )
        self.archive = async_to_raw_response_wrapper(
            files.archive,
        )
        self.describe = async_to_raw_response_wrapper(
            files.describe,
        )
        self.download = async_to_raw_response_wrapper(
            files.download,
        )
        self.upload = async_to_raw_response_wrapper(
            files.upload,
        )


class FilesResourceWithStreamingResponse:
    def __init__(self, files: FilesResource) -> None:
        self._files = files

        self.list = to_streamed_response_wrapper(
            files.list,
        )
        self.archive = to_streamed_response_wrapper(
            files.archive,
        )
        self.describe = to_streamed_response_wrapper(
            files.describe,
        )
        self.download = to_streamed_response_wrapper(
            files.download,
        )
        self.upload = to_streamed_response_wrapper(
            files.upload,
        )


class AsyncFilesResourceWithStreamingResponse:
    def __init__(self, files: AsyncFilesResource) -> None:
        self._files = files

        self.list = async_to_streamed_response_wrapper(
            files.list,
        )
        self.archive = async_to_streamed_response_wrapper(
            files.archive,
        )
        self.describe = async_to_streamed_response_wrapper(
            files.describe,
        )
        self.download = async_to_streamed_response_wrapper(
            files.download,
        )
        self.upload = async_to_streamed_response_wrapper(
            files.upload,
        )
