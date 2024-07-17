# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from deeporigin_data import DeeporiginData, AsyncDeeporiginData

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestChatMessages:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_send(self, client: DeeporiginData) -> None:
        chat_message = client.chat_messages.send(
            messages=[
                {
                    "content": "x",
                    "role": "user",
                },
                {
                    "content": "x",
                    "role": "user",
                },
                {
                    "content": "x",
                    "role": "user",
                },
            ],
            thread_id="threadId",
        )
        assert chat_message is None

    @parametrize
    def test_method_send_with_all_params(self, client: DeeporiginData) -> None:
        chat_message = client.chat_messages.send(
            messages=[
                {
                    "content": "x",
                    "role": "user",
                },
                {
                    "content": "x",
                    "role": "user",
                },
                {
                    "content": "x",
                    "role": "user",
                },
            ],
            thread_id="threadId",
            context={
                "databases": [
                    {
                        "database": {
                            "name": "name",
                            "hid": "hid",
                            "hid_prefix": "hidPrefix",
                        },
                        "rows": [
                            {
                                "name": "name",
                                "hid": "hid",
                            },
                            {
                                "name": "name",
                                "hid": "hid",
                            },
                            {
                                "name": "name",
                                "hid": "hid",
                            },
                        ],
                        "columns": [{"name": "name"}, {"name": "name"}, {"name": "name"}],
                    },
                    {
                        "database": {
                            "name": "name",
                            "hid": "hid",
                            "hid_prefix": "hidPrefix",
                        },
                        "rows": [
                            {
                                "name": "name",
                                "hid": "hid",
                            },
                            {
                                "name": "name",
                                "hid": "hid",
                            },
                            {
                                "name": "name",
                                "hid": "hid",
                            },
                        ],
                        "columns": [{"name": "name"}, {"name": "name"}, {"name": "name"}],
                    },
                    {
                        "database": {
                            "name": "name",
                            "hid": "hid",
                            "hid_prefix": "hidPrefix",
                        },
                        "rows": [
                            {
                                "name": "name",
                                "hid": "hid",
                            },
                            {
                                "name": "name",
                                "hid": "hid",
                            },
                            {
                                "name": "name",
                                "hid": "hid",
                            },
                        ],
                        "columns": [{"name": "name"}, {"name": "name"}, {"name": "name"}],
                    },
                ]
            },
        )
        assert chat_message is None

    @parametrize
    def test_raw_response_send(self, client: DeeporiginData) -> None:
        response = client.chat_messages.with_raw_response.send(
            messages=[
                {
                    "content": "x",
                    "role": "user",
                },
                {
                    "content": "x",
                    "role": "user",
                },
                {
                    "content": "x",
                    "role": "user",
                },
            ],
            thread_id="threadId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chat_message = response.parse()
        assert chat_message is None

    @parametrize
    def test_streaming_response_send(self, client: DeeporiginData) -> None:
        with client.chat_messages.with_streaming_response.send(
            messages=[
                {
                    "content": "x",
                    "role": "user",
                },
                {
                    "content": "x",
                    "role": "user",
                },
                {
                    "content": "x",
                    "role": "user",
                },
            ],
            thread_id="threadId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chat_message = response.parse()
            assert chat_message is None

        assert cast(Any, response.is_closed) is True


class TestAsyncChatMessages:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_send(self, async_client: AsyncDeeporiginData) -> None:
        chat_message = await async_client.chat_messages.send(
            messages=[
                {
                    "content": "x",
                    "role": "user",
                },
                {
                    "content": "x",
                    "role": "user",
                },
                {
                    "content": "x",
                    "role": "user",
                },
            ],
            thread_id="threadId",
        )
        assert chat_message is None

    @parametrize
    async def test_method_send_with_all_params(self, async_client: AsyncDeeporiginData) -> None:
        chat_message = await async_client.chat_messages.send(
            messages=[
                {
                    "content": "x",
                    "role": "user",
                },
                {
                    "content": "x",
                    "role": "user",
                },
                {
                    "content": "x",
                    "role": "user",
                },
            ],
            thread_id="threadId",
            context={
                "databases": [
                    {
                        "database": {
                            "name": "name",
                            "hid": "hid",
                            "hid_prefix": "hidPrefix",
                        },
                        "rows": [
                            {
                                "name": "name",
                                "hid": "hid",
                            },
                            {
                                "name": "name",
                                "hid": "hid",
                            },
                            {
                                "name": "name",
                                "hid": "hid",
                            },
                        ],
                        "columns": [{"name": "name"}, {"name": "name"}, {"name": "name"}],
                    },
                    {
                        "database": {
                            "name": "name",
                            "hid": "hid",
                            "hid_prefix": "hidPrefix",
                        },
                        "rows": [
                            {
                                "name": "name",
                                "hid": "hid",
                            },
                            {
                                "name": "name",
                                "hid": "hid",
                            },
                            {
                                "name": "name",
                                "hid": "hid",
                            },
                        ],
                        "columns": [{"name": "name"}, {"name": "name"}, {"name": "name"}],
                    },
                    {
                        "database": {
                            "name": "name",
                            "hid": "hid",
                            "hid_prefix": "hidPrefix",
                        },
                        "rows": [
                            {
                                "name": "name",
                                "hid": "hid",
                            },
                            {
                                "name": "name",
                                "hid": "hid",
                            },
                            {
                                "name": "name",
                                "hid": "hid",
                            },
                        ],
                        "columns": [{"name": "name"}, {"name": "name"}, {"name": "name"}],
                    },
                ]
            },
        )
        assert chat_message is None

    @parametrize
    async def test_raw_response_send(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.chat_messages.with_raw_response.send(
            messages=[
                {
                    "content": "x",
                    "role": "user",
                },
                {
                    "content": "x",
                    "role": "user",
                },
                {
                    "content": "x",
                    "role": "user",
                },
            ],
            thread_id="threadId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chat_message = await response.parse()
        assert chat_message is None

    @parametrize
    async def test_streaming_response_send(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.chat_messages.with_streaming_response.send(
            messages=[
                {
                    "content": "x",
                    "role": "user",
                },
                {
                    "content": "x",
                    "role": "user",
                },
                {
                    "content": "x",
                    "role": "user",
                },
            ],
            thread_id="threadId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chat_message = await response.parse()
            assert chat_message is None

        assert cast(Any, response.is_closed) is True
