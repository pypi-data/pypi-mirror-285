# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import code_execution_result_params, code_execution_describe_params
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
from ..types.code_execution_describe_response import CodeExecutionDescribeResponse

__all__ = ["CodeExecutionsResource", "AsyncCodeExecutionsResource"]


class CodeExecutionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CodeExecutionsResourceWithRawResponse:
        return CodeExecutionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CodeExecutionsResourceWithStreamingResponse:
        return CodeExecutionsResourceWithStreamingResponse(self)

    def describe(
        self,
        *,
        id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CodeExecutionDescribeResponse:
        """
        Returns information about a particular code execution.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/DescribeCodeExecution",
            body=maybe_transform({"id": id}, code_execution_describe_params.CodeExecutionDescribeParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CodeExecutionDescribeResponse,
        )

    def result(
        self,
        *,
        id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Returns the result of a code execution.

        Args:
          id: Deep Origin system ID.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/GetCodeExecutionResult",
            body=maybe_transform({"id": id}, code_execution_result_params.CodeExecutionResultParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncCodeExecutionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCodeExecutionsResourceWithRawResponse:
        return AsyncCodeExecutionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCodeExecutionsResourceWithStreamingResponse:
        return AsyncCodeExecutionsResourceWithStreamingResponse(self)

    async def describe(
        self,
        *,
        id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CodeExecutionDescribeResponse:
        """
        Returns information about a particular code execution.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/DescribeCodeExecution",
            body=await async_maybe_transform({"id": id}, code_execution_describe_params.CodeExecutionDescribeParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CodeExecutionDescribeResponse,
        )

    async def result(
        self,
        *,
        id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Returns the result of a code execution.

        Args:
          id: Deep Origin system ID.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/GetCodeExecutionResult",
            body=await async_maybe_transform({"id": id}, code_execution_result_params.CodeExecutionResultParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class CodeExecutionsResourceWithRawResponse:
    def __init__(self, code_executions: CodeExecutionsResource) -> None:
        self._code_executions = code_executions

        self.describe = to_raw_response_wrapper(
            code_executions.describe,
        )
        self.result = to_raw_response_wrapper(
            code_executions.result,
        )


class AsyncCodeExecutionsResourceWithRawResponse:
    def __init__(self, code_executions: AsyncCodeExecutionsResource) -> None:
        self._code_executions = code_executions

        self.describe = async_to_raw_response_wrapper(
            code_executions.describe,
        )
        self.result = async_to_raw_response_wrapper(
            code_executions.result,
        )


class CodeExecutionsResourceWithStreamingResponse:
    def __init__(self, code_executions: CodeExecutionsResource) -> None:
        self._code_executions = code_executions

        self.describe = to_streamed_response_wrapper(
            code_executions.describe,
        )
        self.result = to_streamed_response_wrapper(
            code_executions.result,
        )


class AsyncCodeExecutionsResourceWithStreamingResponse:
    def __init__(self, code_executions: AsyncCodeExecutionsResource) -> None:
        self._code_executions = code_executions

        self.describe = async_to_streamed_response_wrapper(
            code_executions.describe,
        )
        self.result = async_to_streamed_response_wrapper(
            code_executions.result,
        )
