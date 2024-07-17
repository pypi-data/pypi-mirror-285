# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...types import chat_thread_create_params
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import (
    maybe_transform,
    async_maybe_transform,
)
from .messages import (
    MessagesResource,
    AsyncMessagesResource,
    MessagesResourceWithRawResponse,
    AsyncMessagesResourceWithRawResponse,
    MessagesResourceWithStreamingResponse,
    AsyncMessagesResourceWithStreamingResponse,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.chat_thread_create_response import ChatThreadCreateResponse

__all__ = ["ChatThreadsResource", "AsyncChatThreadsResource"]


class ChatThreadsResource(SyncAPIResource):
    @cached_property
    def messages(self) -> MessagesResource:
        return MessagesResource(self._client)

    @cached_property
    def with_raw_response(self) -> ChatThreadsResourceWithRawResponse:
        return ChatThreadsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ChatThreadsResourceWithStreamingResponse:
        return ChatThreadsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChatThreadCreateResponse:
        """
        Create a new chat thread.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/CreateChatThread",
            body=maybe_transform(body, chat_thread_create_params.ChatThreadCreateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ChatThreadCreateResponse,
        )


class AsyncChatThreadsResource(AsyncAPIResource):
    @cached_property
    def messages(self) -> AsyncMessagesResource:
        return AsyncMessagesResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncChatThreadsResourceWithRawResponse:
        return AsyncChatThreadsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncChatThreadsResourceWithStreamingResponse:
        return AsyncChatThreadsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChatThreadCreateResponse:
        """
        Create a new chat thread.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/CreateChatThread",
            body=await async_maybe_transform(body, chat_thread_create_params.ChatThreadCreateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ChatThreadCreateResponse,
        )


class ChatThreadsResourceWithRawResponse:
    def __init__(self, chat_threads: ChatThreadsResource) -> None:
        self._chat_threads = chat_threads

        self.create = to_raw_response_wrapper(
            chat_threads.create,
        )

    @cached_property
    def messages(self) -> MessagesResourceWithRawResponse:
        return MessagesResourceWithRawResponse(self._chat_threads.messages)


class AsyncChatThreadsResourceWithRawResponse:
    def __init__(self, chat_threads: AsyncChatThreadsResource) -> None:
        self._chat_threads = chat_threads

        self.create = async_to_raw_response_wrapper(
            chat_threads.create,
        )

    @cached_property
    def messages(self) -> AsyncMessagesResourceWithRawResponse:
        return AsyncMessagesResourceWithRawResponse(self._chat_threads.messages)


class ChatThreadsResourceWithStreamingResponse:
    def __init__(self, chat_threads: ChatThreadsResource) -> None:
        self._chat_threads = chat_threads

        self.create = to_streamed_response_wrapper(
            chat_threads.create,
        )

    @cached_property
    def messages(self) -> MessagesResourceWithStreamingResponse:
        return MessagesResourceWithStreamingResponse(self._chat_threads.messages)


class AsyncChatThreadsResourceWithStreamingResponse:
    def __init__(self, chat_threads: AsyncChatThreadsResource) -> None:
        self._chat_threads = chat_threads

        self.create = async_to_streamed_response_wrapper(
            chat_threads.create,
        )

    @cached_property
    def messages(self) -> AsyncMessagesResourceWithStreamingResponse:
        return AsyncMessagesResourceWithStreamingResponse(self._chat_threads.messages)
