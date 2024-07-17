# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import endpoint_create_file_download_url_params
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
from ..types.endpoint_create_file_download_url_response import EndpointCreateFileDownloadURLResponse

__all__ = ["EndpointsResource", "AsyncEndpointsResource"]


class EndpointsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> EndpointsResourceWithRawResponse:
        return EndpointsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EndpointsResourceWithStreamingResponse:
        return EndpointsResourceWithStreamingResponse(self)

    def create_file_download_url(
        self,
        *,
        file_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EndpointCreateFileDownloadURLResponse:
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
            body=maybe_transform(
                {"file_id": file_id}, endpoint_create_file_download_url_params.EndpointCreateFileDownloadURLParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EndpointCreateFileDownloadURLResponse,
        )


class AsyncEndpointsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncEndpointsResourceWithRawResponse:
        return AsyncEndpointsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEndpointsResourceWithStreamingResponse:
        return AsyncEndpointsResourceWithStreamingResponse(self)

    async def create_file_download_url(
        self,
        *,
        file_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EndpointCreateFileDownloadURLResponse:
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
            body=await async_maybe_transform(
                {"file_id": file_id}, endpoint_create_file_download_url_params.EndpointCreateFileDownloadURLParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EndpointCreateFileDownloadURLResponse,
        )


class EndpointsResourceWithRawResponse:
    def __init__(self, endpoints: EndpointsResource) -> None:
        self._endpoints = endpoints

        self.create_file_download_url = to_raw_response_wrapper(
            endpoints.create_file_download_url,
        )


class AsyncEndpointsResourceWithRawResponse:
    def __init__(self, endpoints: AsyncEndpointsResource) -> None:
        self._endpoints = endpoints

        self.create_file_download_url = async_to_raw_response_wrapper(
            endpoints.create_file_download_url,
        )


class EndpointsResourceWithStreamingResponse:
    def __init__(self, endpoints: EndpointsResource) -> None:
        self._endpoints = endpoints

        self.create_file_download_url = to_streamed_response_wrapper(
            endpoints.create_file_download_url,
        )


class AsyncEndpointsResourceWithStreamingResponse:
    def __init__(self, endpoints: AsyncEndpointsResource) -> None:
        self._endpoints = endpoints

        self.create_file_download_url = async_to_streamed_response_wrapper(
            endpoints.create_file_download_url,
        )
