# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, List, Union, Mapping, Iterable, overload
from typing_extensions import Self, Literal, override

import httpx

from . import resources, _exceptions
from ._qs import Querystring
from .types import (
    top_level_list_rows_params,
    top_level_list_files_params,
    top_level_delete_rows_params,
    top_level_ensure_rows_params,
    top_level_import_rows_params,
    top_level_describe_row_params,
    top_level_archive_files_params,
    top_level_describe_file_params,
    top_level_list_mentions_params,
    top_level_initialize_org_params,
    top_level_create_database_params,
    top_level_update_database_params,
    top_level_create_workspace_params,
    top_level_update_workspace_params,
    top_level_convert_id_format_params,
    top_level_execute_code_sync_params,
    top_level_create_file_upload_params,
    top_level_execute_code_async_params,
    top_level_list_database_rows_params,
    top_level_add_database_column_params,
    top_level_delete_database_column_params,
    top_level_update_database_column_params,
    top_level_describe_code_execution_params,
    top_level_describe_database_stats_params,
    top_level_create_file_download_url_params,
    top_level_list_row_back_references_params,
    top_level_get_code_execution_result_params,
    top_level_configure_column_select_options_params,
    top_level_list_database_column_unique_values_params,
)
from ._types import (
    NOT_GIVEN,
    Body,
    Omit,
    Query,
    Headers,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
)
from ._utils import (
    is_given,
    required_args,
    maybe_transform,
    get_async_library,
    async_maybe_transform,
)
from ._version import __version__
from ._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import APIStatusError, DeeporiginDataError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
    make_request_options,
)
from .types.list_rows_response import ListRowsResponse
from .types.list_files_response import ListFilesResponse
from .types.delete_rows_response import DeleteRowsResponse
from .types.ensure_rows_response import EnsureRowsResponse
from .types.import_rows_response import ImportRowsResponse
from .types.describe_row_response import DescribeRowResponse
from .types.describe_file_response import DescribeFileResponse
from .types.list_mentions_response import ListMentionsResponse
from .types.initialize_org_response import InitializeOrgResponse
from .types.create_database_response import CreateDatabaseResponse
from .types.update_database_response import UpdateDatabaseResponse
from .types.create_workspace_response import CreateWorkspaceResponse
from .types.update_workspace_response import UpdateWorkspaceResponse
from .types.convert_id_format_response import ConvertIDFormatResponse
from .types.execute_code_sync_response import ExecuteCodeSyncResponse
from .types.create_file_upload_response import CreateFileUploadResponse
from .types.execute_code_async_response import ExecuteCodeAsyncResponse
from .types.list_database_rows_response import ListDatabaseRowsResponse
from .types.add_database_column_response import AddDatabaseColumnResponse
from .types.delete_database_column_response import DeleteDatabaseColumnResponse
from .types.update_database_column_response import UpdateDatabaseColumnResponse
from .types.describe_code_execution_response import DescribeCodeExecutionResponse
from .types.describe_database_stats_response import DescribeDatabaseStatsResponse
from .types.create_file_download_url_response import CreateFileDownloadURLResponse
from .types.list_row_back_references_response import ListRowBackReferencesResponse
from .types.configure_column_select_options_response import ConfigureColumnSelectOptionsResponse
from .types.list_database_column_unique_values_response import ListDatabaseColumnUniqueValuesResponse

__all__ = [
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "resources",
    "DeeporiginData",
    "AsyncDeeporiginData",
    "Client",
    "AsyncClient",
]


class DeeporiginData(SyncAPIClient):
    with_raw_response: DeeporiginDataWithRawResponse
    with_streaming_response: DeeporiginDataWithStreamedResponse

    # client options
    token: str
    org_id: str

    def __init__(
        self,
        *,
        token: str | None = None,
        org_id: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous deeporigin_data client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `token` from `ORG_BEARER_TOKEN`
        - `org_id` from `ORG_ID`
        """
        if token is None:
            token = os.environ.get("ORG_BEARER_TOKEN")
        if token is None:
            raise DeeporiginDataError(
                "The token client option must be set either by passing token to the client or by setting the ORG_BEARER_TOKEN environment variable"
            )
        self.token = token

        if org_id is None:
            org_id = os.environ.get("ORG_ID")
        if org_id is None:
            raise DeeporiginDataError(
                "The org_id client option must be set either by passing org_id to the client or by setting the ORG_ID environment variable"
            )
        self.org_id = org_id

        if base_url is None:
            base_url = os.environ.get("DEEPORIGIN_DATA_BASE_URL")
        if base_url is None:
            base_url = f"https://os.edge.deeporigin.io/nucleus-api/api"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.with_raw_response = DeeporiginDataWithRawResponse(self)
        self.with_streaming_response = DeeporiginDataWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        token = self.token
        return {"Authorization": f"Bearer {token}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            "x-org-id": self.org_id,
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        token: str | None = None,
        org_id: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            token=token or self.token,
            org_id=org_id or self.org_id,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    def add_database_column(
        self,
        *,
        column: top_level_add_database_column_params.Column,
        database_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AddDatabaseColumnResponse:
        """
        Add a column to a database.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/AddDatabaseColumn",
            body=maybe_transform(
                {
                    "column": column,
                    "database_id": database_id,
                },
                top_level_add_database_column_params.TopLevelAddDatabaseColumnParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AddDatabaseColumnResponse,
        )

    def archive_files(
        self,
        *,
        file_ids: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Archive files by their ids.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/ArchiveFiles",
            body=maybe_transform({"file_ids": file_ids}, top_level_archive_files_params.TopLevelArchiveFilesParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def configure_column_select_options(
        self,
        *,
        column_id: str,
        option_configuration: Iterable[top_level_configure_column_select_options_params.OptionConfiguration],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ConfigureColumnSelectOptionsResponse:
        """Configure column select options.

        Supports both adding and removing options.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/ConfigureColumnSelectOptions",
            body=maybe_transform(
                {
                    "column_id": column_id,
                    "option_configuration": option_configuration,
                },
                top_level_configure_column_select_options_params.TopLevelConfigureColumnSelectOptionsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConfigureColumnSelectOptionsResponse,
        )

    def convert_id_format(
        self,
        *,
        conversions: Iterable[top_level_convert_id_format_params.Conversion],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ConvertIDFormatResponse:
        """
        Converts between system IDs and human IDs (HIDs).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/ConvertIdFormat",
            body=maybe_transform(
                {"conversions": conversions}, top_level_convert_id_format_params.TopLevelConvertIDFormatParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConvertIDFormatResponse,
        )

    def create_database(
        self,
        *,
        database: top_level_create_database_params.Database,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CreateDatabaseResponse:
        """
        Create a new database.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/CreateDatabase",
            body=maybe_transform({"database": database}, top_level_create_database_params.TopLevelCreateDatabaseParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CreateDatabaseResponse,
        )

    def create_file_download_url(
        self,
        *,
        file_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CreateFileDownloadURLResponse:
        """
        Returns a pre-signed S3 URL.

        Args:
          file_id: Deep Origin system ID.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/CreateFileDownloadUrl",
            body=maybe_transform(
                {"file_id": file_id}, top_level_create_file_download_url_params.TopLevelCreateFileDownloadURLParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CreateFileDownloadURLResponse,
        )

    def create_file_upload(
        self,
        *,
        content_length: str,
        name: str,
        content_type: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CreateFileUploadResponse:
        """Create a file upload URL.

        Typically this is creating a pre-signed S3 URL.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/CreateFileUpload",
            body=maybe_transform(
                {
                    "content_length": content_length,
                    "name": name,
                    "content_type": content_type,
                },
                top_level_create_file_upload_params.TopLevelCreateFileUploadParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CreateFileUploadResponse,
        )

    def create_workspace(
        self,
        *,
        workspace: top_level_create_workspace_params.Workspace,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CreateWorkspaceResponse:
        """
        Create a new workspace.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/CreateWorkspace",
            body=maybe_transform(
                {"workspace": workspace}, top_level_create_workspace_params.TopLevelCreateWorkspaceParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CreateWorkspaceResponse,
        )

    def delete_database_column(
        self,
        *,
        column_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeleteDatabaseColumnResponse:
        """
        Delete a column from a database.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/DeleteDatabaseColumn",
            body=maybe_transform(
                {"column_id": column_id}, top_level_delete_database_column_params.TopLevelDeleteDatabaseColumnParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteDatabaseColumnResponse,
        )

    def delete_rows(
        self,
        *,
        row_ids: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeleteRowsResponse:
        """
        Delete rows by their ids.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/DeleteRows",
            body=maybe_transform({"row_ids": row_ids}, top_level_delete_rows_params.TopLevelDeleteRowsParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteRowsResponse,
        )

    def describe_code_execution(
        self,
        *,
        id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DescribeCodeExecutionResponse:
        """
        Returns information about a particular code execution.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/DescribeCodeExecution",
            body=maybe_transform(
                {"id": id}, top_level_describe_code_execution_params.TopLevelDescribeCodeExecutionParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DescribeCodeExecutionResponse,
        )

    def describe_database_stats(
        self,
        *,
        database_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DescribeDatabaseStatsResponse:
        """
        Returns aggregation information about a particular database.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/DescribeDatabaseStats",
            body=maybe_transform(
                {"database_id": database_id},
                top_level_describe_database_stats_params.TopLevelDescribeDatabaseStatsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DescribeDatabaseStatsResponse,
        )

    def describe_file(
        self,
        *,
        file_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DescribeFileResponse:
        """
        Describe a file by its ID.

        Args:
          file_id: Deep Origin system ID.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/DescribeFile",
            body=maybe_transform({"file_id": file_id}, top_level_describe_file_params.TopLevelDescribeFileParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DescribeFileResponse,
        )

    def describe_row(
        self,
        *,
        row_id: str,
        column_selection: top_level_describe_row_params.ColumnSelection | NotGiven = NOT_GIVEN,
        fields: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DescribeRowResponse:
        """
        Describe a row

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/DescribeRow",
            body=maybe_transform(
                {
                    "row_id": row_id,
                    "column_selection": column_selection,
                    "fields": fields,
                },
                top_level_describe_row_params.TopLevelDescribeRowParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DescribeRowResponse,
        )

    def ensure_rows(
        self,
        *,
        database_id: str,
        rows: Iterable[top_level_ensure_rows_params.Row],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EnsureRowsResponse:
        """Either creates or updates an existing row.

        Supports updates to both system and
        user defined columns.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/EnsureRows",
            body=maybe_transform(
                {
                    "database_id": database_id,
                    "rows": rows,
                },
                top_level_ensure_rows_params.TopLevelEnsureRowsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EnsureRowsResponse,
        )

    def execute_code_async(
        self,
        *,
        code: str,
        code_language: Literal["python"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ExecuteCodeAsyncResponse:
        """
        Execute code asynchronously.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/ExecuteCode",
            body=maybe_transform(
                {
                    "code": code,
                    "code_language": code_language,
                },
                top_level_execute_code_async_params.TopLevelExecuteCodeAsyncParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExecuteCodeAsyncResponse,
        )

    def execute_code_sync(
        self,
        *,
        code: str,
        code_language: Literal["python"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ExecuteCodeSyncResponse:
        """
        Execute code synchronously.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/ExecuteCodeSync",
            body=maybe_transform(
                {
                    "code": code,
                    "code_language": code_language,
                },
                top_level_execute_code_sync_params.TopLevelExecuteCodeSyncParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExecuteCodeSyncResponse,
        )

    def get_code_execution_result(
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
        return self.post(
            "/GetCodeExecutionResult",
            body=maybe_transform(
                {"id": id}, top_level_get_code_execution_result_params.TopLevelGetCodeExecutionResultParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def import_rows(
        self,
        *,
        database_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ImportRowsResponse:
        """
        Creates new rows from CSV data.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/ImportRows",
            body=maybe_transform({"database_id": database_id}, top_level_import_rows_params.TopLevelImportRowsParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ImportRowsResponse,
        )

    def initialize_org(
        self,
        *,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InitializeOrgResponse:
        """
        Initialize an organization.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/InitializeOrg",
            body=maybe_transform(body, top_level_initialize_org_params.TopLevelInitializeOrgParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InitializeOrgResponse,
        )

    @overload
    def list_database_column_unique_values(
        self,
        *,
        column_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ListDatabaseColumnUniqueValuesResponse:
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
    def list_database_column_unique_values(
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
    ) -> ListDatabaseColumnUniqueValuesResponse:
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
    def list_database_column_unique_values(
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
    ) -> ListDatabaseColumnUniqueValuesResponse:
        return self.post(
            "/ListDatabaseColumnUniqueValues",
            body=maybe_transform(
                {
                    "column_id": column_id,
                    "database_row_id": database_row_id,
                    "system_column_name": system_column_name,
                },
                top_level_list_database_column_unique_values_params.TopLevelListDatabaseColumnUniqueValuesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ListDatabaseColumnUniqueValuesResponse,
        )

    def list_database_rows(
        self,
        *,
        database_row_id: str,
        column_selection: top_level_list_database_rows_params.ColumnSelection | NotGiven = NOT_GIVEN,
        creation_block_id: str | NotGiven = NOT_GIVEN,
        creation_parent_id: str | NotGiven = NOT_GIVEN,
        filter: top_level_list_database_rows_params.Filter | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ListDatabaseRowsResponse:
        """
        List database rows with full row data.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/ListDatabaseRows",
            body=maybe_transform(
                {
                    "database_row_id": database_row_id,
                    "column_selection": column_selection,
                    "creation_block_id": creation_block_id,
                    "creation_parent_id": creation_parent_id,
                    "filter": filter,
                },
                top_level_list_database_rows_params.TopLevelListDatabaseRowsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ListDatabaseRowsResponse,
        )

    def list_files(
        self,
        *,
        filters: Iterable[top_level_list_files_params.Filter] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ListFilesResponse:
        """
        Returns a list of files using the filters.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/ListFiles",
            body=maybe_transform({"filters": filters}, top_level_list_files_params.TopLevelListFilesParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ListFilesResponse,
        )

    def list_mentions(
        self,
        *,
        query: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ListMentionsResponse:
        """
        Returns entities that can be mentioned in a body document.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/ListMentions",
            body=maybe_transform({"query": query}, top_level_list_mentions_params.TopLevelListMentionsParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ListMentionsResponse,
        )

    def list_row_back_references(
        self,
        *,
        row_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ListRowBackReferencesResponse:
        """
        Finds all the places a row is referenced.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/ListRowBackReferences",
            body=maybe_transform(
                {"row_id": row_id}, top_level_list_row_back_references_params.TopLevelListRowBackReferencesParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ListRowBackReferencesResponse,
        )

    def list_rows(
        self,
        *,
        filters: Iterable[top_level_list_rows_params.Filter],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ListRowsResponse:
        """
        Lists rows at a given depth in the hierarchy.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/ListRows",
            body=maybe_transform({"filters": filters}, top_level_list_rows_params.TopLevelListRowsParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ListRowsResponse,
        )

    def update_database(
        self,
        *,
        id: str,
        database: top_level_update_database_params.Database,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UpdateDatabaseResponse:
        """
        Update a database.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/UpdateDatabase",
            body=maybe_transform(
                {
                    "id": id,
                    "database": database,
                },
                top_level_update_database_params.TopLevelUpdateDatabaseParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UpdateDatabaseResponse,
        )

    def update_database_column(
        self,
        *,
        column: top_level_update_database_column_params.Column,
        column_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UpdateDatabaseColumnResponse:
        """
        Update a column in a database.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/UpdateDatabaseColumn",
            body=maybe_transform(
                {
                    "column": column,
                    "column_id": column_id,
                },
                top_level_update_database_column_params.TopLevelUpdateDatabaseColumnParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UpdateDatabaseColumnResponse,
        )

    def update_workspace(
        self,
        *,
        id: str,
        workspace: top_level_update_workspace_params.Workspace,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UpdateWorkspaceResponse:
        """
        Update a workspace.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/UpdateWorkspace",
            body=maybe_transform(
                {
                    "id": id,
                    "workspace": workspace,
                },
                top_level_update_workspace_params.TopLevelUpdateWorkspaceParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UpdateWorkspaceResponse,
        )

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncDeeporiginData(AsyncAPIClient):
    with_raw_response: AsyncDeeporiginDataWithRawResponse
    with_streaming_response: AsyncDeeporiginDataWithStreamedResponse

    # client options
    token: str
    org_id: str

    def __init__(
        self,
        *,
        token: str | None = None,
        org_id: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async deeporigin_data client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `token` from `ORG_BEARER_TOKEN`
        - `org_id` from `ORG_ID`
        """
        if token is None:
            token = os.environ.get("ORG_BEARER_TOKEN")
        if token is None:
            raise DeeporiginDataError(
                "The token client option must be set either by passing token to the client or by setting the ORG_BEARER_TOKEN environment variable"
            )
        self.token = token

        if org_id is None:
            org_id = os.environ.get("ORG_ID")
        if org_id is None:
            raise DeeporiginDataError(
                "The org_id client option must be set either by passing org_id to the client or by setting the ORG_ID environment variable"
            )
        self.org_id = org_id

        if base_url is None:
            base_url = os.environ.get("DEEPORIGIN_DATA_BASE_URL")
        if base_url is None:
            base_url = f"https://os.edge.deeporigin.io/nucleus-api/api"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.with_raw_response = AsyncDeeporiginDataWithRawResponse(self)
        self.with_streaming_response = AsyncDeeporiginDataWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        token = self.token
        return {"Authorization": f"Bearer {token}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            "x-org-id": self.org_id,
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        token: str | None = None,
        org_id: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            token=token or self.token,
            org_id=org_id or self.org_id,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    async def add_database_column(
        self,
        *,
        column: top_level_add_database_column_params.Column,
        database_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AddDatabaseColumnResponse:
        """
        Add a column to a database.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/AddDatabaseColumn",
            body=await async_maybe_transform(
                {
                    "column": column,
                    "database_id": database_id,
                },
                top_level_add_database_column_params.TopLevelAddDatabaseColumnParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AddDatabaseColumnResponse,
        )

    async def archive_files(
        self,
        *,
        file_ids: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Archive files by their ids.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/ArchiveFiles",
            body=await async_maybe_transform(
                {"file_ids": file_ids}, top_level_archive_files_params.TopLevelArchiveFilesParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def configure_column_select_options(
        self,
        *,
        column_id: str,
        option_configuration: Iterable[top_level_configure_column_select_options_params.OptionConfiguration],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ConfigureColumnSelectOptionsResponse:
        """Configure column select options.

        Supports both adding and removing options.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/ConfigureColumnSelectOptions",
            body=await async_maybe_transform(
                {
                    "column_id": column_id,
                    "option_configuration": option_configuration,
                },
                top_level_configure_column_select_options_params.TopLevelConfigureColumnSelectOptionsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConfigureColumnSelectOptionsResponse,
        )

    async def convert_id_format(
        self,
        *,
        conversions: Iterable[top_level_convert_id_format_params.Conversion],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ConvertIDFormatResponse:
        """
        Converts between system IDs and human IDs (HIDs).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/ConvertIdFormat",
            body=await async_maybe_transform(
                {"conversions": conversions}, top_level_convert_id_format_params.TopLevelConvertIDFormatParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConvertIDFormatResponse,
        )

    async def create_database(
        self,
        *,
        database: top_level_create_database_params.Database,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CreateDatabaseResponse:
        """
        Create a new database.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/CreateDatabase",
            body=await async_maybe_transform(
                {"database": database}, top_level_create_database_params.TopLevelCreateDatabaseParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CreateDatabaseResponse,
        )

    async def create_file_download_url(
        self,
        *,
        file_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CreateFileDownloadURLResponse:
        """
        Returns a pre-signed S3 URL.

        Args:
          file_id: Deep Origin system ID.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/CreateFileDownloadUrl",
            body=await async_maybe_transform(
                {"file_id": file_id}, top_level_create_file_download_url_params.TopLevelCreateFileDownloadURLParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CreateFileDownloadURLResponse,
        )

    async def create_file_upload(
        self,
        *,
        content_length: str,
        name: str,
        content_type: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CreateFileUploadResponse:
        """Create a file upload URL.

        Typically this is creating a pre-signed S3 URL.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/CreateFileUpload",
            body=await async_maybe_transform(
                {
                    "content_length": content_length,
                    "name": name,
                    "content_type": content_type,
                },
                top_level_create_file_upload_params.TopLevelCreateFileUploadParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CreateFileUploadResponse,
        )

    async def create_workspace(
        self,
        *,
        workspace: top_level_create_workspace_params.Workspace,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CreateWorkspaceResponse:
        """
        Create a new workspace.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/CreateWorkspace",
            body=await async_maybe_transform(
                {"workspace": workspace}, top_level_create_workspace_params.TopLevelCreateWorkspaceParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CreateWorkspaceResponse,
        )

    async def delete_database_column(
        self,
        *,
        column_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeleteDatabaseColumnResponse:
        """
        Delete a column from a database.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/DeleteDatabaseColumn",
            body=await async_maybe_transform(
                {"column_id": column_id}, top_level_delete_database_column_params.TopLevelDeleteDatabaseColumnParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteDatabaseColumnResponse,
        )

    async def delete_rows(
        self,
        *,
        row_ids: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeleteRowsResponse:
        """
        Delete rows by their ids.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/DeleteRows",
            body=await async_maybe_transform(
                {"row_ids": row_ids}, top_level_delete_rows_params.TopLevelDeleteRowsParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteRowsResponse,
        )

    async def describe_code_execution(
        self,
        *,
        id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DescribeCodeExecutionResponse:
        """
        Returns information about a particular code execution.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/DescribeCodeExecution",
            body=await async_maybe_transform(
                {"id": id}, top_level_describe_code_execution_params.TopLevelDescribeCodeExecutionParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DescribeCodeExecutionResponse,
        )

    async def describe_database_stats(
        self,
        *,
        database_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DescribeDatabaseStatsResponse:
        """
        Returns aggregation information about a particular database.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/DescribeDatabaseStats",
            body=await async_maybe_transform(
                {"database_id": database_id},
                top_level_describe_database_stats_params.TopLevelDescribeDatabaseStatsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DescribeDatabaseStatsResponse,
        )

    async def describe_file(
        self,
        *,
        file_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DescribeFileResponse:
        """
        Describe a file by its ID.

        Args:
          file_id: Deep Origin system ID.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/DescribeFile",
            body=await async_maybe_transform(
                {"file_id": file_id}, top_level_describe_file_params.TopLevelDescribeFileParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DescribeFileResponse,
        )

    async def describe_row(
        self,
        *,
        row_id: str,
        column_selection: top_level_describe_row_params.ColumnSelection | NotGiven = NOT_GIVEN,
        fields: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DescribeRowResponse:
        """
        Describe a row

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/DescribeRow",
            body=await async_maybe_transform(
                {
                    "row_id": row_id,
                    "column_selection": column_selection,
                    "fields": fields,
                },
                top_level_describe_row_params.TopLevelDescribeRowParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DescribeRowResponse,
        )

    async def ensure_rows(
        self,
        *,
        database_id: str,
        rows: Iterable[top_level_ensure_rows_params.Row],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EnsureRowsResponse:
        """Either creates or updates an existing row.

        Supports updates to both system and
        user defined columns.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/EnsureRows",
            body=await async_maybe_transform(
                {
                    "database_id": database_id,
                    "rows": rows,
                },
                top_level_ensure_rows_params.TopLevelEnsureRowsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EnsureRowsResponse,
        )

    async def execute_code_async(
        self,
        *,
        code: str,
        code_language: Literal["python"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ExecuteCodeAsyncResponse:
        """
        Execute code asynchronously.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/ExecuteCode",
            body=await async_maybe_transform(
                {
                    "code": code,
                    "code_language": code_language,
                },
                top_level_execute_code_async_params.TopLevelExecuteCodeAsyncParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExecuteCodeAsyncResponse,
        )

    async def execute_code_sync(
        self,
        *,
        code: str,
        code_language: Literal["python"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ExecuteCodeSyncResponse:
        """
        Execute code synchronously.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/ExecuteCodeSync",
            body=await async_maybe_transform(
                {
                    "code": code,
                    "code_language": code_language,
                },
                top_level_execute_code_sync_params.TopLevelExecuteCodeSyncParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExecuteCodeSyncResponse,
        )

    async def get_code_execution_result(
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
        return await self.post(
            "/GetCodeExecutionResult",
            body=await async_maybe_transform(
                {"id": id}, top_level_get_code_execution_result_params.TopLevelGetCodeExecutionResultParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def import_rows(
        self,
        *,
        database_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ImportRowsResponse:
        """
        Creates new rows from CSV data.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/ImportRows",
            body=await async_maybe_transform(
                {"database_id": database_id}, top_level_import_rows_params.TopLevelImportRowsParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ImportRowsResponse,
        )

    async def initialize_org(
        self,
        *,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InitializeOrgResponse:
        """
        Initialize an organization.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/InitializeOrg",
            body=await async_maybe_transform(body, top_level_initialize_org_params.TopLevelInitializeOrgParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InitializeOrgResponse,
        )

    @overload
    async def list_database_column_unique_values(
        self,
        *,
        column_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ListDatabaseColumnUniqueValuesResponse:
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
    async def list_database_column_unique_values(
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
    ) -> ListDatabaseColumnUniqueValuesResponse:
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
    async def list_database_column_unique_values(
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
    ) -> ListDatabaseColumnUniqueValuesResponse:
        return await self.post(
            "/ListDatabaseColumnUniqueValues",
            body=await async_maybe_transform(
                {
                    "column_id": column_id,
                    "database_row_id": database_row_id,
                    "system_column_name": system_column_name,
                },
                top_level_list_database_column_unique_values_params.TopLevelListDatabaseColumnUniqueValuesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ListDatabaseColumnUniqueValuesResponse,
        )

    async def list_database_rows(
        self,
        *,
        database_row_id: str,
        column_selection: top_level_list_database_rows_params.ColumnSelection | NotGiven = NOT_GIVEN,
        creation_block_id: str | NotGiven = NOT_GIVEN,
        creation_parent_id: str | NotGiven = NOT_GIVEN,
        filter: top_level_list_database_rows_params.Filter | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ListDatabaseRowsResponse:
        """
        List database rows with full row data.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/ListDatabaseRows",
            body=await async_maybe_transform(
                {
                    "database_row_id": database_row_id,
                    "column_selection": column_selection,
                    "creation_block_id": creation_block_id,
                    "creation_parent_id": creation_parent_id,
                    "filter": filter,
                },
                top_level_list_database_rows_params.TopLevelListDatabaseRowsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ListDatabaseRowsResponse,
        )

    async def list_files(
        self,
        *,
        filters: Iterable[top_level_list_files_params.Filter] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ListFilesResponse:
        """
        Returns a list of files using the filters.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/ListFiles",
            body=await async_maybe_transform({"filters": filters}, top_level_list_files_params.TopLevelListFilesParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ListFilesResponse,
        )

    async def list_mentions(
        self,
        *,
        query: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ListMentionsResponse:
        """
        Returns entities that can be mentioned in a body document.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/ListMentions",
            body=await async_maybe_transform(
                {"query": query}, top_level_list_mentions_params.TopLevelListMentionsParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ListMentionsResponse,
        )

    async def list_row_back_references(
        self,
        *,
        row_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ListRowBackReferencesResponse:
        """
        Finds all the places a row is referenced.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/ListRowBackReferences",
            body=await async_maybe_transform(
                {"row_id": row_id}, top_level_list_row_back_references_params.TopLevelListRowBackReferencesParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ListRowBackReferencesResponse,
        )

    async def list_rows(
        self,
        *,
        filters: Iterable[top_level_list_rows_params.Filter],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ListRowsResponse:
        """
        Lists rows at a given depth in the hierarchy.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/ListRows",
            body=await async_maybe_transform({"filters": filters}, top_level_list_rows_params.TopLevelListRowsParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ListRowsResponse,
        )

    async def update_database(
        self,
        *,
        id: str,
        database: top_level_update_database_params.Database,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UpdateDatabaseResponse:
        """
        Update a database.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/UpdateDatabase",
            body=await async_maybe_transform(
                {
                    "id": id,
                    "database": database,
                },
                top_level_update_database_params.TopLevelUpdateDatabaseParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UpdateDatabaseResponse,
        )

    async def update_database_column(
        self,
        *,
        column: top_level_update_database_column_params.Column,
        column_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UpdateDatabaseColumnResponse:
        """
        Update a column in a database.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/UpdateDatabaseColumn",
            body=await async_maybe_transform(
                {
                    "column": column,
                    "column_id": column_id,
                },
                top_level_update_database_column_params.TopLevelUpdateDatabaseColumnParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UpdateDatabaseColumnResponse,
        )

    async def update_workspace(
        self,
        *,
        id: str,
        workspace: top_level_update_workspace_params.Workspace,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UpdateWorkspaceResponse:
        """
        Update a workspace.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/UpdateWorkspace",
            body=await async_maybe_transform(
                {
                    "id": id,
                    "workspace": workspace,
                },
                top_level_update_workspace_params.TopLevelUpdateWorkspaceParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UpdateWorkspaceResponse,
        )

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class DeeporiginDataWithRawResponse:
    def __init__(self, client: DeeporiginData) -> None:
        self.add_database_column = to_raw_response_wrapper(
            client.add_database_column,
        )
        self.archive_files = to_raw_response_wrapper(
            client.archive_files,
        )
        self.configure_column_select_options = to_raw_response_wrapper(
            client.configure_column_select_options,
        )
        self.convert_id_format = to_raw_response_wrapper(
            client.convert_id_format,
        )
        self.create_database = to_raw_response_wrapper(
            client.create_database,
        )
        self.create_file_download_url = to_raw_response_wrapper(
            client.create_file_download_url,
        )
        self.create_file_upload = to_raw_response_wrapper(
            client.create_file_upload,
        )
        self.create_workspace = to_raw_response_wrapper(
            client.create_workspace,
        )
        self.delete_database_column = to_raw_response_wrapper(
            client.delete_database_column,
        )
        self.delete_rows = to_raw_response_wrapper(
            client.delete_rows,
        )
        self.describe_code_execution = to_raw_response_wrapper(
            client.describe_code_execution,
        )
        self.describe_database_stats = to_raw_response_wrapper(
            client.describe_database_stats,
        )
        self.describe_file = to_raw_response_wrapper(
            client.describe_file,
        )
        self.describe_row = to_raw_response_wrapper(
            client.describe_row,
        )
        self.ensure_rows = to_raw_response_wrapper(
            client.ensure_rows,
        )
        self.execute_code_async = to_raw_response_wrapper(
            client.execute_code_async,
        )
        self.execute_code_sync = to_raw_response_wrapper(
            client.execute_code_sync,
        )
        self.get_code_execution_result = to_raw_response_wrapper(
            client.get_code_execution_result,
        )
        self.import_rows = to_raw_response_wrapper(
            client.import_rows,
        )
        self.initialize_org = to_raw_response_wrapper(
            client.initialize_org,
        )
        self.list_database_column_unique_values = to_raw_response_wrapper(
            client.list_database_column_unique_values,
        )
        self.list_database_rows = to_raw_response_wrapper(
            client.list_database_rows,
        )
        self.list_files = to_raw_response_wrapper(
            client.list_files,
        )
        self.list_mentions = to_raw_response_wrapper(
            client.list_mentions,
        )
        self.list_row_back_references = to_raw_response_wrapper(
            client.list_row_back_references,
        )
        self.list_rows = to_raw_response_wrapper(
            client.list_rows,
        )
        self.update_database = to_raw_response_wrapper(
            client.update_database,
        )
        self.update_database_column = to_raw_response_wrapper(
            client.update_database_column,
        )
        self.update_workspace = to_raw_response_wrapper(
            client.update_workspace,
        )


class AsyncDeeporiginDataWithRawResponse:
    def __init__(self, client: AsyncDeeporiginData) -> None:
        self.add_database_column = async_to_raw_response_wrapper(
            client.add_database_column,
        )
        self.archive_files = async_to_raw_response_wrapper(
            client.archive_files,
        )
        self.configure_column_select_options = async_to_raw_response_wrapper(
            client.configure_column_select_options,
        )
        self.convert_id_format = async_to_raw_response_wrapper(
            client.convert_id_format,
        )
        self.create_database = async_to_raw_response_wrapper(
            client.create_database,
        )
        self.create_file_download_url = async_to_raw_response_wrapper(
            client.create_file_download_url,
        )
        self.create_file_upload = async_to_raw_response_wrapper(
            client.create_file_upload,
        )
        self.create_workspace = async_to_raw_response_wrapper(
            client.create_workspace,
        )
        self.delete_database_column = async_to_raw_response_wrapper(
            client.delete_database_column,
        )
        self.delete_rows = async_to_raw_response_wrapper(
            client.delete_rows,
        )
        self.describe_code_execution = async_to_raw_response_wrapper(
            client.describe_code_execution,
        )
        self.describe_database_stats = async_to_raw_response_wrapper(
            client.describe_database_stats,
        )
        self.describe_file = async_to_raw_response_wrapper(
            client.describe_file,
        )
        self.describe_row = async_to_raw_response_wrapper(
            client.describe_row,
        )
        self.ensure_rows = async_to_raw_response_wrapper(
            client.ensure_rows,
        )
        self.execute_code_async = async_to_raw_response_wrapper(
            client.execute_code_async,
        )
        self.execute_code_sync = async_to_raw_response_wrapper(
            client.execute_code_sync,
        )
        self.get_code_execution_result = async_to_raw_response_wrapper(
            client.get_code_execution_result,
        )
        self.import_rows = async_to_raw_response_wrapper(
            client.import_rows,
        )
        self.initialize_org = async_to_raw_response_wrapper(
            client.initialize_org,
        )
        self.list_database_column_unique_values = async_to_raw_response_wrapper(
            client.list_database_column_unique_values,
        )
        self.list_database_rows = async_to_raw_response_wrapper(
            client.list_database_rows,
        )
        self.list_files = async_to_raw_response_wrapper(
            client.list_files,
        )
        self.list_mentions = async_to_raw_response_wrapper(
            client.list_mentions,
        )
        self.list_row_back_references = async_to_raw_response_wrapper(
            client.list_row_back_references,
        )
        self.list_rows = async_to_raw_response_wrapper(
            client.list_rows,
        )
        self.update_database = async_to_raw_response_wrapper(
            client.update_database,
        )
        self.update_database_column = async_to_raw_response_wrapper(
            client.update_database_column,
        )
        self.update_workspace = async_to_raw_response_wrapper(
            client.update_workspace,
        )


class DeeporiginDataWithStreamedResponse:
    def __init__(self, client: DeeporiginData) -> None:
        self.add_database_column = to_streamed_response_wrapper(
            client.add_database_column,
        )
        self.archive_files = to_streamed_response_wrapper(
            client.archive_files,
        )
        self.configure_column_select_options = to_streamed_response_wrapper(
            client.configure_column_select_options,
        )
        self.convert_id_format = to_streamed_response_wrapper(
            client.convert_id_format,
        )
        self.create_database = to_streamed_response_wrapper(
            client.create_database,
        )
        self.create_file_download_url = to_streamed_response_wrapper(
            client.create_file_download_url,
        )
        self.create_file_upload = to_streamed_response_wrapper(
            client.create_file_upload,
        )
        self.create_workspace = to_streamed_response_wrapper(
            client.create_workspace,
        )
        self.delete_database_column = to_streamed_response_wrapper(
            client.delete_database_column,
        )
        self.delete_rows = to_streamed_response_wrapper(
            client.delete_rows,
        )
        self.describe_code_execution = to_streamed_response_wrapper(
            client.describe_code_execution,
        )
        self.describe_database_stats = to_streamed_response_wrapper(
            client.describe_database_stats,
        )
        self.describe_file = to_streamed_response_wrapper(
            client.describe_file,
        )
        self.describe_row = to_streamed_response_wrapper(
            client.describe_row,
        )
        self.ensure_rows = to_streamed_response_wrapper(
            client.ensure_rows,
        )
        self.execute_code_async = to_streamed_response_wrapper(
            client.execute_code_async,
        )
        self.execute_code_sync = to_streamed_response_wrapper(
            client.execute_code_sync,
        )
        self.get_code_execution_result = to_streamed_response_wrapper(
            client.get_code_execution_result,
        )
        self.import_rows = to_streamed_response_wrapper(
            client.import_rows,
        )
        self.initialize_org = to_streamed_response_wrapper(
            client.initialize_org,
        )
        self.list_database_column_unique_values = to_streamed_response_wrapper(
            client.list_database_column_unique_values,
        )
        self.list_database_rows = to_streamed_response_wrapper(
            client.list_database_rows,
        )
        self.list_files = to_streamed_response_wrapper(
            client.list_files,
        )
        self.list_mentions = to_streamed_response_wrapper(
            client.list_mentions,
        )
        self.list_row_back_references = to_streamed_response_wrapper(
            client.list_row_back_references,
        )
        self.list_rows = to_streamed_response_wrapper(
            client.list_rows,
        )
        self.update_database = to_streamed_response_wrapper(
            client.update_database,
        )
        self.update_database_column = to_streamed_response_wrapper(
            client.update_database_column,
        )
        self.update_workspace = to_streamed_response_wrapper(
            client.update_workspace,
        )


class AsyncDeeporiginDataWithStreamedResponse:
    def __init__(self, client: AsyncDeeporiginData) -> None:
        self.add_database_column = async_to_streamed_response_wrapper(
            client.add_database_column,
        )
        self.archive_files = async_to_streamed_response_wrapper(
            client.archive_files,
        )
        self.configure_column_select_options = async_to_streamed_response_wrapper(
            client.configure_column_select_options,
        )
        self.convert_id_format = async_to_streamed_response_wrapper(
            client.convert_id_format,
        )
        self.create_database = async_to_streamed_response_wrapper(
            client.create_database,
        )
        self.create_file_download_url = async_to_streamed_response_wrapper(
            client.create_file_download_url,
        )
        self.create_file_upload = async_to_streamed_response_wrapper(
            client.create_file_upload,
        )
        self.create_workspace = async_to_streamed_response_wrapper(
            client.create_workspace,
        )
        self.delete_database_column = async_to_streamed_response_wrapper(
            client.delete_database_column,
        )
        self.delete_rows = async_to_streamed_response_wrapper(
            client.delete_rows,
        )
        self.describe_code_execution = async_to_streamed_response_wrapper(
            client.describe_code_execution,
        )
        self.describe_database_stats = async_to_streamed_response_wrapper(
            client.describe_database_stats,
        )
        self.describe_file = async_to_streamed_response_wrapper(
            client.describe_file,
        )
        self.describe_row = async_to_streamed_response_wrapper(
            client.describe_row,
        )
        self.ensure_rows = async_to_streamed_response_wrapper(
            client.ensure_rows,
        )
        self.execute_code_async = async_to_streamed_response_wrapper(
            client.execute_code_async,
        )
        self.execute_code_sync = async_to_streamed_response_wrapper(
            client.execute_code_sync,
        )
        self.get_code_execution_result = async_to_streamed_response_wrapper(
            client.get_code_execution_result,
        )
        self.import_rows = async_to_streamed_response_wrapper(
            client.import_rows,
        )
        self.initialize_org = async_to_streamed_response_wrapper(
            client.initialize_org,
        )
        self.list_database_column_unique_values = async_to_streamed_response_wrapper(
            client.list_database_column_unique_values,
        )
        self.list_database_rows = async_to_streamed_response_wrapper(
            client.list_database_rows,
        )
        self.list_files = async_to_streamed_response_wrapper(
            client.list_files,
        )
        self.list_mentions = async_to_streamed_response_wrapper(
            client.list_mentions,
        )
        self.list_row_back_references = async_to_streamed_response_wrapper(
            client.list_row_back_references,
        )
        self.list_rows = async_to_streamed_response_wrapper(
            client.list_rows,
        )
        self.update_database = async_to_streamed_response_wrapper(
            client.update_database,
        )
        self.update_database_column = async_to_streamed_response_wrapper(
            client.update_database_column,
        )
        self.update_workspace = async_to_streamed_response_wrapper(
            client.update_workspace,
        )


Client = DeeporiginData

AsyncClient = AsyncDeeporiginData
