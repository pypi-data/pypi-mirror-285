# DeeporiginData

Types:

```python
from deeporigin_data.types import (
    Database,
    DescribeRowResponse,
    AddDatabaseColumnResponse,
    ArchiveFilesResponse,
    ConfigureColumnSelectOptionsResponse,
    ConvertIDFormatResponse,
    CreateDatabaseResponse,
    CreateFileDownloadURLResponse,
    CreateFileUploadResponse,
    CreateWorkspaceResponse,
    DeleteDatabaseColumnResponse,
    DeleteRowsResponse,
    DescribeCodeExecutionResponse,
    DescribeDatabaseStatsResponse,
    DescribeFileResponse,
    EnsureRowsResponse,
    ExecuteCodeAsyncResponse,
    ExecuteCodeSyncResponse,
    GetCodeExecutionResultResponse,
    ImportRowsResponse,
    InitializeOrgResponse,
    ListDatabaseColumnUniqueValuesResponse,
    ListDatabaseRowsResponse,
    ListFilesResponse,
    ListMentionsResponse,
    ListRowBackReferencesResponse,
    ListRowsResponse,
    UpdateDatabaseResponse,
    UpdateDatabaseColumnResponse,
    UpdateWorkspaceResponse,
)
```

Methods:

- <code title="post /AddDatabaseColumn">client.<a href="./src/deeporigin_data/_client.py">add_database_column</a>(\*\*<a href="src/deeporigin_data/types/top_level_add_database_column_params.py">params</a>) -> <a href="./src/deeporigin_data/types/add_database_column_response.py">AddDatabaseColumnResponse</a></code>
- <code title="post /ArchiveFiles">client.<a href="./src/deeporigin_data/_client.py">archive_files</a>(\*\*<a href="src/deeporigin_data/types/top_level_archive_files_params.py">params</a>) -> <a href="./src/deeporigin_data/types/archive_files_response.py">object</a></code>
- <code title="post /ConfigureColumnSelectOptions">client.<a href="./src/deeporigin_data/_client.py">configure_column_select_options</a>(\*\*<a href="src/deeporigin_data/types/top_level_configure_column_select_options_params.py">params</a>) -> <a href="./src/deeporigin_data/types/configure_column_select_options_response.py">ConfigureColumnSelectOptionsResponse</a></code>
- <code title="post /ConvertIdFormat">client.<a href="./src/deeporigin_data/_client.py">convert_id_format</a>(\*\*<a href="src/deeporigin_data/types/top_level_convert_id_format_params.py">params</a>) -> <a href="./src/deeporigin_data/types/convert_id_format_response.py">ConvertIDFormatResponse</a></code>
- <code title="post /CreateDatabase">client.<a href="./src/deeporigin_data/_client.py">create_database</a>(\*\*<a href="src/deeporigin_data/types/top_level_create_database_params.py">params</a>) -> <a href="./src/deeporigin_data/types/create_database_response.py">CreateDatabaseResponse</a></code>
- <code title="post /CreateFileDownloadUrl">client.<a href="./src/deeporigin_data/_client.py">create_file_download_url</a>(\*\*<a href="src/deeporigin_data/types/top_level_create_file_download_url_params.py">params</a>) -> <a href="./src/deeporigin_data/types/create_file_download_url_response.py">CreateFileDownloadURLResponse</a></code>
- <code title="post /CreateFileUpload">client.<a href="./src/deeporigin_data/_client.py">create_file_upload</a>(\*\*<a href="src/deeporigin_data/types/top_level_create_file_upload_params.py">params</a>) -> <a href="./src/deeporigin_data/types/create_file_upload_response.py">CreateFileUploadResponse</a></code>
- <code title="post /CreateWorkspace">client.<a href="./src/deeporigin_data/_client.py">create_workspace</a>(\*\*<a href="src/deeporigin_data/types/top_level_create_workspace_params.py">params</a>) -> <a href="./src/deeporigin_data/types/create_workspace_response.py">CreateWorkspaceResponse</a></code>
- <code title="post /DeleteDatabaseColumn">client.<a href="./src/deeporigin_data/_client.py">delete_database_column</a>(\*\*<a href="src/deeporigin_data/types/top_level_delete_database_column_params.py">params</a>) -> <a href="./src/deeporigin_data/types/delete_database_column_response.py">DeleteDatabaseColumnResponse</a></code>
- <code title="post /DeleteRows">client.<a href="./src/deeporigin_data/_client.py">delete_rows</a>(\*\*<a href="src/deeporigin_data/types/top_level_delete_rows_params.py">params</a>) -> <a href="./src/deeporigin_data/types/delete_rows_response.py">DeleteRowsResponse</a></code>
- <code title="post /DescribeCodeExecution">client.<a href="./src/deeporigin_data/_client.py">describe_code_execution</a>(\*\*<a href="src/deeporigin_data/types/top_level_describe_code_execution_params.py">params</a>) -> <a href="./src/deeporigin_data/types/describe_code_execution_response.py">DescribeCodeExecutionResponse</a></code>
- <code title="post /DescribeDatabaseStats">client.<a href="./src/deeporigin_data/_client.py">describe_database_stats</a>(\*\*<a href="src/deeporigin_data/types/top_level_describe_database_stats_params.py">params</a>) -> <a href="./src/deeporigin_data/types/describe_database_stats_response.py">DescribeDatabaseStatsResponse</a></code>
- <code title="post /DescribeFile">client.<a href="./src/deeporigin_data/_client.py">describe_file</a>(\*\*<a href="src/deeporigin_data/types/top_level_describe_file_params.py">params</a>) -> <a href="./src/deeporigin_data/types/describe_file_response.py">DescribeFileResponse</a></code>
- <code title="post /DescribeRow">client.<a href="./src/deeporigin_data/_client.py">describe_row</a>(\*\*<a href="src/deeporigin_data/types/top_level_describe_row_params.py">params</a>) -> <a href="./src/deeporigin_data/types/describe_row_response.py">DescribeRowResponse</a></code>
- <code title="post /EnsureRows">client.<a href="./src/deeporigin_data/_client.py">ensure_rows</a>(\*\*<a href="src/deeporigin_data/types/top_level_ensure_rows_params.py">params</a>) -> <a href="./src/deeporigin_data/types/ensure_rows_response.py">EnsureRowsResponse</a></code>
- <code title="post /ExecuteCode">client.<a href="./src/deeporigin_data/_client.py">execute_code_async</a>(\*\*<a href="src/deeporigin_data/types/top_level_execute_code_async_params.py">params</a>) -> <a href="./src/deeporigin_data/types/execute_code_async_response.py">ExecuteCodeAsyncResponse</a></code>
- <code title="post /ExecuteCodeSync">client.<a href="./src/deeporigin_data/_client.py">execute_code_sync</a>(\*\*<a href="src/deeporigin_data/types/top_level_execute_code_sync_params.py">params</a>) -> <a href="./src/deeporigin_data/types/execute_code_sync_response.py">ExecuteCodeSyncResponse</a></code>
- <code title="post /GetCodeExecutionResult">client.<a href="./src/deeporigin_data/_client.py">get_code_execution_result</a>(\*\*<a href="src/deeporigin_data/types/top_level_get_code_execution_result_params.py">params</a>) -> <a href="./src/deeporigin_data/types/get_code_execution_result_response.py">object</a></code>
- <code title="post /ImportRows">client.<a href="./src/deeporigin_data/_client.py">import_rows</a>(\*\*<a href="src/deeporigin_data/types/top_level_import_rows_params.py">params</a>) -> <a href="./src/deeporigin_data/types/import_rows_response.py">ImportRowsResponse</a></code>
- <code title="post /InitializeOrg">client.<a href="./src/deeporigin_data/_client.py">initialize_org</a>(\*\*<a href="src/deeporigin_data/types/top_level_initialize_org_params.py">params</a>) -> <a href="./src/deeporigin_data/types/initialize_org_response.py">InitializeOrgResponse</a></code>
- <code title="post /ListDatabaseColumnUniqueValues">client.<a href="./src/deeporigin_data/_client.py">list_database_column_unique_values</a>(\*\*<a href="src/deeporigin_data/types/top_level_list_database_column_unique_values_params.py">params</a>) -> <a href="./src/deeporigin_data/types/list_database_column_unique_values_response.py">ListDatabaseColumnUniqueValuesResponse</a></code>
- <code title="post /ListDatabaseRows">client.<a href="./src/deeporigin_data/_client.py">list_database_rows</a>(\*\*<a href="src/deeporigin_data/types/top_level_list_database_rows_params.py">params</a>) -> <a href="./src/deeporigin_data/types/list_database_rows_response.py">ListDatabaseRowsResponse</a></code>
- <code title="post /ListFiles">client.<a href="./src/deeporigin_data/_client.py">list_files</a>(\*\*<a href="src/deeporigin_data/types/top_level_list_files_params.py">params</a>) -> <a href="./src/deeporigin_data/types/list_files_response.py">ListFilesResponse</a></code>
- <code title="post /ListMentions">client.<a href="./src/deeporigin_data/_client.py">list_mentions</a>(\*\*<a href="src/deeporigin_data/types/top_level_list_mentions_params.py">params</a>) -> <a href="./src/deeporigin_data/types/list_mentions_response.py">ListMentionsResponse</a></code>
- <code title="post /ListRowBackReferences">client.<a href="./src/deeporigin_data/_client.py">list_row_back_references</a>(\*\*<a href="src/deeporigin_data/types/top_level_list_row_back_references_params.py">params</a>) -> <a href="./src/deeporigin_data/types/list_row_back_references_response.py">ListRowBackReferencesResponse</a></code>
- <code title="post /ListRows">client.<a href="./src/deeporigin_data/_client.py">list_rows</a>(\*\*<a href="src/deeporigin_data/types/top_level_list_rows_params.py">params</a>) -> <a href="./src/deeporigin_data/types/list_rows_response.py">ListRowsResponse</a></code>
- <code title="post /UpdateDatabase">client.<a href="./src/deeporigin_data/_client.py">update_database</a>(\*\*<a href="src/deeporigin_data/types/top_level_update_database_params.py">params</a>) -> <a href="./src/deeporigin_data/types/update_database_response.py">UpdateDatabaseResponse</a></code>
- <code title="post /UpdateDatabaseColumn">client.<a href="./src/deeporigin_data/_client.py">update_database_column</a>(\*\*<a href="src/deeporigin_data/types/top_level_update_database_column_params.py">params</a>) -> <a href="./src/deeporigin_data/types/update_database_column_response.py">UpdateDatabaseColumnResponse</a></code>
- <code title="post /UpdateWorkspace">client.<a href="./src/deeporigin_data/_client.py">update_workspace</a>(\*\*<a href="src/deeporigin_data/types/top_level_update_workspace_params.py">params</a>) -> <a href="./src/deeporigin_data/types/update_workspace_response.py">UpdateWorkspaceResponse</a></code>
