# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import database_row_list_params
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
from ..types.database_row_list_response import DatabaseRowListResponse

__all__ = ["DatabaseRowsResource", "AsyncDatabaseRowsResource"]


class DatabaseRowsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DatabaseRowsResourceWithRawResponse:
        return DatabaseRowsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DatabaseRowsResourceWithStreamingResponse:
        return DatabaseRowsResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        database_row_id: str,
        column_selection: database_row_list_params.ColumnSelection | NotGiven = NOT_GIVEN,
        creation_block_id: str | NotGiven = NOT_GIVEN,
        creation_parent_id: str | NotGiven = NOT_GIVEN,
        filter: database_row_list_params.Filter | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatabaseRowListResponse:
        """
        List database rows with full row data.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/ListDatabaseRows",
            body=maybe_transform(
                {
                    "database_row_id": database_row_id,
                    "column_selection": column_selection,
                    "creation_block_id": creation_block_id,
                    "creation_parent_id": creation_parent_id,
                    "filter": filter,
                },
                database_row_list_params.DatabaseRowListParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatabaseRowListResponse,
        )


class AsyncDatabaseRowsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDatabaseRowsResourceWithRawResponse:
        return AsyncDatabaseRowsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDatabaseRowsResourceWithStreamingResponse:
        return AsyncDatabaseRowsResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        database_row_id: str,
        column_selection: database_row_list_params.ColumnSelection | NotGiven = NOT_GIVEN,
        creation_block_id: str | NotGiven = NOT_GIVEN,
        creation_parent_id: str | NotGiven = NOT_GIVEN,
        filter: database_row_list_params.Filter | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatabaseRowListResponse:
        """
        List database rows with full row data.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/ListDatabaseRows",
            body=await async_maybe_transform(
                {
                    "database_row_id": database_row_id,
                    "column_selection": column_selection,
                    "creation_block_id": creation_block_id,
                    "creation_parent_id": creation_parent_id,
                    "filter": filter,
                },
                database_row_list_params.DatabaseRowListParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatabaseRowListResponse,
        )


class DatabaseRowsResourceWithRawResponse:
    def __init__(self, database_rows: DatabaseRowsResource) -> None:
        self._database_rows = database_rows

        self.list = to_raw_response_wrapper(
            database_rows.list,
        )


class AsyncDatabaseRowsResourceWithRawResponse:
    def __init__(self, database_rows: AsyncDatabaseRowsResource) -> None:
        self._database_rows = database_rows

        self.list = async_to_raw_response_wrapper(
            database_rows.list,
        )


class DatabaseRowsResourceWithStreamingResponse:
    def __init__(self, database_rows: DatabaseRowsResource) -> None:
        self._database_rows = database_rows

        self.list = to_streamed_response_wrapper(
            database_rows.list,
        )


class AsyncDatabaseRowsResourceWithStreamingResponse:
    def __init__(self, database_rows: AsyncDatabaseRowsResource) -> None:
        self._database_rows = database_rows

        self.list = async_to_streamed_response_wrapper(
            database_rows.list,
        )
