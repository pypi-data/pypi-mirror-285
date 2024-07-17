# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import base_sequence_parse_params
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
from ..types.base_sequence_parse_response import BaseSequenceParseResponse

__all__ = ["BaseSequencesResource", "AsyncBaseSequencesResource"]


class BaseSequencesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> BaseSequencesResourceWithRawResponse:
        return BaseSequencesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BaseSequencesResourceWithStreamingResponse:
        return BaseSequencesResourceWithStreamingResponse(self)

    def parse(
        self,
        *,
        file_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BaseSequenceParseResponse:
        """
        Parses a base sequence file and returns the parsed result.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/ParseBaseSequenceData",
            body=maybe_transform({"file_id": file_id}, base_sequence_parse_params.BaseSequenceParseParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BaseSequenceParseResponse,
        )


class AsyncBaseSequencesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncBaseSequencesResourceWithRawResponse:
        return AsyncBaseSequencesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBaseSequencesResourceWithStreamingResponse:
        return AsyncBaseSequencesResourceWithStreamingResponse(self)

    async def parse(
        self,
        *,
        file_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BaseSequenceParseResponse:
        """
        Parses a base sequence file and returns the parsed result.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/ParseBaseSequenceData",
            body=await async_maybe_transform({"file_id": file_id}, base_sequence_parse_params.BaseSequenceParseParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BaseSequenceParseResponse,
        )


class BaseSequencesResourceWithRawResponse:
    def __init__(self, base_sequences: BaseSequencesResource) -> None:
        self._base_sequences = base_sequences

        self.parse = to_raw_response_wrapper(
            base_sequences.parse,
        )


class AsyncBaseSequencesResourceWithRawResponse:
    def __init__(self, base_sequences: AsyncBaseSequencesResource) -> None:
        self._base_sequences = base_sequences

        self.parse = async_to_raw_response_wrapper(
            base_sequences.parse,
        )


class BaseSequencesResourceWithStreamingResponse:
    def __init__(self, base_sequences: BaseSequencesResource) -> None:
        self._base_sequences = base_sequences

        self.parse = to_streamed_response_wrapper(
            base_sequences.parse,
        )


class AsyncBaseSequencesResourceWithStreamingResponse:
    def __init__(self, base_sequences: AsyncBaseSequencesResource) -> None:
        self._base_sequences = base_sequences

        self.parse = async_to_streamed_response_wrapper(
            base_sequences.parse,
        )
