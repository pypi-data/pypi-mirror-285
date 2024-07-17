# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deeporigin_data import DeeporiginData, AsyncDeeporiginData
from deeporigin_data.types import ColumnOptionConfigureResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestColumnOptions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_configure(self, client: DeeporiginData) -> None:
        column_option = client.column_options.configure(
            column_id="columnId",
            option_configuration=[
                {
                    "option": "option",
                    "op": "add",
                },
                {
                    "option": "option",
                    "op": "add",
                },
                {
                    "option": "option",
                    "op": "add",
                },
            ],
        )
        assert_matches_type(ColumnOptionConfigureResponse, column_option, path=["response"])

    @parametrize
    def test_raw_response_configure(self, client: DeeporiginData) -> None:
        response = client.column_options.with_raw_response.configure(
            column_id="columnId",
            option_configuration=[
                {
                    "option": "option",
                    "op": "add",
                },
                {
                    "option": "option",
                    "op": "add",
                },
                {
                    "option": "option",
                    "op": "add",
                },
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        column_option = response.parse()
        assert_matches_type(ColumnOptionConfigureResponse, column_option, path=["response"])

    @parametrize
    def test_streaming_response_configure(self, client: DeeporiginData) -> None:
        with client.column_options.with_streaming_response.configure(
            column_id="columnId",
            option_configuration=[
                {
                    "option": "option",
                    "op": "add",
                },
                {
                    "option": "option",
                    "op": "add",
                },
                {
                    "option": "option",
                    "op": "add",
                },
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            column_option = response.parse()
            assert_matches_type(ColumnOptionConfigureResponse, column_option, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncColumnOptions:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_configure(self, async_client: AsyncDeeporiginData) -> None:
        column_option = await async_client.column_options.configure(
            column_id="columnId",
            option_configuration=[
                {
                    "option": "option",
                    "op": "add",
                },
                {
                    "option": "option",
                    "op": "add",
                },
                {
                    "option": "option",
                    "op": "add",
                },
            ],
        )
        assert_matches_type(ColumnOptionConfigureResponse, column_option, path=["response"])

    @parametrize
    async def test_raw_response_configure(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.column_options.with_raw_response.configure(
            column_id="columnId",
            option_configuration=[
                {
                    "option": "option",
                    "op": "add",
                },
                {
                    "option": "option",
                    "op": "add",
                },
                {
                    "option": "option",
                    "op": "add",
                },
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        column_option = await response.parse()
        assert_matches_type(ColumnOptionConfigureResponse, column_option, path=["response"])

    @parametrize
    async def test_streaming_response_configure(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.column_options.with_streaming_response.configure(
            column_id="columnId",
            option_configuration=[
                {
                    "option": "option",
                    "op": "add",
                },
                {
                    "option": "option",
                    "op": "add",
                },
                {
                    "option": "option",
                    "op": "add",
                },
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            column_option = await response.parse()
            assert_matches_type(ColumnOptionConfigureResponse, column_option, path=["response"])

        assert cast(Any, response.is_closed) is True
