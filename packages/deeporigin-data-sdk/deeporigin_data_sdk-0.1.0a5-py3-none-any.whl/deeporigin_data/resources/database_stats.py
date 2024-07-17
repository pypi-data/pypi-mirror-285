# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import database_stat_describe_params
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
from ..types.database_stat_describe_response import DatabaseStatDescribeResponse

__all__ = ["DatabaseStatsResource", "AsyncDatabaseStatsResource"]


class DatabaseStatsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DatabaseStatsResourceWithRawResponse:
        return DatabaseStatsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DatabaseStatsResourceWithStreamingResponse:
        return DatabaseStatsResourceWithStreamingResponse(self)

    def describe(
        self,
        *,
        database_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatabaseStatDescribeResponse:
        """
        Returns aggregation information about a particular database.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/DescribeDatabaseStats",
            body=maybe_transform(
                {"database_id": database_id}, database_stat_describe_params.DatabaseStatDescribeParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatabaseStatDescribeResponse,
        )


class AsyncDatabaseStatsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDatabaseStatsResourceWithRawResponse:
        return AsyncDatabaseStatsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDatabaseStatsResourceWithStreamingResponse:
        return AsyncDatabaseStatsResourceWithStreamingResponse(self)

    async def describe(
        self,
        *,
        database_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatabaseStatDescribeResponse:
        """
        Returns aggregation information about a particular database.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/DescribeDatabaseStats",
            body=await async_maybe_transform(
                {"database_id": database_id}, database_stat_describe_params.DatabaseStatDescribeParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatabaseStatDescribeResponse,
        )


class DatabaseStatsResourceWithRawResponse:
    def __init__(self, database_stats: DatabaseStatsResource) -> None:
        self._database_stats = database_stats

        self.describe = to_raw_response_wrapper(
            database_stats.describe,
        )


class AsyncDatabaseStatsResourceWithRawResponse:
    def __init__(self, database_stats: AsyncDatabaseStatsResource) -> None:
        self._database_stats = database_stats

        self.describe = async_to_raw_response_wrapper(
            database_stats.describe,
        )


class DatabaseStatsResourceWithStreamingResponse:
    def __init__(self, database_stats: DatabaseStatsResource) -> None:
        self._database_stats = database_stats

        self.describe = to_streamed_response_wrapper(
            database_stats.describe,
        )


class AsyncDatabaseStatsResourceWithStreamingResponse:
    def __init__(self, database_stats: AsyncDatabaseStatsResource) -> None:
        self._database_stats = database_stats

        self.describe = async_to_streamed_response_wrapper(
            database_stats.describe,
        )
