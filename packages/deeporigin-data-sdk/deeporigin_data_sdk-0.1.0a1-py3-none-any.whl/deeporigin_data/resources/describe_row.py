# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import describe_row_describe_params
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
from ..types.describe_row_response import DescribeRowResponse

__all__ = ["DescribeRowResource", "AsyncDescribeRowResource"]


class DescribeRowResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DescribeRowResourceWithRawResponse:
        return DescribeRowResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DescribeRowResourceWithStreamingResponse:
        return DescribeRowResourceWithStreamingResponse(self)

    def describe(
        self,
        *,
        row_id: str,
        column_selection: describe_row_describe_params.ColumnSelection | NotGiven = NOT_GIVEN,
        fields: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DescribeRowResponse:
        """
        Describe a row

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/DescribeRow",
            body=maybe_transform(
                {
                    "row_id": row_id,
                    "column_selection": column_selection,
                    "fields": fields,
                },
                describe_row_describe_params.DescribeRowDescribeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DescribeRowResponse,
        )


class AsyncDescribeRowResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDescribeRowResourceWithRawResponse:
        return AsyncDescribeRowResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDescribeRowResourceWithStreamingResponse:
        return AsyncDescribeRowResourceWithStreamingResponse(self)

    async def describe(
        self,
        *,
        row_id: str,
        column_selection: describe_row_describe_params.ColumnSelection | NotGiven = NOT_GIVEN,
        fields: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DescribeRowResponse:
        """
        Describe a row

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/DescribeRow",
            body=await async_maybe_transform(
                {
                    "row_id": row_id,
                    "column_selection": column_selection,
                    "fields": fields,
                },
                describe_row_describe_params.DescribeRowDescribeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DescribeRowResponse,
        )


class DescribeRowResourceWithRawResponse:
    def __init__(self, describe_row: DescribeRowResource) -> None:
        self._describe_row = describe_row

        self.describe = to_raw_response_wrapper(
            describe_row.describe,
        )


class AsyncDescribeRowResourceWithRawResponse:
    def __init__(self, describe_row: AsyncDescribeRowResource) -> None:
        self._describe_row = describe_row

        self.describe = async_to_raw_response_wrapper(
            describe_row.describe,
        )


class DescribeRowResourceWithStreamingResponse:
    def __init__(self, describe_row: DescribeRowResource) -> None:
        self._describe_row = describe_row

        self.describe = to_streamed_response_wrapper(
            describe_row.describe,
        )


class AsyncDescribeRowResourceWithStreamingResponse:
    def __init__(self, describe_row: AsyncDescribeRowResource) -> None:
        self._describe_row = describe_row

        self.describe = async_to_streamed_response_wrapper(
            describe_row.describe,
        )
