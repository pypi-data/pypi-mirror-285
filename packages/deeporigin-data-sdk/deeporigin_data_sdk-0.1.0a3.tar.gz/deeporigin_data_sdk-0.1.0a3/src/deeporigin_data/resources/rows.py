# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable

import httpx

from ..types import (
    row_list_params,
    row_delete_params,
    row_ensure_params,
    row_import_params,
    row_back_references_params,
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
from ..types.row_list_response import RowListResponse
from ..types.row_delete_response import RowDeleteResponse
from ..types.row_ensure_response import RowEnsureResponse
from ..types.row_import_response import RowImportResponse
from ..types.row_back_references_response import RowBackReferencesResponse

__all__ = ["RowsResource", "AsyncRowsResource"]


class RowsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RowsResourceWithRawResponse:
        return RowsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RowsResourceWithStreamingResponse:
        return RowsResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        filters: Iterable[row_list_params.Filter],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RowListResponse:
        """
        Lists rows at a given depth in the hierarchy.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/ListRows",
            body=maybe_transform({"filters": filters}, row_list_params.RowListParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RowListResponse,
        )

    def delete(
        self,
        *,
        row_ids: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RowDeleteResponse:
        """
        Delete rows by their ids.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/DeleteRows",
            body=maybe_transform({"row_ids": row_ids}, row_delete_params.RowDeleteParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RowDeleteResponse,
        )

    def back_references(
        self,
        *,
        row_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RowBackReferencesResponse:
        """
        Finds all the places a row is referenced.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/ListRowBackReferences",
            body=maybe_transform({"row_id": row_id}, row_back_references_params.RowBackReferencesParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RowBackReferencesResponse,
        )

    def ensure(
        self,
        *,
        database_id: str,
        rows: Iterable[row_ensure_params.Row],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RowEnsureResponse:
        """Either creates or updates an existing row.

        Supports updates to both system and
        user defined columns.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/EnsureRows",
            body=maybe_transform(
                {
                    "database_id": database_id,
                    "rows": rows,
                },
                row_ensure_params.RowEnsureParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RowEnsureResponse,
        )

    def import_(
        self,
        *,
        database_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RowImportResponse:
        """
        Creates new rows from CSV data.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/ImportRows",
            body=maybe_transform({"database_id": database_id}, row_import_params.RowImportParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RowImportResponse,
        )


class AsyncRowsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRowsResourceWithRawResponse:
        return AsyncRowsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRowsResourceWithStreamingResponse:
        return AsyncRowsResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        filters: Iterable[row_list_params.Filter],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RowListResponse:
        """
        Lists rows at a given depth in the hierarchy.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/ListRows",
            body=await async_maybe_transform({"filters": filters}, row_list_params.RowListParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RowListResponse,
        )

    async def delete(
        self,
        *,
        row_ids: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RowDeleteResponse:
        """
        Delete rows by their ids.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/DeleteRows",
            body=await async_maybe_transform({"row_ids": row_ids}, row_delete_params.RowDeleteParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RowDeleteResponse,
        )

    async def back_references(
        self,
        *,
        row_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RowBackReferencesResponse:
        """
        Finds all the places a row is referenced.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/ListRowBackReferences",
            body=await async_maybe_transform({"row_id": row_id}, row_back_references_params.RowBackReferencesParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RowBackReferencesResponse,
        )

    async def ensure(
        self,
        *,
        database_id: str,
        rows: Iterable[row_ensure_params.Row],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RowEnsureResponse:
        """Either creates or updates an existing row.

        Supports updates to both system and
        user defined columns.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/EnsureRows",
            body=await async_maybe_transform(
                {
                    "database_id": database_id,
                    "rows": rows,
                },
                row_ensure_params.RowEnsureParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RowEnsureResponse,
        )

    async def import_(
        self,
        *,
        database_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RowImportResponse:
        """
        Creates new rows from CSV data.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/ImportRows",
            body=await async_maybe_transform({"database_id": database_id}, row_import_params.RowImportParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RowImportResponse,
        )


class RowsResourceWithRawResponse:
    def __init__(self, rows: RowsResource) -> None:
        self._rows = rows

        self.list = to_raw_response_wrapper(
            rows.list,
        )
        self.delete = to_raw_response_wrapper(
            rows.delete,
        )
        self.back_references = to_raw_response_wrapper(
            rows.back_references,
        )
        self.ensure = to_raw_response_wrapper(
            rows.ensure,
        )
        self.import_ = to_raw_response_wrapper(
            rows.import_,
        )


class AsyncRowsResourceWithRawResponse:
    def __init__(self, rows: AsyncRowsResource) -> None:
        self._rows = rows

        self.list = async_to_raw_response_wrapper(
            rows.list,
        )
        self.delete = async_to_raw_response_wrapper(
            rows.delete,
        )
        self.back_references = async_to_raw_response_wrapper(
            rows.back_references,
        )
        self.ensure = async_to_raw_response_wrapper(
            rows.ensure,
        )
        self.import_ = async_to_raw_response_wrapper(
            rows.import_,
        )


class RowsResourceWithStreamingResponse:
    def __init__(self, rows: RowsResource) -> None:
        self._rows = rows

        self.list = to_streamed_response_wrapper(
            rows.list,
        )
        self.delete = to_streamed_response_wrapper(
            rows.delete,
        )
        self.back_references = to_streamed_response_wrapper(
            rows.back_references,
        )
        self.ensure = to_streamed_response_wrapper(
            rows.ensure,
        )
        self.import_ = to_streamed_response_wrapper(
            rows.import_,
        )


class AsyncRowsResourceWithStreamingResponse:
    def __init__(self, rows: AsyncRowsResource) -> None:
        self._rows = rows

        self.list = async_to_streamed_response_wrapper(
            rows.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            rows.delete,
        )
        self.back_references = async_to_streamed_response_wrapper(
            rows.back_references,
        )
        self.ensure = async_to_streamed_response_wrapper(
            rows.ensure,
        )
        self.import_ = async_to_streamed_response_wrapper(
            rows.import_,
        )
