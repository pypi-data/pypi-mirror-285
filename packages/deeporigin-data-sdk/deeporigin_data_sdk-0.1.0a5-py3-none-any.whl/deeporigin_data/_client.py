# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Union, Mapping
from typing_extensions import Self, override

import httpx

from . import resources, _exceptions
from ._qs import Querystring
from ._types import (
    NOT_GIVEN,
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
)
from ._utils import (
    is_given,
    get_async_library,
)
from ._version import __version__
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import APIStatusError, DeeporiginDataError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)

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
    endpoints: resources.EndpointsResource
    describe_row: resources.DescribeRowResource
    convert_id_format: resources.ConvertIDFormatResource
    rows: resources.RowsResource
    database_rows: resources.DatabaseRowsResource
    database_columns: resources.DatabaseColumnsResource
    mentions: resources.MentionsResource
    files: resources.FilesResource
    base_sequences: resources.BaseSequencesResource
    database_stats: resources.DatabaseStatsResource
    code_executions: resources.CodeExecutionsResource
    chat_threads: resources.ChatThreadsResource
    workspaces: resources.WorkspacesResource
    databases: resources.DatabasesResource
    column_options: resources.ColumnOptionsResource
    organizations: resources.OrganizationsResource
    execute_code: resources.ExecuteCodeResource
    chat_messages: resources.ChatMessagesResource
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

        self.endpoints = resources.EndpointsResource(self)
        self.describe_row = resources.DescribeRowResource(self)
        self.convert_id_format = resources.ConvertIDFormatResource(self)
        self.rows = resources.RowsResource(self)
        self.database_rows = resources.DatabaseRowsResource(self)
        self.database_columns = resources.DatabaseColumnsResource(self)
        self.mentions = resources.MentionsResource(self)
        self.files = resources.FilesResource(self)
        self.base_sequences = resources.BaseSequencesResource(self)
        self.database_stats = resources.DatabaseStatsResource(self)
        self.code_executions = resources.CodeExecutionsResource(self)
        self.chat_threads = resources.ChatThreadsResource(self)
        self.workspaces = resources.WorkspacesResource(self)
        self.databases = resources.DatabasesResource(self)
        self.column_options = resources.ColumnOptionsResource(self)
        self.organizations = resources.OrganizationsResource(self)
        self.execute_code = resources.ExecuteCodeResource(self)
        self.chat_messages = resources.ChatMessagesResource(self)
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
    endpoints: resources.AsyncEndpointsResource
    describe_row: resources.AsyncDescribeRowResource
    convert_id_format: resources.AsyncConvertIDFormatResource
    rows: resources.AsyncRowsResource
    database_rows: resources.AsyncDatabaseRowsResource
    database_columns: resources.AsyncDatabaseColumnsResource
    mentions: resources.AsyncMentionsResource
    files: resources.AsyncFilesResource
    base_sequences: resources.AsyncBaseSequencesResource
    database_stats: resources.AsyncDatabaseStatsResource
    code_executions: resources.AsyncCodeExecutionsResource
    chat_threads: resources.AsyncChatThreadsResource
    workspaces: resources.AsyncWorkspacesResource
    databases: resources.AsyncDatabasesResource
    column_options: resources.AsyncColumnOptionsResource
    organizations: resources.AsyncOrganizationsResource
    execute_code: resources.AsyncExecuteCodeResource
    chat_messages: resources.AsyncChatMessagesResource
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

        self.endpoints = resources.AsyncEndpointsResource(self)
        self.describe_row = resources.AsyncDescribeRowResource(self)
        self.convert_id_format = resources.AsyncConvertIDFormatResource(self)
        self.rows = resources.AsyncRowsResource(self)
        self.database_rows = resources.AsyncDatabaseRowsResource(self)
        self.database_columns = resources.AsyncDatabaseColumnsResource(self)
        self.mentions = resources.AsyncMentionsResource(self)
        self.files = resources.AsyncFilesResource(self)
        self.base_sequences = resources.AsyncBaseSequencesResource(self)
        self.database_stats = resources.AsyncDatabaseStatsResource(self)
        self.code_executions = resources.AsyncCodeExecutionsResource(self)
        self.chat_threads = resources.AsyncChatThreadsResource(self)
        self.workspaces = resources.AsyncWorkspacesResource(self)
        self.databases = resources.AsyncDatabasesResource(self)
        self.column_options = resources.AsyncColumnOptionsResource(self)
        self.organizations = resources.AsyncOrganizationsResource(self)
        self.execute_code = resources.AsyncExecuteCodeResource(self)
        self.chat_messages = resources.AsyncChatMessagesResource(self)
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
        self.endpoints = resources.EndpointsResourceWithRawResponse(client.endpoints)
        self.describe_row = resources.DescribeRowResourceWithRawResponse(client.describe_row)
        self.convert_id_format = resources.ConvertIDFormatResourceWithRawResponse(client.convert_id_format)
        self.rows = resources.RowsResourceWithRawResponse(client.rows)
        self.database_rows = resources.DatabaseRowsResourceWithRawResponse(client.database_rows)
        self.database_columns = resources.DatabaseColumnsResourceWithRawResponse(client.database_columns)
        self.mentions = resources.MentionsResourceWithRawResponse(client.mentions)
        self.files = resources.FilesResourceWithRawResponse(client.files)
        self.base_sequences = resources.BaseSequencesResourceWithRawResponse(client.base_sequences)
        self.database_stats = resources.DatabaseStatsResourceWithRawResponse(client.database_stats)
        self.code_executions = resources.CodeExecutionsResourceWithRawResponse(client.code_executions)
        self.chat_threads = resources.ChatThreadsResourceWithRawResponse(client.chat_threads)
        self.workspaces = resources.WorkspacesResourceWithRawResponse(client.workspaces)
        self.databases = resources.DatabasesResourceWithRawResponse(client.databases)
        self.column_options = resources.ColumnOptionsResourceWithRawResponse(client.column_options)
        self.organizations = resources.OrganizationsResourceWithRawResponse(client.organizations)
        self.execute_code = resources.ExecuteCodeResourceWithRawResponse(client.execute_code)
        self.chat_messages = resources.ChatMessagesResourceWithRawResponse(client.chat_messages)


class AsyncDeeporiginDataWithRawResponse:
    def __init__(self, client: AsyncDeeporiginData) -> None:
        self.endpoints = resources.AsyncEndpointsResourceWithRawResponse(client.endpoints)
        self.describe_row = resources.AsyncDescribeRowResourceWithRawResponse(client.describe_row)
        self.convert_id_format = resources.AsyncConvertIDFormatResourceWithRawResponse(client.convert_id_format)
        self.rows = resources.AsyncRowsResourceWithRawResponse(client.rows)
        self.database_rows = resources.AsyncDatabaseRowsResourceWithRawResponse(client.database_rows)
        self.database_columns = resources.AsyncDatabaseColumnsResourceWithRawResponse(client.database_columns)
        self.mentions = resources.AsyncMentionsResourceWithRawResponse(client.mentions)
        self.files = resources.AsyncFilesResourceWithRawResponse(client.files)
        self.base_sequences = resources.AsyncBaseSequencesResourceWithRawResponse(client.base_sequences)
        self.database_stats = resources.AsyncDatabaseStatsResourceWithRawResponse(client.database_stats)
        self.code_executions = resources.AsyncCodeExecutionsResourceWithRawResponse(client.code_executions)
        self.chat_threads = resources.AsyncChatThreadsResourceWithRawResponse(client.chat_threads)
        self.workspaces = resources.AsyncWorkspacesResourceWithRawResponse(client.workspaces)
        self.databases = resources.AsyncDatabasesResourceWithRawResponse(client.databases)
        self.column_options = resources.AsyncColumnOptionsResourceWithRawResponse(client.column_options)
        self.organizations = resources.AsyncOrganizationsResourceWithRawResponse(client.organizations)
        self.execute_code = resources.AsyncExecuteCodeResourceWithRawResponse(client.execute_code)
        self.chat_messages = resources.AsyncChatMessagesResourceWithRawResponse(client.chat_messages)


class DeeporiginDataWithStreamedResponse:
    def __init__(self, client: DeeporiginData) -> None:
        self.endpoints = resources.EndpointsResourceWithStreamingResponse(client.endpoints)
        self.describe_row = resources.DescribeRowResourceWithStreamingResponse(client.describe_row)
        self.convert_id_format = resources.ConvertIDFormatResourceWithStreamingResponse(client.convert_id_format)
        self.rows = resources.RowsResourceWithStreamingResponse(client.rows)
        self.database_rows = resources.DatabaseRowsResourceWithStreamingResponse(client.database_rows)
        self.database_columns = resources.DatabaseColumnsResourceWithStreamingResponse(client.database_columns)
        self.mentions = resources.MentionsResourceWithStreamingResponse(client.mentions)
        self.files = resources.FilesResourceWithStreamingResponse(client.files)
        self.base_sequences = resources.BaseSequencesResourceWithStreamingResponse(client.base_sequences)
        self.database_stats = resources.DatabaseStatsResourceWithStreamingResponse(client.database_stats)
        self.code_executions = resources.CodeExecutionsResourceWithStreamingResponse(client.code_executions)
        self.chat_threads = resources.ChatThreadsResourceWithStreamingResponse(client.chat_threads)
        self.workspaces = resources.WorkspacesResourceWithStreamingResponse(client.workspaces)
        self.databases = resources.DatabasesResourceWithStreamingResponse(client.databases)
        self.column_options = resources.ColumnOptionsResourceWithStreamingResponse(client.column_options)
        self.organizations = resources.OrganizationsResourceWithStreamingResponse(client.organizations)
        self.execute_code = resources.ExecuteCodeResourceWithStreamingResponse(client.execute_code)
        self.chat_messages = resources.ChatMessagesResourceWithStreamingResponse(client.chat_messages)


class AsyncDeeporiginDataWithStreamedResponse:
    def __init__(self, client: AsyncDeeporiginData) -> None:
        self.endpoints = resources.AsyncEndpointsResourceWithStreamingResponse(client.endpoints)
        self.describe_row = resources.AsyncDescribeRowResourceWithStreamingResponse(client.describe_row)
        self.convert_id_format = resources.AsyncConvertIDFormatResourceWithStreamingResponse(client.convert_id_format)
        self.rows = resources.AsyncRowsResourceWithStreamingResponse(client.rows)
        self.database_rows = resources.AsyncDatabaseRowsResourceWithStreamingResponse(client.database_rows)
        self.database_columns = resources.AsyncDatabaseColumnsResourceWithStreamingResponse(client.database_columns)
        self.mentions = resources.AsyncMentionsResourceWithStreamingResponse(client.mentions)
        self.files = resources.AsyncFilesResourceWithStreamingResponse(client.files)
        self.base_sequences = resources.AsyncBaseSequencesResourceWithStreamingResponse(client.base_sequences)
        self.database_stats = resources.AsyncDatabaseStatsResourceWithStreamingResponse(client.database_stats)
        self.code_executions = resources.AsyncCodeExecutionsResourceWithStreamingResponse(client.code_executions)
        self.chat_threads = resources.AsyncChatThreadsResourceWithStreamingResponse(client.chat_threads)
        self.workspaces = resources.AsyncWorkspacesResourceWithStreamingResponse(client.workspaces)
        self.databases = resources.AsyncDatabasesResourceWithStreamingResponse(client.databases)
        self.column_options = resources.AsyncColumnOptionsResourceWithStreamingResponse(client.column_options)
        self.organizations = resources.AsyncOrganizationsResourceWithStreamingResponse(client.organizations)
        self.execute_code = resources.AsyncExecuteCodeResourceWithStreamingResponse(client.execute_code)
        self.chat_messages = resources.AsyncChatMessagesResourceWithStreamingResponse(client.chat_messages)


Client = DeeporiginData

AsyncClient = AsyncDeeporiginData
