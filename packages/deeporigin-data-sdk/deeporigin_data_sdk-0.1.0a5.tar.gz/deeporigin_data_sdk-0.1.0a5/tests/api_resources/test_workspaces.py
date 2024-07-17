# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deeporigin_data import DeeporiginData, AsyncDeeporiginData
from deeporigin_data.types import (
    WorkspaceCreateResponse,
    WorkspaceUpdateResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestWorkspaces:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: DeeporiginData) -> None:
        workspace = client.workspaces.create(
            workspace={
                "hid": "hid",
                "name": "name",
            },
        )
        assert_matches_type(WorkspaceCreateResponse, workspace, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: DeeporiginData) -> None:
        workspace = client.workspaces.create(
            workspace={
                "hid": "hid",
                "name": "name",
                "parent_id": "parentId",
            },
        )
        assert_matches_type(WorkspaceCreateResponse, workspace, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: DeeporiginData) -> None:
        response = client.workspaces.with_raw_response.create(
            workspace={
                "hid": "hid",
                "name": "name",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workspace = response.parse()
        assert_matches_type(WorkspaceCreateResponse, workspace, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: DeeporiginData) -> None:
        with client.workspaces.with_streaming_response.create(
            workspace={
                "hid": "hid",
                "name": "name",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workspace = response.parse()
            assert_matches_type(WorkspaceCreateResponse, workspace, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_update(self, client: DeeporiginData) -> None:
        workspace = client.workspaces.update(
            id="id",
            workspace={},
        )
        assert_matches_type(WorkspaceUpdateResponse, workspace, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: DeeporiginData) -> None:
        workspace = client.workspaces.update(
            id="id",
            workspace={
                "hid": "hid",
                "name": "name",
                "parent_id": "parentId",
                "editor": {},
            },
        )
        assert_matches_type(WorkspaceUpdateResponse, workspace, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: DeeporiginData) -> None:
        response = client.workspaces.with_raw_response.update(
            id="id",
            workspace={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workspace = response.parse()
        assert_matches_type(WorkspaceUpdateResponse, workspace, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: DeeporiginData) -> None:
        with client.workspaces.with_streaming_response.update(
            id="id",
            workspace={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workspace = response.parse()
            assert_matches_type(WorkspaceUpdateResponse, workspace, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncWorkspaces:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncDeeporiginData) -> None:
        workspace = await async_client.workspaces.create(
            workspace={
                "hid": "hid",
                "name": "name",
            },
        )
        assert_matches_type(WorkspaceCreateResponse, workspace, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncDeeporiginData) -> None:
        workspace = await async_client.workspaces.create(
            workspace={
                "hid": "hid",
                "name": "name",
                "parent_id": "parentId",
            },
        )
        assert_matches_type(WorkspaceCreateResponse, workspace, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.workspaces.with_raw_response.create(
            workspace={
                "hid": "hid",
                "name": "name",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workspace = await response.parse()
        assert_matches_type(WorkspaceCreateResponse, workspace, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.workspaces.with_streaming_response.create(
            workspace={
                "hid": "hid",
                "name": "name",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workspace = await response.parse()
            assert_matches_type(WorkspaceCreateResponse, workspace, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_update(self, async_client: AsyncDeeporiginData) -> None:
        workspace = await async_client.workspaces.update(
            id="id",
            workspace={},
        )
        assert_matches_type(WorkspaceUpdateResponse, workspace, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncDeeporiginData) -> None:
        workspace = await async_client.workspaces.update(
            id="id",
            workspace={
                "hid": "hid",
                "name": "name",
                "parent_id": "parentId",
                "editor": {},
            },
        )
        assert_matches_type(WorkspaceUpdateResponse, workspace, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.workspaces.with_raw_response.update(
            id="id",
            workspace={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workspace = await response.parse()
        assert_matches_type(WorkspaceUpdateResponse, workspace, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.workspaces.with_streaming_response.update(
            id="id",
            workspace={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workspace = await response.parse()
            assert_matches_type(WorkspaceUpdateResponse, workspace, path=["response"])

        assert cast(Any, response.is_closed) is True
