# Endpoints

Types:

```python
from deeporigin_data.types import EndpointCreateFileDownloadURLResponse
```

Methods:

- <code title="post /CreateFileDownloadUrl">client.endpoints.<a href="./src/deeporigin_data/resources/endpoints.py">create_file_download_url</a>(\*\*<a href="src/deeporigin_data/types/endpoint_create_file_download_url_params.py">params</a>) -> <a href="./src/deeporigin_data/types/endpoint_create_file_download_url_response.py">EndpointCreateFileDownloadURLResponse</a></code>

# DescribeRow

Types:

```python
from deeporigin_data.types import DescribeRowResponse
```

Methods:

- <code title="post /DescribeRow">client.describe_row.<a href="./src/deeporigin_data/resources/describe_row.py">describe</a>(\*\*<a href="src/deeporigin_data/types/describe_row_describe_params.py">params</a>) -> <a href="./src/deeporigin_data/types/describe_row_response.py">DescribeRowResponse</a></code>

# ConvertIDFormat

Types:

```python
from deeporigin_data.types import ConvertIDFormatConvertResponse
```

Methods:

- <code title="post /ConvertIdFormat">client.convert_id_format.<a href="./src/deeporigin_data/resources/convert_id_format.py">convert</a>(\*\*<a href="src/deeporigin_data/types/convert_id_format_convert_params.py">params</a>) -> <a href="./src/deeporigin_data/types/convert_id_format_convert_response.py">ConvertIDFormatConvertResponse</a></code>

# Rows

Types:

```python
from deeporigin_data.types import (
    RowListResponse,
    RowDeleteResponse,
    RowBackReferencesResponse,
    RowEnsureResponse,
    RowImportResponse,
)
```

Methods:

- <code title="post /ListRows">client.rows.<a href="./src/deeporigin_data/resources/rows.py">list</a>(\*\*<a href="src/deeporigin_data/types/row_list_params.py">params</a>) -> <a href="./src/deeporigin_data/types/row_list_response.py">RowListResponse</a></code>
- <code title="post /DeleteRows">client.rows.<a href="./src/deeporigin_data/resources/rows.py">delete</a>(\*\*<a href="src/deeporigin_data/types/row_delete_params.py">params</a>) -> <a href="./src/deeporigin_data/types/row_delete_response.py">RowDeleteResponse</a></code>
- <code title="post /ListRowBackReferences">client.rows.<a href="./src/deeporigin_data/resources/rows.py">back_references</a>(\*\*<a href="src/deeporigin_data/types/row_back_references_params.py">params</a>) -> <a href="./src/deeporigin_data/types/row_back_references_response.py">RowBackReferencesResponse</a></code>
- <code title="post /EnsureRows">client.rows.<a href="./src/deeporigin_data/resources/rows.py">ensure</a>(\*\*<a href="src/deeporigin_data/types/row_ensure_params.py">params</a>) -> <a href="./src/deeporigin_data/types/row_ensure_response.py">RowEnsureResponse</a></code>
- <code title="post /ImportRows">client.rows.<a href="./src/deeporigin_data/resources/rows.py">import\_</a>(\*\*<a href="src/deeporigin_data/types/row_import_params.py">params</a>) -> <a href="./src/deeporigin_data/types/row_import_response.py">RowImportResponse</a></code>

# DatabaseRows

Types:

```python
from deeporigin_data.types import DatabaseRowListResponse
```

Methods:

- <code title="post /ListDatabaseRows">client.database_rows.<a href="./src/deeporigin_data/resources/database_rows.py">list</a>(\*\*<a href="src/deeporigin_data/types/database_row_list_params.py">params</a>) -> <a href="./src/deeporigin_data/types/database_row_list_response.py">DatabaseRowListResponse</a></code>

# DatabaseColumns

Types:

```python
from deeporigin_data.types import (
    DatabaseColumnUpdateResponse,
    DatabaseColumnDeleteResponse,
    DatabaseColumnAddResponse,
    DatabaseColumnUniqueValuesResponse,
)
```

Methods:

- <code title="post /UpdateDatabaseColumn">client.database_columns.<a href="./src/deeporigin_data/resources/database_columns.py">update</a>(\*\*<a href="src/deeporigin_data/types/database_column_update_params.py">params</a>) -> <a href="./src/deeporigin_data/types/database_column_update_response.py">DatabaseColumnUpdateResponse</a></code>
- <code title="post /DeleteDatabaseColumn">client.database_columns.<a href="./src/deeporigin_data/resources/database_columns.py">delete</a>(\*\*<a href="src/deeporigin_data/types/database_column_delete_params.py">params</a>) -> <a href="./src/deeporigin_data/types/database_column_delete_response.py">DatabaseColumnDeleteResponse</a></code>
- <code title="post /AddDatabaseColumn">client.database_columns.<a href="./src/deeporigin_data/resources/database_columns.py">add</a>(\*\*<a href="src/deeporigin_data/types/database_column_add_params.py">params</a>) -> <a href="./src/deeporigin_data/types/database_column_add_response.py">DatabaseColumnAddResponse</a></code>
- <code title="post /ListDatabaseColumnUniqueValues">client.database_columns.<a href="./src/deeporigin_data/resources/database_columns.py">unique_values</a>(\*\*<a href="src/deeporigin_data/types/database_column_unique_values_params.py">params</a>) -> <a href="./src/deeporigin_data/types/database_column_unique_values_response.py">DatabaseColumnUniqueValuesResponse</a></code>

# Mentions

Types:

```python
from deeporigin_data.types import MentionListResponse
```

Methods:

- <code title="post /ListMentions">client.mentions.<a href="./src/deeporigin_data/resources/mentions.py">list</a>(\*\*<a href="src/deeporigin_data/types/mention_list_params.py">params</a>) -> <a href="./src/deeporigin_data/types/mention_list_response.py">MentionListResponse</a></code>

# Files

Types:

```python
from deeporigin_data.types import (
    FileListResponse,
    FileArchiveResponse,
    FileDescribeResponse,
    FileUploadResponse,
)
```

Methods:

- <code title="post /ListFiles">client.files.<a href="./src/deeporigin_data/resources/files.py">list</a>(\*\*<a href="src/deeporigin_data/types/file_list_params.py">params</a>) -> <a href="./src/deeporigin_data/types/file_list_response.py">FileListResponse</a></code>
- <code title="post /ArchiveFiles">client.files.<a href="./src/deeporigin_data/resources/files.py">archive</a>(\*\*<a href="src/deeporigin_data/types/file_archive_params.py">params</a>) -> <a href="./src/deeporigin_data/types/file_archive_response.py">object</a></code>
- <code title="post /DescribeFile">client.files.<a href="./src/deeporigin_data/resources/files.py">describe</a>(\*\*<a href="src/deeporigin_data/types/file_describe_params.py">params</a>) -> <a href="./src/deeporigin_data/types/file_describe_response.py">FileDescribeResponse</a></code>
- <code title="post /CreateFileUpload">client.files.<a href="./src/deeporigin_data/resources/files.py">upload</a>(\*\*<a href="src/deeporigin_data/types/file_upload_params.py">params</a>) -> <a href="./src/deeporigin_data/types/file_upload_response.py">FileUploadResponse</a></code>

# BaseSequences

Types:

```python
from deeporigin_data.types import SeqData, BaseSequenceParseResponse
```

Methods:

- <code title="post /ParseBaseSequenceData">client.base_sequences.<a href="./src/deeporigin_data/resources/base_sequences.py">parse</a>(\*\*<a href="src/deeporigin_data/types/base_sequence_parse_params.py">params</a>) -> <a href="./src/deeporigin_data/types/base_sequence_parse_response.py">BaseSequenceParseResponse</a></code>

# DatabaseStats

Types:

```python
from deeporigin_data.types import DatabaseStatDescribeResponse
```

Methods:

- <code title="post /DescribeDatabaseStats">client.database_stats.<a href="./src/deeporigin_data/resources/database_stats.py">describe</a>(\*\*<a href="src/deeporigin_data/types/database_stat_describe_params.py">params</a>) -> <a href="./src/deeporigin_data/types/database_stat_describe_response.py">DatabaseStatDescribeResponse</a></code>

# CodeExecutions

Types:

```python
from deeporigin_data.types import CodeExecutionDescribeResponse, CodeExecutionResultResponse
```

Methods:

- <code title="post /DescribeCodeExecution">client.code_executions.<a href="./src/deeporigin_data/resources/code_executions.py">describe</a>(\*\*<a href="src/deeporigin_data/types/code_execution_describe_params.py">params</a>) -> <a href="./src/deeporigin_data/types/code_execution_describe_response.py">CodeExecutionDescribeResponse</a></code>
- <code title="post /GetCodeExecutionResult">client.code_executions.<a href="./src/deeporigin_data/resources/code_executions.py">result</a>(\*\*<a href="src/deeporigin_data/types/code_execution_result_params.py">params</a>) -> <a href="./src/deeporigin_data/types/code_execution_result_response.py">object</a></code>

# ChatThreads

Types:

```python
from deeporigin_data.types import ChatThreadCreateResponse
```

Methods:

- <code title="post /CreateChatThread">client.chat_threads.<a href="./src/deeporigin_data/resources/chat_threads/chat_threads.py">create</a>(\*\*<a href="src/deeporigin_data/types/chat_thread_create_params.py">params</a>) -> <a href="./src/deeporigin_data/types/chat_thread_create_response.py">ChatThreadCreateResponse</a></code>

## Messages

Types:

```python
from deeporigin_data.types.chat_threads import MessageListResponse
```

Methods:

- <code title="post /ListChatThreadMessages">client.chat_threads.messages.<a href="./src/deeporigin_data/resources/chat_threads/messages.py">list</a>(\*\*<a href="src/deeporigin_data/types/chat_threads/message_list_params.py">params</a>) -> <a href="./src/deeporigin_data/types/chat_threads/message_list_response.py">MessageListResponse</a></code>

# Workspaces

Types:

```python
from deeporigin_data.types import WorkspaceCreateResponse, WorkspaceUpdateResponse
```

Methods:

- <code title="post /CreateWorkspace">client.workspaces.<a href="./src/deeporigin_data/resources/workspaces.py">create</a>(\*\*<a href="src/deeporigin_data/types/workspace_create_params.py">params</a>) -> <a href="./src/deeporigin_data/types/workspace_create_response.py">WorkspaceCreateResponse</a></code>
- <code title="post /UpdateWorkspace">client.workspaces.<a href="./src/deeporigin_data/resources/workspaces.py">update</a>(\*\*<a href="src/deeporigin_data/types/workspace_update_params.py">params</a>) -> <a href="./src/deeporigin_data/types/workspace_update_response.py">WorkspaceUpdateResponse</a></code>

# Databases

Types:

```python
from deeporigin_data.types import Database, DatabaseCreateResponse, DatabaseUpdateResponse
```

Methods:

- <code title="post /CreateDatabase">client.databases.<a href="./src/deeporigin_data/resources/databases.py">create</a>(\*\*<a href="src/deeporigin_data/types/database_create_params.py">params</a>) -> <a href="./src/deeporigin_data/types/database_create_response.py">DatabaseCreateResponse</a></code>
- <code title="post /UpdateDatabase">client.databases.<a href="./src/deeporigin_data/resources/databases.py">update</a>(\*\*<a href="src/deeporigin_data/types/database_update_params.py">params</a>) -> <a href="./src/deeporigin_data/types/database_update_response.py">DatabaseUpdateResponse</a></code>

# ColumnOptions

Types:

```python
from deeporigin_data.types import ColumnOptionConfigureResponse
```

Methods:

- <code title="post /ConfigureColumnSelectOptions">client.column_options.<a href="./src/deeporigin_data/resources/column_options.py">configure</a>(\*\*<a href="src/deeporigin_data/types/column_option_configure_params.py">params</a>) -> <a href="./src/deeporigin_data/types/column_option_configure_response.py">ColumnOptionConfigureResponse</a></code>

# Organizations

Types:

```python
from deeporigin_data.types import OrganizationInitializeResponse
```

Methods:

- <code title="post /InitializeOrg">client.organizations.<a href="./src/deeporigin_data/resources/organizations.py">initialize</a>(\*\*<a href="src/deeporigin_data/types/organization_initialize_params.py">params</a>) -> <a href="./src/deeporigin_data/types/organization_initialize_response.py">OrganizationInitializeResponse</a></code>

# ExecuteCode

Types:

```python
from deeporigin_data.types import ExecuteCodeAsyncExecuteResponse, ExecuteCodeSyncExecuteResponse
```

Methods:

- <code title="post /ExecuteCode">client.execute_code.<a href="./src/deeporigin_data/resources/execute_code.py">async_execute</a>(\*\*<a href="src/deeporigin_data/types/execute_code_async_execute_params.py">params</a>) -> <a href="./src/deeporigin_data/types/execute_code_async_execute_response.py">ExecuteCodeAsyncExecuteResponse</a></code>
- <code title="post /ExecuteCodeSync">client.execute_code.<a href="./src/deeporigin_data/resources/execute_code.py">sync_execute</a>(\*\*<a href="src/deeporigin_data/types/execute_code_sync_execute_params.py">params</a>) -> <a href="./src/deeporigin_data/types/execute_code_sync_execute_response.py">ExecuteCodeSyncExecuteResponse</a></code>

# ChatMessages

Methods:

- <code title="post /SendChatMessage">client.chat_messages.<a href="./src/deeporigin_data/resources/chat_messages.py">send</a>(\*\*<a href="src/deeporigin_data/types/chat_message_send_params.py">params</a>) -> None</code>
