# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deeporigin_data import DeeporiginData, AsyncDeeporiginData
from deeporigin_data.types import (
    ListRowsResponse,
    ListFilesResponse,
    DeleteRowsResponse,
    EnsureRowsResponse,
    ImportRowsResponse,
    DescribeRowResponse,
    DescribeFileResponse,
    ListMentionsResponse,
    InitializeOrgResponse,
    CreateDatabaseResponse,
    UpdateDatabaseResponse,
    ConvertIDFormatResponse,
    CreateWorkspaceResponse,
    ExecuteCodeSyncResponse,
    UpdateWorkspaceResponse,
    CreateFileUploadResponse,
    ExecuteCodeAsyncResponse,
    ListDatabaseRowsResponse,
    AddDatabaseColumnResponse,
    DeleteDatabaseColumnResponse,
    UpdateDatabaseColumnResponse,
    CreateFileDownloadURLResponse,
    DescribeCodeExecutionResponse,
    DescribeDatabaseStatsResponse,
    ListRowBackReferencesResponse,
    ConfigureColumnSelectOptionsResponse,
    ListDatabaseColumnUniqueValuesResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTopLevel:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_add_database_column(self, client: DeeporiginData) -> None:
        top_level = client.add_database_column(
            column={
                "type": "boolean",
                "name": "name",
                "key": "key",
                "cardinality": "one",
            },
            database_id="databaseId",
        )
        assert_matches_type(AddDatabaseColumnResponse, top_level, path=["response"])

    @parametrize
    def test_method_add_database_column_with_all_params(self, client: DeeporiginData) -> None:
        top_level = client.add_database_column(
            column={
                "type": "boolean",
                "name": "name",
                "key": "key",
                "cardinality": "one",
                "systemType": "name",
                "isRequired": True,
                "enabledViewers": ["code", "html", "image"],
                "cellJsonSchema": {},
            },
            database_id="databaseId",
        )
        assert_matches_type(AddDatabaseColumnResponse, top_level, path=["response"])

    @parametrize
    def test_raw_response_add_database_column(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.add_database_column(
            column={
                "type": "boolean",
                "name": "name",
                "key": "key",
                "cardinality": "one",
            },
            database_id="databaseId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = response.parse()
        assert_matches_type(AddDatabaseColumnResponse, top_level, path=["response"])

    @parametrize
    def test_streaming_response_add_database_column(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.add_database_column(
            column={
                "type": "boolean",
                "name": "name",
                "key": "key",
                "cardinality": "one",
            },
            database_id="databaseId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = response.parse()
            assert_matches_type(AddDatabaseColumnResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_archive_files(self, client: DeeporiginData) -> None:
        top_level = client.archive_files(
            file_ids=["string", "string", "string"],
        )
        assert_matches_type(object, top_level, path=["response"])

    @parametrize
    def test_raw_response_archive_files(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.archive_files(
            file_ids=["string", "string", "string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = response.parse()
        assert_matches_type(object, top_level, path=["response"])

    @parametrize
    def test_streaming_response_archive_files(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.archive_files(
            file_ids=["string", "string", "string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = response.parse()
            assert_matches_type(object, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_configure_column_select_options(self, client: DeeporiginData) -> None:
        top_level = client.configure_column_select_options(
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
        assert_matches_type(ConfigureColumnSelectOptionsResponse, top_level, path=["response"])

    @parametrize
    def test_raw_response_configure_column_select_options(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.configure_column_select_options(
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
        top_level = response.parse()
        assert_matches_type(ConfigureColumnSelectOptionsResponse, top_level, path=["response"])

    @parametrize
    def test_streaming_response_configure_column_select_options(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.configure_column_select_options(
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

            top_level = response.parse()
            assert_matches_type(ConfigureColumnSelectOptionsResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_convert_id_format(self, client: DeeporiginData) -> None:
        top_level = client.convert_id_format(
            conversions=[{"id": "id"}, {"id": "id"}, {"id": "id"}],
        )
        assert_matches_type(ConvertIDFormatResponse, top_level, path=["response"])

    @parametrize
    def test_raw_response_convert_id_format(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.convert_id_format(
            conversions=[{"id": "id"}, {"id": "id"}, {"id": "id"}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = response.parse()
        assert_matches_type(ConvertIDFormatResponse, top_level, path=["response"])

    @parametrize
    def test_streaming_response_convert_id_format(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.convert_id_format(
            conversions=[{"id": "id"}, {"id": "id"}, {"id": "id"}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = response.parse()
            assert_matches_type(ConvertIDFormatResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_create_database(self, client: DeeporiginData) -> None:
        top_level = client.create_database(
            database={
                "hid": "hid",
                "name": "name",
                "hid_prefix": "hidPrefix",
            },
        )
        assert_matches_type(CreateDatabaseResponse, top_level, path=["response"])

    @parametrize
    def test_method_create_database_with_all_params(self, client: DeeporiginData) -> None:
        top_level = client.create_database(
            database={
                "hid": "hid",
                "name": "name",
                "parent_id": "parentId",
                "hid_prefix": "hidPrefix",
                "cols": [{}, {}, {}],
            },
        )
        assert_matches_type(CreateDatabaseResponse, top_level, path=["response"])

    @parametrize
    def test_raw_response_create_database(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.create_database(
            database={
                "hid": "hid",
                "name": "name",
                "hid_prefix": "hidPrefix",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = response.parse()
        assert_matches_type(CreateDatabaseResponse, top_level, path=["response"])

    @parametrize
    def test_streaming_response_create_database(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.create_database(
            database={
                "hid": "hid",
                "name": "name",
                "hid_prefix": "hidPrefix",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = response.parse()
            assert_matches_type(CreateDatabaseResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_create_file_download_url(self, client: DeeporiginData) -> None:
        top_level = client.create_file_download_url(
            file_id="fileId",
        )
        assert_matches_type(CreateFileDownloadURLResponse, top_level, path=["response"])

    @parametrize
    def test_raw_response_create_file_download_url(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.create_file_download_url(
            file_id="fileId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = response.parse()
        assert_matches_type(CreateFileDownloadURLResponse, top_level, path=["response"])

    @parametrize
    def test_streaming_response_create_file_download_url(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.create_file_download_url(
            file_id="fileId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = response.parse()
            assert_matches_type(CreateFileDownloadURLResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_create_file_upload(self, client: DeeporiginData) -> None:
        top_level = client.create_file_upload(
            content_length="contentLength",
            name="name",
        )
        assert_matches_type(CreateFileUploadResponse, top_level, path=["response"])

    @parametrize
    def test_method_create_file_upload_with_all_params(self, client: DeeporiginData) -> None:
        top_level = client.create_file_upload(
            content_length="contentLength",
            name="name",
            content_type="contentType",
        )
        assert_matches_type(CreateFileUploadResponse, top_level, path=["response"])

    @parametrize
    def test_raw_response_create_file_upload(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.create_file_upload(
            content_length="contentLength",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = response.parse()
        assert_matches_type(CreateFileUploadResponse, top_level, path=["response"])

    @parametrize
    def test_streaming_response_create_file_upload(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.create_file_upload(
            content_length="contentLength",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = response.parse()
            assert_matches_type(CreateFileUploadResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_create_workspace(self, client: DeeporiginData) -> None:
        top_level = client.create_workspace(
            workspace={
                "hid": "hid",
                "name": "name",
            },
        )
        assert_matches_type(CreateWorkspaceResponse, top_level, path=["response"])

    @parametrize
    def test_method_create_workspace_with_all_params(self, client: DeeporiginData) -> None:
        top_level = client.create_workspace(
            workspace={
                "hid": "hid",
                "name": "name",
                "parent_id": "parentId",
            },
        )
        assert_matches_type(CreateWorkspaceResponse, top_level, path=["response"])

    @parametrize
    def test_raw_response_create_workspace(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.create_workspace(
            workspace={
                "hid": "hid",
                "name": "name",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = response.parse()
        assert_matches_type(CreateWorkspaceResponse, top_level, path=["response"])

    @parametrize
    def test_streaming_response_create_workspace(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.create_workspace(
            workspace={
                "hid": "hid",
                "name": "name",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = response.parse()
            assert_matches_type(CreateWorkspaceResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete_database_column(self, client: DeeporiginData) -> None:
        top_level = client.delete_database_column(
            column_id="columnId",
        )
        assert_matches_type(DeleteDatabaseColumnResponse, top_level, path=["response"])

    @parametrize
    def test_raw_response_delete_database_column(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.delete_database_column(
            column_id="columnId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = response.parse()
        assert_matches_type(DeleteDatabaseColumnResponse, top_level, path=["response"])

    @parametrize
    def test_streaming_response_delete_database_column(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.delete_database_column(
            column_id="columnId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = response.parse()
            assert_matches_type(DeleteDatabaseColumnResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete_rows(self, client: DeeporiginData) -> None:
        top_level = client.delete_rows(
            row_ids=["string", "string", "string"],
        )
        assert_matches_type(DeleteRowsResponse, top_level, path=["response"])

    @parametrize
    def test_raw_response_delete_rows(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.delete_rows(
            row_ids=["string", "string", "string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = response.parse()
        assert_matches_type(DeleteRowsResponse, top_level, path=["response"])

    @parametrize
    def test_streaming_response_delete_rows(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.delete_rows(
            row_ids=["string", "string", "string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = response.parse()
            assert_matches_type(DeleteRowsResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_describe_code_execution(self, client: DeeporiginData) -> None:
        top_level = client.describe_code_execution(
            id="id",
        )
        assert_matches_type(DescribeCodeExecutionResponse, top_level, path=["response"])

    @parametrize
    def test_raw_response_describe_code_execution(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.describe_code_execution(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = response.parse()
        assert_matches_type(DescribeCodeExecutionResponse, top_level, path=["response"])

    @parametrize
    def test_streaming_response_describe_code_execution(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.describe_code_execution(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = response.parse()
            assert_matches_type(DescribeCodeExecutionResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_describe_database_stats(self, client: DeeporiginData) -> None:
        top_level = client.describe_database_stats(
            database_id="databaseId",
        )
        assert_matches_type(DescribeDatabaseStatsResponse, top_level, path=["response"])

    @parametrize
    def test_raw_response_describe_database_stats(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.describe_database_stats(
            database_id="databaseId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = response.parse()
        assert_matches_type(DescribeDatabaseStatsResponse, top_level, path=["response"])

    @parametrize
    def test_streaming_response_describe_database_stats(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.describe_database_stats(
            database_id="databaseId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = response.parse()
            assert_matches_type(DescribeDatabaseStatsResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_describe_file(self, client: DeeporiginData) -> None:
        top_level = client.describe_file(
            file_id="fileId",
        )
        assert_matches_type(DescribeFileResponse, top_level, path=["response"])

    @parametrize
    def test_raw_response_describe_file(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.describe_file(
            file_id="fileId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = response.parse()
        assert_matches_type(DescribeFileResponse, top_level, path=["response"])

    @parametrize
    def test_streaming_response_describe_file(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.describe_file(
            file_id="fileId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = response.parse()
            assert_matches_type(DescribeFileResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_describe_row(self, client: DeeporiginData) -> None:
        top_level = client.describe_row(
            row_id="rowId",
        )
        assert_matches_type(DescribeRowResponse, top_level, path=["response"])

    @parametrize
    def test_method_describe_row_with_all_params(self, client: DeeporiginData) -> None:
        top_level = client.describe_row(
            row_id="rowId",
            column_selection={
                "include": ["string"],
                "exclude": ["string"],
            },
            fields=True,
        )
        assert_matches_type(DescribeRowResponse, top_level, path=["response"])

    @parametrize
    def test_raw_response_describe_row(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.describe_row(
            row_id="rowId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = response.parse()
        assert_matches_type(DescribeRowResponse, top_level, path=["response"])

    @parametrize
    def test_streaming_response_describe_row(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.describe_row(
            row_id="rowId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = response.parse()
            assert_matches_type(DescribeRowResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_ensure_rows(self, client: DeeporiginData) -> None:
        top_level = client.ensure_rows(
            database_id="databaseId",
            rows=[{}],
        )
        assert_matches_type(EnsureRowsResponse, top_level, path=["response"])

    @parametrize
    def test_raw_response_ensure_rows(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.ensure_rows(
            database_id="databaseId",
            rows=[{}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = response.parse()
        assert_matches_type(EnsureRowsResponse, top_level, path=["response"])

    @parametrize
    def test_streaming_response_ensure_rows(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.ensure_rows(
            database_id="databaseId",
            rows=[{}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = response.parse()
            assert_matches_type(EnsureRowsResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_execute_code_async(self, client: DeeporiginData) -> None:
        top_level = client.execute_code_async(
            code="code",
            code_language="python",
        )
        assert_matches_type(ExecuteCodeAsyncResponse, top_level, path=["response"])

    @parametrize
    def test_raw_response_execute_code_async(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.execute_code_async(
            code="code",
            code_language="python",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = response.parse()
        assert_matches_type(ExecuteCodeAsyncResponse, top_level, path=["response"])

    @parametrize
    def test_streaming_response_execute_code_async(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.execute_code_async(
            code="code",
            code_language="python",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = response.parse()
            assert_matches_type(ExecuteCodeAsyncResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_execute_code_sync(self, client: DeeporiginData) -> None:
        top_level = client.execute_code_sync(
            code="code",
            code_language="python",
        )
        assert_matches_type(ExecuteCodeSyncResponse, top_level, path=["response"])

    @parametrize
    def test_raw_response_execute_code_sync(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.execute_code_sync(
            code="code",
            code_language="python",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = response.parse()
        assert_matches_type(ExecuteCodeSyncResponse, top_level, path=["response"])

    @parametrize
    def test_streaming_response_execute_code_sync(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.execute_code_sync(
            code="code",
            code_language="python",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = response.parse()
            assert_matches_type(ExecuteCodeSyncResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_get_code_execution_result(self, client: DeeporiginData) -> None:
        top_level = client.get_code_execution_result(
            id="id",
        )
        assert_matches_type(object, top_level, path=["response"])

    @parametrize
    def test_raw_response_get_code_execution_result(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.get_code_execution_result(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = response.parse()
        assert_matches_type(object, top_level, path=["response"])

    @parametrize
    def test_streaming_response_get_code_execution_result(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.get_code_execution_result(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = response.parse()
            assert_matches_type(object, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_import_rows(self, client: DeeporiginData) -> None:
        top_level = client.import_rows(
            database_id="databaseId",
        )
        assert_matches_type(ImportRowsResponse, top_level, path=["response"])

    @parametrize
    def test_raw_response_import_rows(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.import_rows(
            database_id="databaseId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = response.parse()
        assert_matches_type(ImportRowsResponse, top_level, path=["response"])

    @parametrize
    def test_streaming_response_import_rows(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.import_rows(
            database_id="databaseId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = response.parse()
            assert_matches_type(ImportRowsResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_initialize_org(self, client: DeeporiginData) -> None:
        top_level = client.initialize_org(
            body={},
        )
        assert_matches_type(InitializeOrgResponse, top_level, path=["response"])

    @parametrize
    def test_raw_response_initialize_org(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.initialize_org(
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = response.parse()
        assert_matches_type(InitializeOrgResponse, top_level, path=["response"])

    @parametrize
    def test_streaming_response_initialize_org(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.initialize_org(
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = response.parse()
            assert_matches_type(InitializeOrgResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_list_database_column_unique_values_overload_1(self, client: DeeporiginData) -> None:
        top_level = client.list_database_column_unique_values(
            column_id="columnId",
        )
        assert_matches_type(ListDatabaseColumnUniqueValuesResponse, top_level, path=["response"])

    @parametrize
    def test_raw_response_list_database_column_unique_values_overload_1(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.list_database_column_unique_values(
            column_id="columnId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = response.parse()
        assert_matches_type(ListDatabaseColumnUniqueValuesResponse, top_level, path=["response"])

    @parametrize
    def test_streaming_response_list_database_column_unique_values_overload_1(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.list_database_column_unique_values(
            column_id="columnId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = response.parse()
            assert_matches_type(ListDatabaseColumnUniqueValuesResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_list_database_column_unique_values_overload_2(self, client: DeeporiginData) -> None:
        top_level = client.list_database_column_unique_values(
            database_row_id="databaseRowId",
            system_column_name="creationParentId",
        )
        assert_matches_type(ListDatabaseColumnUniqueValuesResponse, top_level, path=["response"])

    @parametrize
    def test_raw_response_list_database_column_unique_values_overload_2(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.list_database_column_unique_values(
            database_row_id="databaseRowId",
            system_column_name="creationParentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = response.parse()
        assert_matches_type(ListDatabaseColumnUniqueValuesResponse, top_level, path=["response"])

    @parametrize
    def test_streaming_response_list_database_column_unique_values_overload_2(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.list_database_column_unique_values(
            database_row_id="databaseRowId",
            system_column_name="creationParentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = response.parse()
            assert_matches_type(ListDatabaseColumnUniqueValuesResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_list_database_rows(self, client: DeeporiginData) -> None:
        top_level = client.list_database_rows(
            database_row_id="databaseRowId",
        )
        assert_matches_type(ListDatabaseRowsResponse, top_level, path=["response"])

    @parametrize
    def test_method_list_database_rows_with_all_params(self, client: DeeporiginData) -> None:
        top_level = client.list_database_rows(
            database_row_id="databaseRowId",
            column_selection={
                "include": ["string"],
                "exclude": ["string"],
            },
            creation_block_id="creationBlockId",
            creation_parent_id="creationParentId",
            filter={
                "filter_type": "text",
                "column_id": "columnId",
                "operator": "equals",
                "filter_value": "filterValue",
            },
        )
        assert_matches_type(ListDatabaseRowsResponse, top_level, path=["response"])

    @parametrize
    def test_raw_response_list_database_rows(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.list_database_rows(
            database_row_id="databaseRowId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = response.parse()
        assert_matches_type(ListDatabaseRowsResponse, top_level, path=["response"])

    @parametrize
    def test_streaming_response_list_database_rows(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.list_database_rows(
            database_row_id="databaseRowId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = response.parse()
            assert_matches_type(ListDatabaseRowsResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_list_files(self, client: DeeporiginData) -> None:
        top_level = client.list_files()
        assert_matches_type(ListFilesResponse, top_level, path=["response"])

    @parametrize
    def test_method_list_files_with_all_params(self, client: DeeporiginData) -> None:
        top_level = client.list_files(
            filters=[
                {
                    "assigned_row_ids": ["string", "string", "string"],
                    "is_unassigned": True,
                },
                {
                    "assigned_row_ids": ["string", "string", "string"],
                    "is_unassigned": True,
                },
                {
                    "assigned_row_ids": ["string", "string", "string"],
                    "is_unassigned": True,
                },
            ],
        )
        assert_matches_type(ListFilesResponse, top_level, path=["response"])

    @parametrize
    def test_raw_response_list_files(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.list_files()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = response.parse()
        assert_matches_type(ListFilesResponse, top_level, path=["response"])

    @parametrize
    def test_streaming_response_list_files(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.list_files() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = response.parse()
            assert_matches_type(ListFilesResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_list_mentions(self, client: DeeporiginData) -> None:
        top_level = client.list_mentions(
            query="query",
        )
        assert_matches_type(ListMentionsResponse, top_level, path=["response"])

    @parametrize
    def test_raw_response_list_mentions(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.list_mentions(
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = response.parse()
        assert_matches_type(ListMentionsResponse, top_level, path=["response"])

    @parametrize
    def test_streaming_response_list_mentions(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.list_mentions(
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = response.parse()
            assert_matches_type(ListMentionsResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_list_row_back_references(self, client: DeeporiginData) -> None:
        top_level = client.list_row_back_references(
            row_id="rowId",
        )
        assert_matches_type(ListRowBackReferencesResponse, top_level, path=["response"])

    @parametrize
    def test_raw_response_list_row_back_references(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.list_row_back_references(
            row_id="rowId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = response.parse()
        assert_matches_type(ListRowBackReferencesResponse, top_level, path=["response"])

    @parametrize
    def test_streaming_response_list_row_back_references(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.list_row_back_references(
            row_id="rowId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = response.parse()
            assert_matches_type(ListRowBackReferencesResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_list_rows(self, client: DeeporiginData) -> None:
        top_level = client.list_rows(
            filters=[{"parent": {"id": "id"}}, {"parent": {"id": "id"}}, {"parent": {"id": "id"}}],
        )
        assert_matches_type(ListRowsResponse, top_level, path=["response"])

    @parametrize
    def test_raw_response_list_rows(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.list_rows(
            filters=[{"parent": {"id": "id"}}, {"parent": {"id": "id"}}, {"parent": {"id": "id"}}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = response.parse()
        assert_matches_type(ListRowsResponse, top_level, path=["response"])

    @parametrize
    def test_streaming_response_list_rows(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.list_rows(
            filters=[{"parent": {"id": "id"}}, {"parent": {"id": "id"}}, {"parent": {"id": "id"}}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = response.parse()
            assert_matches_type(ListRowsResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_update_database(self, client: DeeporiginData) -> None:
        top_level = client.update_database(
            id="id",
            database={},
        )
        assert_matches_type(UpdateDatabaseResponse, top_level, path=["response"])

    @parametrize
    def test_method_update_database_with_all_params(self, client: DeeporiginData) -> None:
        top_level = client.update_database(
            id="id",
            database={
                "hid": "hid",
                "name": "name",
                "parent_id": "parentId",
                "hid_prefix": "hidPrefix",
                "editor": {},
            },
        )
        assert_matches_type(UpdateDatabaseResponse, top_level, path=["response"])

    @parametrize
    def test_raw_response_update_database(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.update_database(
            id="id",
            database={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = response.parse()
        assert_matches_type(UpdateDatabaseResponse, top_level, path=["response"])

    @parametrize
    def test_streaming_response_update_database(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.update_database(
            id="id",
            database={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = response.parse()
            assert_matches_type(UpdateDatabaseResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_update_database_column(self, client: DeeporiginData) -> None:
        top_level = client.update_database_column(
            column={"type": "boolean"},
            column_id="columnId",
        )
        assert_matches_type(UpdateDatabaseColumnResponse, top_level, path=["response"])

    @parametrize
    def test_method_update_database_column_with_all_params(self, client: DeeporiginData) -> None:
        top_level = client.update_database_column(
            column={
                "type": "boolean",
                "name": "name",
                "key": "key",
                "cardinality": "one",
                "systemType": "name",
                "isRequired": True,
                "enabledViewers": ["code", "html", "image"],
                "cellJsonSchema": {},
            },
            column_id="columnId",
        )
        assert_matches_type(UpdateDatabaseColumnResponse, top_level, path=["response"])

    @parametrize
    def test_raw_response_update_database_column(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.update_database_column(
            column={"type": "boolean"},
            column_id="columnId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = response.parse()
        assert_matches_type(UpdateDatabaseColumnResponse, top_level, path=["response"])

    @parametrize
    def test_streaming_response_update_database_column(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.update_database_column(
            column={"type": "boolean"},
            column_id="columnId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = response.parse()
            assert_matches_type(UpdateDatabaseColumnResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_update_workspace(self, client: DeeporiginData) -> None:
        top_level = client.update_workspace(
            id="id",
            workspace={},
        )
        assert_matches_type(UpdateWorkspaceResponse, top_level, path=["response"])

    @parametrize
    def test_method_update_workspace_with_all_params(self, client: DeeporiginData) -> None:
        top_level = client.update_workspace(
            id="id",
            workspace={
                "hid": "hid",
                "name": "name",
                "parent_id": "parentId",
                "editor": {},
            },
        )
        assert_matches_type(UpdateWorkspaceResponse, top_level, path=["response"])

    @parametrize
    def test_raw_response_update_workspace(self, client: DeeporiginData) -> None:
        response = client.with_raw_response.update_workspace(
            id="id",
            workspace={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = response.parse()
        assert_matches_type(UpdateWorkspaceResponse, top_level, path=["response"])

    @parametrize
    def test_streaming_response_update_workspace(self, client: DeeporiginData) -> None:
        with client.with_streaming_response.update_workspace(
            id="id",
            workspace={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = response.parse()
            assert_matches_type(UpdateWorkspaceResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncTopLevel:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_add_database_column(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.add_database_column(
            column={
                "type": "boolean",
                "name": "name",
                "key": "key",
                "cardinality": "one",
            },
            database_id="databaseId",
        )
        assert_matches_type(AddDatabaseColumnResponse, top_level, path=["response"])

    @parametrize
    async def test_method_add_database_column_with_all_params(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.add_database_column(
            column={
                "type": "boolean",
                "name": "name",
                "key": "key",
                "cardinality": "one",
                "systemType": "name",
                "isRequired": True,
                "enabledViewers": ["code", "html", "image"],
                "cellJsonSchema": {},
            },
            database_id="databaseId",
        )
        assert_matches_type(AddDatabaseColumnResponse, top_level, path=["response"])

    @parametrize
    async def test_raw_response_add_database_column(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.with_raw_response.add_database_column(
            column={
                "type": "boolean",
                "name": "name",
                "key": "key",
                "cardinality": "one",
            },
            database_id="databaseId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = await response.parse()
        assert_matches_type(AddDatabaseColumnResponse, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_add_database_column(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.with_streaming_response.add_database_column(
            column={
                "type": "boolean",
                "name": "name",
                "key": "key",
                "cardinality": "one",
            },
            database_id="databaseId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = await response.parse()
            assert_matches_type(AddDatabaseColumnResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_archive_files(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.archive_files(
            file_ids=["string", "string", "string"],
        )
        assert_matches_type(object, top_level, path=["response"])

    @parametrize
    async def test_raw_response_archive_files(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.with_raw_response.archive_files(
            file_ids=["string", "string", "string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = await response.parse()
        assert_matches_type(object, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_archive_files(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.with_streaming_response.archive_files(
            file_ids=["string", "string", "string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = await response.parse()
            assert_matches_type(object, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_configure_column_select_options(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.configure_column_select_options(
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
        assert_matches_type(ConfigureColumnSelectOptionsResponse, top_level, path=["response"])

    @parametrize
    async def test_raw_response_configure_column_select_options(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.with_raw_response.configure_column_select_options(
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
        top_level = await response.parse()
        assert_matches_type(ConfigureColumnSelectOptionsResponse, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_configure_column_select_options(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.with_streaming_response.configure_column_select_options(
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

            top_level = await response.parse()
            assert_matches_type(ConfigureColumnSelectOptionsResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_convert_id_format(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.convert_id_format(
            conversions=[{"id": "id"}, {"id": "id"}, {"id": "id"}],
        )
        assert_matches_type(ConvertIDFormatResponse, top_level, path=["response"])

    @parametrize
    async def test_raw_response_convert_id_format(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.with_raw_response.convert_id_format(
            conversions=[{"id": "id"}, {"id": "id"}, {"id": "id"}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = await response.parse()
        assert_matches_type(ConvertIDFormatResponse, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_convert_id_format(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.with_streaming_response.convert_id_format(
            conversions=[{"id": "id"}, {"id": "id"}, {"id": "id"}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = await response.parse()
            assert_matches_type(ConvertIDFormatResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_create_database(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.create_database(
            database={
                "hid": "hid",
                "name": "name",
                "hid_prefix": "hidPrefix",
            },
        )
        assert_matches_type(CreateDatabaseResponse, top_level, path=["response"])

    @parametrize
    async def test_method_create_database_with_all_params(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.create_database(
            database={
                "hid": "hid",
                "name": "name",
                "parent_id": "parentId",
                "hid_prefix": "hidPrefix",
                "cols": [{}, {}, {}],
            },
        )
        assert_matches_type(CreateDatabaseResponse, top_level, path=["response"])

    @parametrize
    async def test_raw_response_create_database(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.with_raw_response.create_database(
            database={
                "hid": "hid",
                "name": "name",
                "hid_prefix": "hidPrefix",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = await response.parse()
        assert_matches_type(CreateDatabaseResponse, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_create_database(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.with_streaming_response.create_database(
            database={
                "hid": "hid",
                "name": "name",
                "hid_prefix": "hidPrefix",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = await response.parse()
            assert_matches_type(CreateDatabaseResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_create_file_download_url(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.create_file_download_url(
            file_id="fileId",
        )
        assert_matches_type(CreateFileDownloadURLResponse, top_level, path=["response"])

    @parametrize
    async def test_raw_response_create_file_download_url(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.with_raw_response.create_file_download_url(
            file_id="fileId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = await response.parse()
        assert_matches_type(CreateFileDownloadURLResponse, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_create_file_download_url(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.with_streaming_response.create_file_download_url(
            file_id="fileId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = await response.parse()
            assert_matches_type(CreateFileDownloadURLResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_create_file_upload(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.create_file_upload(
            content_length="contentLength",
            name="name",
        )
        assert_matches_type(CreateFileUploadResponse, top_level, path=["response"])

    @parametrize
    async def test_method_create_file_upload_with_all_params(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.create_file_upload(
            content_length="contentLength",
            name="name",
            content_type="contentType",
        )
        assert_matches_type(CreateFileUploadResponse, top_level, path=["response"])

    @parametrize
    async def test_raw_response_create_file_upload(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.with_raw_response.create_file_upload(
            content_length="contentLength",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = await response.parse()
        assert_matches_type(CreateFileUploadResponse, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_create_file_upload(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.with_streaming_response.create_file_upload(
            content_length="contentLength",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = await response.parse()
            assert_matches_type(CreateFileUploadResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_create_workspace(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.create_workspace(
            workspace={
                "hid": "hid",
                "name": "name",
            },
        )
        assert_matches_type(CreateWorkspaceResponse, top_level, path=["response"])

    @parametrize
    async def test_method_create_workspace_with_all_params(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.create_workspace(
            workspace={
                "hid": "hid",
                "name": "name",
                "parent_id": "parentId",
            },
        )
        assert_matches_type(CreateWorkspaceResponse, top_level, path=["response"])

    @parametrize
    async def test_raw_response_create_workspace(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.with_raw_response.create_workspace(
            workspace={
                "hid": "hid",
                "name": "name",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = await response.parse()
        assert_matches_type(CreateWorkspaceResponse, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_create_workspace(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.with_streaming_response.create_workspace(
            workspace={
                "hid": "hid",
                "name": "name",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = await response.parse()
            assert_matches_type(CreateWorkspaceResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete_database_column(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.delete_database_column(
            column_id="columnId",
        )
        assert_matches_type(DeleteDatabaseColumnResponse, top_level, path=["response"])

    @parametrize
    async def test_raw_response_delete_database_column(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.with_raw_response.delete_database_column(
            column_id="columnId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = await response.parse()
        assert_matches_type(DeleteDatabaseColumnResponse, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_delete_database_column(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.with_streaming_response.delete_database_column(
            column_id="columnId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = await response.parse()
            assert_matches_type(DeleteDatabaseColumnResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete_rows(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.delete_rows(
            row_ids=["string", "string", "string"],
        )
        assert_matches_type(DeleteRowsResponse, top_level, path=["response"])

    @parametrize
    async def test_raw_response_delete_rows(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.with_raw_response.delete_rows(
            row_ids=["string", "string", "string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = await response.parse()
        assert_matches_type(DeleteRowsResponse, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_delete_rows(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.with_streaming_response.delete_rows(
            row_ids=["string", "string", "string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = await response.parse()
            assert_matches_type(DeleteRowsResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_describe_code_execution(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.describe_code_execution(
            id="id",
        )
        assert_matches_type(DescribeCodeExecutionResponse, top_level, path=["response"])

    @parametrize
    async def test_raw_response_describe_code_execution(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.with_raw_response.describe_code_execution(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = await response.parse()
        assert_matches_type(DescribeCodeExecutionResponse, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_describe_code_execution(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.with_streaming_response.describe_code_execution(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = await response.parse()
            assert_matches_type(DescribeCodeExecutionResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_describe_database_stats(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.describe_database_stats(
            database_id="databaseId",
        )
        assert_matches_type(DescribeDatabaseStatsResponse, top_level, path=["response"])

    @parametrize
    async def test_raw_response_describe_database_stats(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.with_raw_response.describe_database_stats(
            database_id="databaseId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = await response.parse()
        assert_matches_type(DescribeDatabaseStatsResponse, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_describe_database_stats(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.with_streaming_response.describe_database_stats(
            database_id="databaseId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = await response.parse()
            assert_matches_type(DescribeDatabaseStatsResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_describe_file(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.describe_file(
            file_id="fileId",
        )
        assert_matches_type(DescribeFileResponse, top_level, path=["response"])

    @parametrize
    async def test_raw_response_describe_file(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.with_raw_response.describe_file(
            file_id="fileId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = await response.parse()
        assert_matches_type(DescribeFileResponse, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_describe_file(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.with_streaming_response.describe_file(
            file_id="fileId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = await response.parse()
            assert_matches_type(DescribeFileResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_describe_row(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.describe_row(
            row_id="rowId",
        )
        assert_matches_type(DescribeRowResponse, top_level, path=["response"])

    @parametrize
    async def test_method_describe_row_with_all_params(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.describe_row(
            row_id="rowId",
            column_selection={
                "include": ["string"],
                "exclude": ["string"],
            },
            fields=True,
        )
        assert_matches_type(DescribeRowResponse, top_level, path=["response"])

    @parametrize
    async def test_raw_response_describe_row(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.with_raw_response.describe_row(
            row_id="rowId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = await response.parse()
        assert_matches_type(DescribeRowResponse, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_describe_row(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.with_streaming_response.describe_row(
            row_id="rowId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = await response.parse()
            assert_matches_type(DescribeRowResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_ensure_rows(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.ensure_rows(
            database_id="databaseId",
            rows=[{}],
        )
        assert_matches_type(EnsureRowsResponse, top_level, path=["response"])

    @parametrize
    async def test_raw_response_ensure_rows(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.with_raw_response.ensure_rows(
            database_id="databaseId",
            rows=[{}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = await response.parse()
        assert_matches_type(EnsureRowsResponse, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_ensure_rows(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.with_streaming_response.ensure_rows(
            database_id="databaseId",
            rows=[{}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = await response.parse()
            assert_matches_type(EnsureRowsResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_execute_code_async(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.execute_code_async(
            code="code",
            code_language="python",
        )
        assert_matches_type(ExecuteCodeAsyncResponse, top_level, path=["response"])

    @parametrize
    async def test_raw_response_execute_code_async(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.with_raw_response.execute_code_async(
            code="code",
            code_language="python",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = await response.parse()
        assert_matches_type(ExecuteCodeAsyncResponse, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_execute_code_async(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.with_streaming_response.execute_code_async(
            code="code",
            code_language="python",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = await response.parse()
            assert_matches_type(ExecuteCodeAsyncResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_execute_code_sync(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.execute_code_sync(
            code="code",
            code_language="python",
        )
        assert_matches_type(ExecuteCodeSyncResponse, top_level, path=["response"])

    @parametrize
    async def test_raw_response_execute_code_sync(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.with_raw_response.execute_code_sync(
            code="code",
            code_language="python",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = await response.parse()
        assert_matches_type(ExecuteCodeSyncResponse, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_execute_code_sync(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.with_streaming_response.execute_code_sync(
            code="code",
            code_language="python",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = await response.parse()
            assert_matches_type(ExecuteCodeSyncResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_get_code_execution_result(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.get_code_execution_result(
            id="id",
        )
        assert_matches_type(object, top_level, path=["response"])

    @parametrize
    async def test_raw_response_get_code_execution_result(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.with_raw_response.get_code_execution_result(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = await response.parse()
        assert_matches_type(object, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_get_code_execution_result(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.with_streaming_response.get_code_execution_result(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = await response.parse()
            assert_matches_type(object, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_import_rows(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.import_rows(
            database_id="databaseId",
        )
        assert_matches_type(ImportRowsResponse, top_level, path=["response"])

    @parametrize
    async def test_raw_response_import_rows(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.with_raw_response.import_rows(
            database_id="databaseId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = await response.parse()
        assert_matches_type(ImportRowsResponse, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_import_rows(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.with_streaming_response.import_rows(
            database_id="databaseId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = await response.parse()
            assert_matches_type(ImportRowsResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_initialize_org(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.initialize_org(
            body={},
        )
        assert_matches_type(InitializeOrgResponse, top_level, path=["response"])

    @parametrize
    async def test_raw_response_initialize_org(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.with_raw_response.initialize_org(
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = await response.parse()
        assert_matches_type(InitializeOrgResponse, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_initialize_org(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.with_streaming_response.initialize_org(
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = await response.parse()
            assert_matches_type(InitializeOrgResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_list_database_column_unique_values_overload_1(
        self, async_client: AsyncDeeporiginData
    ) -> None:
        top_level = await async_client.list_database_column_unique_values(
            column_id="columnId",
        )
        assert_matches_type(ListDatabaseColumnUniqueValuesResponse, top_level, path=["response"])

    @parametrize
    async def test_raw_response_list_database_column_unique_values_overload_1(
        self, async_client: AsyncDeeporiginData
    ) -> None:
        response = await async_client.with_raw_response.list_database_column_unique_values(
            column_id="columnId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = await response.parse()
        assert_matches_type(ListDatabaseColumnUniqueValuesResponse, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_list_database_column_unique_values_overload_1(
        self, async_client: AsyncDeeporiginData
    ) -> None:
        async with async_client.with_streaming_response.list_database_column_unique_values(
            column_id="columnId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = await response.parse()
            assert_matches_type(ListDatabaseColumnUniqueValuesResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_list_database_column_unique_values_overload_2(
        self, async_client: AsyncDeeporiginData
    ) -> None:
        top_level = await async_client.list_database_column_unique_values(
            database_row_id="databaseRowId",
            system_column_name="creationParentId",
        )
        assert_matches_type(ListDatabaseColumnUniqueValuesResponse, top_level, path=["response"])

    @parametrize
    async def test_raw_response_list_database_column_unique_values_overload_2(
        self, async_client: AsyncDeeporiginData
    ) -> None:
        response = await async_client.with_raw_response.list_database_column_unique_values(
            database_row_id="databaseRowId",
            system_column_name="creationParentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = await response.parse()
        assert_matches_type(ListDatabaseColumnUniqueValuesResponse, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_list_database_column_unique_values_overload_2(
        self, async_client: AsyncDeeporiginData
    ) -> None:
        async with async_client.with_streaming_response.list_database_column_unique_values(
            database_row_id="databaseRowId",
            system_column_name="creationParentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = await response.parse()
            assert_matches_type(ListDatabaseColumnUniqueValuesResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_list_database_rows(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.list_database_rows(
            database_row_id="databaseRowId",
        )
        assert_matches_type(ListDatabaseRowsResponse, top_level, path=["response"])

    @parametrize
    async def test_method_list_database_rows_with_all_params(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.list_database_rows(
            database_row_id="databaseRowId",
            column_selection={
                "include": ["string"],
                "exclude": ["string"],
            },
            creation_block_id="creationBlockId",
            creation_parent_id="creationParentId",
            filter={
                "filter_type": "text",
                "column_id": "columnId",
                "operator": "equals",
                "filter_value": "filterValue",
            },
        )
        assert_matches_type(ListDatabaseRowsResponse, top_level, path=["response"])

    @parametrize
    async def test_raw_response_list_database_rows(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.with_raw_response.list_database_rows(
            database_row_id="databaseRowId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = await response.parse()
        assert_matches_type(ListDatabaseRowsResponse, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_list_database_rows(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.with_streaming_response.list_database_rows(
            database_row_id="databaseRowId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = await response.parse()
            assert_matches_type(ListDatabaseRowsResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_list_files(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.list_files()
        assert_matches_type(ListFilesResponse, top_level, path=["response"])

    @parametrize
    async def test_method_list_files_with_all_params(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.list_files(
            filters=[
                {
                    "assigned_row_ids": ["string", "string", "string"],
                    "is_unassigned": True,
                },
                {
                    "assigned_row_ids": ["string", "string", "string"],
                    "is_unassigned": True,
                },
                {
                    "assigned_row_ids": ["string", "string", "string"],
                    "is_unassigned": True,
                },
            ],
        )
        assert_matches_type(ListFilesResponse, top_level, path=["response"])

    @parametrize
    async def test_raw_response_list_files(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.with_raw_response.list_files()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = await response.parse()
        assert_matches_type(ListFilesResponse, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_list_files(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.with_streaming_response.list_files() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = await response.parse()
            assert_matches_type(ListFilesResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_list_mentions(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.list_mentions(
            query="query",
        )
        assert_matches_type(ListMentionsResponse, top_level, path=["response"])

    @parametrize
    async def test_raw_response_list_mentions(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.with_raw_response.list_mentions(
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = await response.parse()
        assert_matches_type(ListMentionsResponse, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_list_mentions(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.with_streaming_response.list_mentions(
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = await response.parse()
            assert_matches_type(ListMentionsResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_list_row_back_references(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.list_row_back_references(
            row_id="rowId",
        )
        assert_matches_type(ListRowBackReferencesResponse, top_level, path=["response"])

    @parametrize
    async def test_raw_response_list_row_back_references(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.with_raw_response.list_row_back_references(
            row_id="rowId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = await response.parse()
        assert_matches_type(ListRowBackReferencesResponse, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_list_row_back_references(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.with_streaming_response.list_row_back_references(
            row_id="rowId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = await response.parse()
            assert_matches_type(ListRowBackReferencesResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_list_rows(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.list_rows(
            filters=[{"parent": {"id": "id"}}, {"parent": {"id": "id"}}, {"parent": {"id": "id"}}],
        )
        assert_matches_type(ListRowsResponse, top_level, path=["response"])

    @parametrize
    async def test_raw_response_list_rows(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.with_raw_response.list_rows(
            filters=[{"parent": {"id": "id"}}, {"parent": {"id": "id"}}, {"parent": {"id": "id"}}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = await response.parse()
        assert_matches_type(ListRowsResponse, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_list_rows(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.with_streaming_response.list_rows(
            filters=[{"parent": {"id": "id"}}, {"parent": {"id": "id"}}, {"parent": {"id": "id"}}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = await response.parse()
            assert_matches_type(ListRowsResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_update_database(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.update_database(
            id="id",
            database={},
        )
        assert_matches_type(UpdateDatabaseResponse, top_level, path=["response"])

    @parametrize
    async def test_method_update_database_with_all_params(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.update_database(
            id="id",
            database={
                "hid": "hid",
                "name": "name",
                "parent_id": "parentId",
                "hid_prefix": "hidPrefix",
                "editor": {},
            },
        )
        assert_matches_type(UpdateDatabaseResponse, top_level, path=["response"])

    @parametrize
    async def test_raw_response_update_database(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.with_raw_response.update_database(
            id="id",
            database={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = await response.parse()
        assert_matches_type(UpdateDatabaseResponse, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_update_database(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.with_streaming_response.update_database(
            id="id",
            database={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = await response.parse()
            assert_matches_type(UpdateDatabaseResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_update_database_column(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.update_database_column(
            column={"type": "boolean"},
            column_id="columnId",
        )
        assert_matches_type(UpdateDatabaseColumnResponse, top_level, path=["response"])

    @parametrize
    async def test_method_update_database_column_with_all_params(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.update_database_column(
            column={
                "type": "boolean",
                "name": "name",
                "key": "key",
                "cardinality": "one",
                "systemType": "name",
                "isRequired": True,
                "enabledViewers": ["code", "html", "image"],
                "cellJsonSchema": {},
            },
            column_id="columnId",
        )
        assert_matches_type(UpdateDatabaseColumnResponse, top_level, path=["response"])

    @parametrize
    async def test_raw_response_update_database_column(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.with_raw_response.update_database_column(
            column={"type": "boolean"},
            column_id="columnId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = await response.parse()
        assert_matches_type(UpdateDatabaseColumnResponse, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_update_database_column(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.with_streaming_response.update_database_column(
            column={"type": "boolean"},
            column_id="columnId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = await response.parse()
            assert_matches_type(UpdateDatabaseColumnResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_update_workspace(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.update_workspace(
            id="id",
            workspace={},
        )
        assert_matches_type(UpdateWorkspaceResponse, top_level, path=["response"])

    @parametrize
    async def test_method_update_workspace_with_all_params(self, async_client: AsyncDeeporiginData) -> None:
        top_level = await async_client.update_workspace(
            id="id",
            workspace={
                "hid": "hid",
                "name": "name",
                "parent_id": "parentId",
                "editor": {},
            },
        )
        assert_matches_type(UpdateWorkspaceResponse, top_level, path=["response"])

    @parametrize
    async def test_raw_response_update_workspace(self, async_client: AsyncDeeporiginData) -> None:
        response = await async_client.with_raw_response.update_workspace(
            id="id",
            workspace={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        top_level = await response.parse()
        assert_matches_type(UpdateWorkspaceResponse, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_update_workspace(self, async_client: AsyncDeeporiginData) -> None:
        async with async_client.with_streaming_response.update_workspace(
            id="id",
            workspace={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            top_level = await response.parse()
            assert_matches_type(UpdateWorkspaceResponse, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True
