# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import overload
from typing_extensions import Literal

import httpx

from ..types import (
    database_column_add_params,
    database_column_delete_params,
    database_column_update_params,
    database_column_unique_values_params,
)
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import (
    required_args,
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
from ..types.database_column_add_response import DatabaseColumnAddResponse
from ..types.database_column_delete_response import DatabaseColumnDeleteResponse
from ..types.database_column_update_response import DatabaseColumnUpdateResponse
from ..types.database_column_unique_values_response import DatabaseColumnUniqueValuesResponse

__all__ = ["DatabaseColumnsResource", "AsyncDatabaseColumnsResource"]


class DatabaseColumnsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DatabaseColumnsResourceWithRawResponse:
        return DatabaseColumnsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DatabaseColumnsResourceWithStreamingResponse:
        return DatabaseColumnsResourceWithStreamingResponse(self)

    def update(
        self,
        *,
        column: database_column_update_params.Column,
        column_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatabaseColumnUpdateResponse:
        """
        Update a column in a database.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/UpdateDatabaseColumn",
            body=maybe_transform(
                {
                    "column": column,
                    "column_id": column_id,
                },
                database_column_update_params.DatabaseColumnUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatabaseColumnUpdateResponse,
        )

    def delete(
        self,
        *,
        column_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatabaseColumnDeleteResponse:
        """
        Delete a column from a database.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/DeleteDatabaseColumn",
            body=maybe_transform({"column_id": column_id}, database_column_delete_params.DatabaseColumnDeleteParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatabaseColumnDeleteResponse,
        )

    def add(
        self,
        *,
        column: database_column_add_params.Column,
        database_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatabaseColumnAddResponse:
        """
        Add a column to a database.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/AddDatabaseColumn",
            body=maybe_transform(
                {
                    "column": column,
                    "database_id": database_id,
                },
                database_column_add_params.DatabaseColumnAddParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatabaseColumnAddResponse,
        )

    @overload
    def unique_values(
        self,
        *,
        column_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatabaseColumnUniqueValuesResponse:
        """
        Returns the unique values for every cell within the column.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def unique_values(
        self,
        *,
        database_row_id: str,
        system_column_name: Literal["creationParentId"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatabaseColumnUniqueValuesResponse:
        """
        Returns the unique values for every cell within the column.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["column_id"], ["database_row_id", "system_column_name"])
    def unique_values(
        self,
        *,
        column_id: str | NotGiven = NOT_GIVEN,
        database_row_id: str | NotGiven = NOT_GIVEN,
        system_column_name: Literal["creationParentId"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatabaseColumnUniqueValuesResponse:
        return self._post(
            "/ListDatabaseColumnUniqueValues",
            body=maybe_transform(
                {
                    "column_id": column_id,
                    "database_row_id": database_row_id,
                    "system_column_name": system_column_name,
                },
                database_column_unique_values_params.DatabaseColumnUniqueValuesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatabaseColumnUniqueValuesResponse,
        )


class AsyncDatabaseColumnsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDatabaseColumnsResourceWithRawResponse:
        return AsyncDatabaseColumnsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDatabaseColumnsResourceWithStreamingResponse:
        return AsyncDatabaseColumnsResourceWithStreamingResponse(self)

    async def update(
        self,
        *,
        column: database_column_update_params.Column,
        column_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatabaseColumnUpdateResponse:
        """
        Update a column in a database.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/UpdateDatabaseColumn",
            body=await async_maybe_transform(
                {
                    "column": column,
                    "column_id": column_id,
                },
                database_column_update_params.DatabaseColumnUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatabaseColumnUpdateResponse,
        )

    async def delete(
        self,
        *,
        column_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatabaseColumnDeleteResponse:
        """
        Delete a column from a database.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/DeleteDatabaseColumn",
            body=await async_maybe_transform(
                {"column_id": column_id}, database_column_delete_params.DatabaseColumnDeleteParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatabaseColumnDeleteResponse,
        )

    async def add(
        self,
        *,
        column: database_column_add_params.Column,
        database_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatabaseColumnAddResponse:
        """
        Add a column to a database.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/AddDatabaseColumn",
            body=await async_maybe_transform(
                {
                    "column": column,
                    "database_id": database_id,
                },
                database_column_add_params.DatabaseColumnAddParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatabaseColumnAddResponse,
        )

    @overload
    async def unique_values(
        self,
        *,
        column_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatabaseColumnUniqueValuesResponse:
        """
        Returns the unique values for every cell within the column.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def unique_values(
        self,
        *,
        database_row_id: str,
        system_column_name: Literal["creationParentId"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatabaseColumnUniqueValuesResponse:
        """
        Returns the unique values for every cell within the column.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["column_id"], ["database_row_id", "system_column_name"])
    async def unique_values(
        self,
        *,
        column_id: str | NotGiven = NOT_GIVEN,
        database_row_id: str | NotGiven = NOT_GIVEN,
        system_column_name: Literal["creationParentId"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatabaseColumnUniqueValuesResponse:
        return await self._post(
            "/ListDatabaseColumnUniqueValues",
            body=await async_maybe_transform(
                {
                    "column_id": column_id,
                    "database_row_id": database_row_id,
                    "system_column_name": system_column_name,
                },
                database_column_unique_values_params.DatabaseColumnUniqueValuesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatabaseColumnUniqueValuesResponse,
        )


class DatabaseColumnsResourceWithRawResponse:
    def __init__(self, database_columns: DatabaseColumnsResource) -> None:
        self._database_columns = database_columns

        self.update = to_raw_response_wrapper(
            database_columns.update,
        )
        self.delete = to_raw_response_wrapper(
            database_columns.delete,
        )
        self.add = to_raw_response_wrapper(
            database_columns.add,
        )
        self.unique_values = to_raw_response_wrapper(
            database_columns.unique_values,
        )


class AsyncDatabaseColumnsResourceWithRawResponse:
    def __init__(self, database_columns: AsyncDatabaseColumnsResource) -> None:
        self._database_columns = database_columns

        self.update = async_to_raw_response_wrapper(
            database_columns.update,
        )
        self.delete = async_to_raw_response_wrapper(
            database_columns.delete,
        )
        self.add = async_to_raw_response_wrapper(
            database_columns.add,
        )
        self.unique_values = async_to_raw_response_wrapper(
            database_columns.unique_values,
        )


class DatabaseColumnsResourceWithStreamingResponse:
    def __init__(self, database_columns: DatabaseColumnsResource) -> None:
        self._database_columns = database_columns

        self.update = to_streamed_response_wrapper(
            database_columns.update,
        )
        self.delete = to_streamed_response_wrapper(
            database_columns.delete,
        )
        self.add = to_streamed_response_wrapper(
            database_columns.add,
        )
        self.unique_values = to_streamed_response_wrapper(
            database_columns.unique_values,
        )


class AsyncDatabaseColumnsResourceWithStreamingResponse:
    def __init__(self, database_columns: AsyncDatabaseColumnsResource) -> None:
        self._database_columns = database_columns

        self.update = async_to_streamed_response_wrapper(
            database_columns.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            database_columns.delete,
        )
        self.add = async_to_streamed_response_wrapper(
            database_columns.add,
        )
        self.unique_values = async_to_streamed_response_wrapper(
            database_columns.unique_values,
        )
