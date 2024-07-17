# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deeporigin_data import DeeporiginData, AsyncDeeporiginData
from deeporigin_data.types import OrganizationInitializeResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestOrganizations:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_initialize(self, client: DeeporiginData) -> None:
        organization = client.organizations.initialize(
            body={},
        )
        assert_matches_type(OrganizationInitializeResponse, organization, path=["response"])

    @parametrize
    def test_raw_response_initialize(self, client: DeeporiginData) -> None:
        response = client.organizations.with_raw_response.initialize(
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        organization = response.parse()
        assert_matches_type(OrganizationInitializeResponse, organization, path=["response"])

    @parametrize
    def test_streaming_response_initialize(self, client: DeeporiginData) -> None:
        with client.organizations.with_streaming_response.initialize(
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            organization = response.parse()
            assert_matches_type(OrganizationInitializeResponse, organization, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncOrganizations:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_initialize(self, async_client: AsyncDeeporiginData) -> None:
        organization = await async_client.organizations.initialize(
            body={},
        )
        assert_matches_type(OrganizationInitializeResponse, organization, path=["response"])

    @parametrize
    async def test_raw_response_initialize(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.organizations.with_raw_response.initialize(
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        organization = await response.parse()
        assert_matches_type(OrganizationInitializeResponse, organization, path=["response"])

    @parametrize
    async def test_streaming_response_initialize(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.organizations.with_streaming_response.initialize(
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            organization = await response.parse()
            assert_matches_type(OrganizationInitializeResponse, organization, path=["response"])

        assert cast(Any, response.is_closed) is True
