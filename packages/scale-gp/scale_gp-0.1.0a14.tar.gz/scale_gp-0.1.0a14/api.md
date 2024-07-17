# Shared Types

```python
from scale_gp.types import (
    DeleteResponse,
    DeleteResponse,
    ModelUsageResponse,
    PaginationResponseModelDeployment,
    TaskResponse,
    TestCaseResultResponse,
    TestCaseResultResponseWithViews,
    TestCaseVersionResponse,
)
```

# KnowledgeBases

Types:

```python
from scale_gp.types import (
    CreateKnowledgeBaseResponse,
    DeleteKnowledgeBaseResponseV2,
    KnowledgeBaseItemV2,
    KnowledgeBaseItemV2List,
    KnowledgeBaseQueryResponse,
)
```

Methods:

- <code title="post /v4/knowledge-bases">client.knowledge_bases.<a href="./src/scale_gp/resources/knowledge_bases/knowledge_bases.py">create</a>(\*\*<a href="src/scale_gp/types/knowledge_base_create_params.py">params</a>) -> <a href="./src/scale_gp/types/create_knowledge_base_response.py">CreateKnowledgeBaseResponse</a></code>
- <code title="get /v4/knowledge-bases/{knowledge_base_id}">client.knowledge_bases.<a href="./src/scale_gp/resources/knowledge_bases/knowledge_bases.py">retrieve</a>(knowledge_base_id, \*\*<a href="src/scale_gp/types/knowledge_base_retrieve_params.py">params</a>) -> <a href="./src/scale_gp/types/knowledge_base_item_v2.py">KnowledgeBaseItemV2</a></code>
- <code title="get /v4/knowledge-bases">client.knowledge_bases.<a href="./src/scale_gp/resources/knowledge_bases/knowledge_bases.py">list</a>(\*\*<a href="src/scale_gp/types/knowledge_base_list_params.py">params</a>) -> <a href="./src/scale_gp/types/knowledge_base_item_v2_list.py">KnowledgeBaseItemV2List</a></code>
- <code title="delete /v4/knowledge-bases/{knowledge_base_id}">client.knowledge_bases.<a href="./src/scale_gp/resources/knowledge_bases/knowledge_bases.py">delete</a>(knowledge_base_id) -> <a href="./src/scale_gp/types/delete_knowledge_base_response_v2.py">DeleteKnowledgeBaseResponseV2</a></code>
- <code title="post /v4/knowledge-bases/{knowledge_base_id}/query">client.knowledge_bases.<a href="./src/scale_gp/resources/knowledge_bases/knowledge_bases.py">query</a>(knowledge_base_id, \*\*<a href="src/scale_gp/types/knowledge_base_query_params.py">params</a>) -> <a href="./src/scale_gp/types/knowledge_base_query_response.py">object</a></code>

## AsyncJobs

Types:

```python
from scale_gp.types.knowledge_bases import AsyncJobListResponse
```

Methods:

- <code title="get /v4/knowledge-bases/{knowledge_base_id}/async-jobs">client.knowledge_bases.async_jobs.<a href="./src/scale_gp/resources/knowledge_bases/async_jobs.py">list</a>(knowledge_base_id, \*\*<a href="src/scale_gp/types/knowledge_bases/async_job_list_params.py">params</a>) -> <a href="./src/scale_gp/types/knowledge_bases/async_job_list_response.py">object</a></code>

## Chunks

Types:

```python
from scale_gp.types.knowledge_bases import GetChunksResponse
```

Methods:

- <code title="get /v4/knowledge-bases/{knowledge_base_id}/chunks">client.knowledge_bases.chunks.<a href="./src/scale_gp/resources/knowledge_bases/chunks.py">list</a>(knowledge_base_id, \*\*<a href="src/scale_gp/types/knowledge_bases/chunk_list_params.py">params</a>) -> <a href="./src/scale_gp/types/knowledge_bases/get_chunks_response.py">GetChunksResponse</a></code>

## DataSourceConnections

Types:

```python
from scale_gp.types.knowledge_bases import DeleteKnowledgeBaseDataSourceConnectionResponse
```

Methods:

- <code title="post /v4/knowledge-bases/{knowledge_base_id}/data-source-connections/{knowledge_base_data_source_id}/delete">client.knowledge_bases.data_source_connections.<a href="./src/scale_gp/resources/knowledge_bases/data_source_connections.py">delete</a>(knowledge_base_data_source_id, \*, knowledge_base_id, \*\*<a href="src/scale_gp/types/knowledge_bases/data_source_connection_delete_params.py">params</a>) -> <a href="./src/scale_gp/types/knowledge_bases/delete_knowledge_base_data_source_connection_response.py">DeleteKnowledgeBaseDataSourceConnectionResponse</a></code>

## Uploads

Types:

```python
from scale_gp.types.knowledge_bases import (
    CancelKnowledgeBaseV2UploadResponse,
    CreateKnowledgeBaseV2UploadResponse,
    GetKnowledgeBaseV2UploadResponse,
    KnowledgeBaseUploadList,
)
```

Methods:

- <code title="post /v4/knowledge-bases/{knowledge_base_id}/uploads">client.knowledge_bases.uploads.<a href="./src/scale_gp/resources/knowledge_bases/uploads.py">create</a>(knowledge_base_id, \*\*<a href="src/scale_gp/types/knowledge_bases/upload_create_params.py">params</a>) -> <a href="./src/scale_gp/types/knowledge_bases/create_knowledge_base_v2_upload_response.py">CreateKnowledgeBaseV2UploadResponse</a></code>
- <code title="get /v4/knowledge-bases/{knowledge_base_id}/uploads/{upload_id}">client.knowledge_bases.uploads.<a href="./src/scale_gp/resources/knowledge_bases/uploads.py">retrieve</a>(upload_id, \*, knowledge_base_id, \*\*<a href="src/scale_gp/types/knowledge_bases/upload_retrieve_params.py">params</a>) -> <a href="./src/scale_gp/types/knowledge_bases/get_knowledge_base_v2_upload_response.py">GetKnowledgeBaseV2UploadResponse</a></code>
- <code title="get /v4/knowledge-bases/{knowledge_base_id}/uploads">client.knowledge_bases.uploads.<a href="./src/scale_gp/resources/knowledge_bases/uploads.py">list</a>(knowledge_base_id, \*\*<a href="src/scale_gp/types/knowledge_bases/upload_list_params.py">params</a>) -> <a href="./src/scale_gp/types/knowledge_bases/knowledge_base_upload_list.py">KnowledgeBaseUploadList</a></code>
- <code title="post /v4/knowledge-bases/{knowledge_base_id}/uploads/{upload_id}/cancel">client.knowledge_bases.uploads.<a href="./src/scale_gp/resources/knowledge_bases/uploads.py">cancel</a>(upload_id, \*, knowledge_base_id) -> <a href="./src/scale_gp/types/knowledge_bases/cancel_knowledge_base_v2_upload_response.py">CancelKnowledgeBaseV2UploadResponse</a></code>

## Artifacts

Types:

```python
from scale_gp.types.knowledge_bases import ArtifactInfoList, GetKnowledgeBaseV2ArtifactResponse
```

Methods:

- <code title="get /v4/knowledge-bases/{knowledge_base_id}/artifacts/{artifact_id}">client.knowledge_bases.artifacts.<a href="./src/scale_gp/resources/knowledge_bases/artifacts.py">retrieve</a>(artifact_id, \*, knowledge_base_id, \*\*<a href="src/scale_gp/types/knowledge_bases/artifact_retrieve_params.py">params</a>) -> <a href="./src/scale_gp/types/knowledge_bases/get_knowledge_base_v2_artifact_response.py">GetKnowledgeBaseV2ArtifactResponse</a></code>
- <code title="get /v4/knowledge-bases/{knowledge_base_id}/artifacts">client.knowledge_bases.artifacts.<a href="./src/scale_gp/resources/knowledge_bases/artifacts.py">list</a>(knowledge_base_id, \*\*<a href="src/scale_gp/types/knowledge_bases/artifact_list_params.py">params</a>) -> <a href="./src/scale_gp/types/knowledge_bases/artifact_info_list.py">ArtifactInfoList</a></code>

## UploadSchedules

Types:

```python
from scale_gp.types.knowledge_bases import (
    KnowledgeBaseUploadScheduleResponse,
    KnowledgeBaseUploadScheduleResponseWithViews,
    UploadScheduleListResponse,
)
```

Methods:

- <code title="post /v4/knowledge-bases/{knowledge_base_id}/upload-schedules">client.knowledge_bases.upload_schedules.<a href="./src/scale_gp/resources/knowledge_bases/upload_schedules.py">create</a>(knowledge_base_id, \*\*<a href="src/scale_gp/types/knowledge_bases/upload_schedule_create_params.py">params</a>) -> <a href="./src/scale_gp/types/knowledge_bases/knowledge_base_upload_schedule_response.py">KnowledgeBaseUploadScheduleResponse</a></code>
- <code title="get /v4/knowledge-bases/{knowledge_base_id}/upload-schedules/{upload_schedule_id}">client.knowledge_bases.upload_schedules.<a href="./src/scale_gp/resources/knowledge_bases/upload_schedules.py">retrieve</a>(upload_schedule_id, \*, knowledge_base_id, \*\*<a href="src/scale_gp/types/knowledge_bases/upload_schedule_retrieve_params.py">params</a>) -> <a href="./src/scale_gp/types/knowledge_bases/knowledge_base_upload_schedule_response_with_views.py">KnowledgeBaseUploadScheduleResponseWithViews</a></code>
- <code title="patch /v4/knowledge-bases/{knowledge_base_id}/upload-schedules/{upload_schedule_id}">client.knowledge_bases.upload_schedules.<a href="./src/scale_gp/resources/knowledge_bases/upload_schedules.py">update</a>(upload_schedule_id, \*, knowledge_base_id, \*\*<a href="src/scale_gp/types/knowledge_bases/upload_schedule_update_params.py">params</a>) -> <a href="./src/scale_gp/types/knowledge_bases/knowledge_base_upload_schedule_response.py">KnowledgeBaseUploadScheduleResponse</a></code>
- <code title="get /v4/knowledge-bases/{knowledge_base_id}/upload-schedules">client.knowledge_bases.upload_schedules.<a href="./src/scale_gp/resources/knowledge_bases/upload_schedules.py">list</a>(knowledge_base_id, \*\*<a href="src/scale_gp/types/knowledge_bases/upload_schedule_list_params.py">params</a>) -> <a href="./src/scale_gp/types/knowledge_bases/upload_schedule_list_response.py">UploadScheduleListResponse</a></code>
- <code title="delete /v4/knowledge-bases/{knowledge_base_id}/upload-schedules/{upload_schedule_id}">client.knowledge_bases.upload_schedules.<a href="./src/scale_gp/resources/knowledge_bases/upload_schedules.py">delete</a>(upload_schedule_id, \*, knowledge_base_id) -> <a href="./src/scale_gp/types/shared/delete_response.py">DeleteResponse</a></code>

# KnowledgeBaseDataSources

Types:

```python
from scale_gp.types import (
    KnowledgeBaseDataSourceResponse,
    KnowledgeBaseDataSourceListResponse,
    KnowledgeBaseDataSourceVerifyResponse,
)
```

Methods:

- <code title="post /v4/knowledge-base-data-sources">client.knowledge_base_data_sources.<a href="./src/scale_gp/resources/knowledge_base_data_sources.py">create</a>(\*\*<a href="src/scale_gp/types/knowledge_base_data_source_create_params.py">params</a>) -> <a href="./src/scale_gp/types/knowledge_base_data_source_response.py">KnowledgeBaseDataSourceResponse</a></code>
- <code title="get /v4/knowledge-base-data-sources/{knowledge_base_data_source_id}">client.knowledge_base_data_sources.<a href="./src/scale_gp/resources/knowledge_base_data_sources.py">retrieve</a>(knowledge_base_data_source_id) -> <a href="./src/scale_gp/types/knowledge_base_data_source_response.py">KnowledgeBaseDataSourceResponse</a></code>
- <code title="patch /v4/knowledge-base-data-sources/{knowledge_base_data_source_id}">client.knowledge_base_data_sources.<a href="./src/scale_gp/resources/knowledge_base_data_sources.py">update</a>(knowledge_base_data_source_id, \*\*<a href="src/scale_gp/types/knowledge_base_data_source_update_params.py">params</a>) -> <a href="./src/scale_gp/types/knowledge_base_data_source_response.py">KnowledgeBaseDataSourceResponse</a></code>
- <code title="get /v4/knowledge-base-data-sources">client.knowledge_base_data_sources.<a href="./src/scale_gp/resources/knowledge_base_data_sources.py">list</a>(\*\*<a href="src/scale_gp/types/knowledge_base_data_source_list_params.py">params</a>) -> <a href="./src/scale_gp/types/knowledge_base_data_source_list_response.py">KnowledgeBaseDataSourceListResponse</a></code>
- <code title="delete /v4/knowledge-base-data-sources/{knowledge_base_data_source_id}">client.knowledge_base_data_sources.<a href="./src/scale_gp/resources/knowledge_base_data_sources.py">delete</a>(knowledge_base_data_source_id) -> <a href="./src/scale_gp/types/shared/delete_response.py">DeleteResponse</a></code>
- <code title="post /v4/knowledge-base-data-sources/{knowledge_base_data_source_id}/verify">client.knowledge_base_data_sources.<a href="./src/scale_gp/resources/knowledge_base_data_sources.py">verify</a>(knowledge_base_data_source_id) -> <a href="./src/scale_gp/types/knowledge_base_data_source_verify_response.py">object</a></code>

# Chunks

Types:

```python
from scale_gp.types import ChunksRankResponse, SynthesizeChunksResponse
```

Methods:

- <code title="post /v4/chunks/rank">client.chunks.<a href="./src/scale_gp/resources/chunks.py">rank</a>(\*\*<a href="src/scale_gp/types/chunk_rank_params.py">params</a>) -> <a href="./src/scale_gp/types/chunks_rank_response.py">ChunksRankResponse</a></code>
- <code title="post /v4/chunks/synthesis">client.chunks.<a href="./src/scale_gp/resources/chunks.py">synthesis</a>(\*\*<a href="src/scale_gp/types/chunk_synthesis_params.py">params</a>) -> <a href="./src/scale_gp/types/synthesize_chunks_response.py">SynthesizeChunksResponse</a></code>

# Agents

Types:

```python
from scale_gp.types import ExecuteAgentResponse
```

Methods:

- <code title="post /v4/agents/execute">client.agents.<a href="./src/scale_gp/resources/agents.py">execute</a>(\*\*<a href="src/scale_gp/types/agent_execute_params.py">params</a>) -> <a href="./src/scale_gp/types/execute_agent_response.py">ExecuteAgentResponse</a></code>

# Completions

Types:

```python
from scale_gp.types import CreateCompletionResponse
```

Methods:

- <code title="post /v4/completions">client.completions.<a href="./src/scale_gp/resources/completions.py">create</a>(\*\*<a href="src/scale_gp/types/completion_create_params.py">params</a>) -> <a href="./src/scale_gp/types/create_completion_response.py">CreateCompletionResponse</a></code>

# ChatCompletions

Types:

```python
from scale_gp.types import CreateChatCompletionResponse
```

Methods:

- <code title="post /v4/chat-completions">client.chat_completions.<a href="./src/scale_gp/resources/chat_completions.py">create</a>(\*\*<a href="src/scale_gp/types/chat_completion_create_params.py">params</a>) -> <a href="./src/scale_gp/types/create_chat_completion_response.py">CreateChatCompletionResponse</a></code>

# Models

Types:

```python
from scale_gp.types import (
    ModelInstanceResponse,
    ModelInstanceResponseWithViews,
    PaginationResponseListPydanticMainModelInstanceResponseWithViews,
)
```

Methods:

- <code title="post /v4/models">client.models.<a href="./src/scale_gp/resources/models/models.py">create</a>(\*\*<a href="src/scale_gp/types/model_create_params.py">params</a>) -> <a href="./src/scale_gp/types/model_instance_response.py">ModelInstanceResponse</a></code>
- <code title="get /v4/models/{model_id}">client.models.<a href="./src/scale_gp/resources/models/models.py">retrieve</a>(model_id, \*\*<a href="src/scale_gp/types/model_retrieve_params.py">params</a>) -> <a href="./src/scale_gp/types/model_instance_response_with_views.py">ModelInstanceResponseWithViews</a></code>
- <code title="patch /v4/models/{model_id}">client.models.<a href="./src/scale_gp/resources/models/models.py">update</a>(model_id, \*\*<a href="src/scale_gp/types/model_update_params.py">params</a>) -> <a href="./src/scale_gp/types/model_instance_response.py">ModelInstanceResponse</a></code>
- <code title="get /v4/models">client.models.<a href="./src/scale_gp/resources/models/models.py">list</a>(\*\*<a href="src/scale_gp/types/model_list_params.py">params</a>) -> <a href="./src/scale_gp/types/pagination_response_list_pydantic_main_model_instance_response_with_views.py">PaginationResponseListPydanticMainModelInstanceResponseWithViews</a></code>
- <code title="delete /v4/models/{model_id}">client.models.<a href="./src/scale_gp/resources/models/models.py">delete</a>(model_id) -> <a href="./src/scale_gp/types/shared/delete_response.py">DeleteResponse</a></code>

## Deployments

Types:

```python
from scale_gp.types.models import (
    CompletionResponse,
    EmbeddingResponse,
    ModelDeploymentResponse,
    ModelDeploymentResponse,
    RerankingResponse,
    DeploymentExecuteResponse,
)
```

Methods:

- <code title="post /v4/models/{model_instance_id}/deployments">client.models.deployments.<a href="./src/scale_gp/resources/models/deployments.py">create</a>(model_instance_id, \*\*<a href="src/scale_gp/types/models/deployment_create_params.py">params</a>) -> <a href="./src/scale_gp/types/models/model_deployment_response.py">ModelDeploymentResponse</a></code>
- <code title="get /v4/models/{model_instance_id}/deployments/{deployment_id}">client.models.deployments.<a href="./src/scale_gp/resources/models/deployments.py">retrieve</a>(deployment_id, \*, model_instance_id) -> <a href="./src/scale_gp/types/models/model_deployment_response.py">ModelDeploymentResponse</a></code>
- <code title="patch /v4/models/{model_instance_id}/deployments/{deployment_id}">client.models.deployments.<a href="./src/scale_gp/resources/models/deployments.py">update</a>(deployment_id, \*, model_instance_id, \*\*<a href="src/scale_gp/types/models/deployment_update_params.py">params</a>) -> <a href="./src/scale_gp/types/models/model_deployment_response.py">ModelDeploymentResponse</a></code>
- <code title="get /v4/models/{model_instance_id}/deployments">client.models.deployments.<a href="./src/scale_gp/resources/models/deployments.py">list</a>(model_instance_id, \*\*<a href="src/scale_gp/types/models/deployment_list_params.py">params</a>) -> <a href="./src/scale_gp/types/shared/pagination_response_model_deployment.py">PaginationResponseModelDeployment</a></code>
- <code title="delete /v4/models/{model_instance_id}/deployments/{deployment_id}">client.models.deployments.<a href="./src/scale_gp/resources/models/deployments.py">delete</a>(deployment_id, \*, model_instance_id) -> <a href="./src/scale_gp/types/shared/delete_response.py">DeleteResponse</a></code>
- <code title="post /v4/models/{model_deployment_id}/chat-completions">client.models.deployments.<a href="./src/scale_gp/resources/models/deployments.py">chat_completions</a>(model_deployment_id, \*\*<a href="src/scale_gp/types/models/deployment_chat_completions_params.py">params</a>) -> <a href="./src/scale_gp/types/models/completion_response.py">CompletionResponse</a></code>
- <code title="post /v4/models/{model_deployment_id}/completions">client.models.deployments.<a href="./src/scale_gp/resources/models/deployments.py">completions</a>(model_deployment_id, \*\*<a href="src/scale_gp/types/models/deployment_completions_params.py">params</a>) -> <a href="./src/scale_gp/types/models/completion_response.py">CompletionResponse</a></code>
- <code title="post /v4/models/{model_deployment_id}/embeddings">client.models.deployments.<a href="./src/scale_gp/resources/models/deployments.py">embeddings</a>(model_deployment_id, \*\*<a href="src/scale_gp/types/models/deployment_embeddings_params.py">params</a>) -> <a href="./src/scale_gp/types/models/embedding_response.py">EmbeddingResponse</a></code>
- <code title="post /v4/models/{model_instance_id}/deployments/{model_deployment_id}/execute">client.models.deployments.<a href="./src/scale_gp/resources/models/deployments.py">execute</a>(model_deployment_id, \*, model_instance_id) -> <a href="./src/scale_gp/types/models/deployment_execute_response.py">object</a></code>
- <code title="post /v4/models/{model_deployment_id}/rerankings">client.models.deployments.<a href="./src/scale_gp/resources/models/deployments.py">rerankings</a>(model_deployment_id, \*\*<a href="src/scale_gp/types/models/deployment_rerankings_params.py">params</a>) -> <a href="./src/scale_gp/types/models/reranking_response.py">RerankingResponse</a></code>

## UsageStatistics

Methods:

- <code title="get /v4/models/{model_name}/usage-statistics">client.models.usage_statistics.<a href="./src/scale_gp/resources/models/usage_statistics.py">retrieve</a>(model_name, \*\*<a href="src/scale_gp/types/models/usage_statistic_retrieve_params.py">params</a>) -> <a href="./src/scale_gp/types/shared/model_usage_response.py">ModelUsageResponse</a></code>

# ModelDeployments

Methods:

- <code title="get /v4/model-deployments">client.model_deployments.<a href="./src/scale_gp/resources/model_deployments/model_deployments.py">list</a>(\*\*<a href="src/scale_gp/types/model_deployment_list_params.py">params</a>) -> <a href="./src/scale_gp/types/shared/pagination_response_model_deployment.py">PaginationResponseModelDeployment</a></code>

## UsageStatistics

Methods:

- <code title="get /v4/model-deployments/{model_deployment_id}/usage-statistics">client.model_deployments.usage_statistics.<a href="./src/scale_gp/resources/model_deployments/usage_statistics.py">retrieve</a>(model_deployment_id, \*\*<a href="src/scale_gp/types/model_deployments/usage_statistic_retrieve_params.py">params</a>) -> <a href="./src/scale_gp/types/shared/model_usage_response.py">ModelUsageResponse</a></code>

# ModelGroups

Types:

```python
from scale_gp.types import (
    ModelGroupResponse,
    PaginationResponseListEgpAPIBackendServerAPIModelsModelAPIModelsModelGroupResponse,
)
```

Methods:

- <code title="post /v4/model-groups">client.model_groups.<a href="./src/scale_gp/resources/model_groups/model_groups.py">create</a>(\*\*<a href="src/scale_gp/types/model_group_create_params.py">params</a>) -> <a href="./src/scale_gp/types/model_group_response.py">ModelGroupResponse</a></code>
- <code title="get /v4/model-groups/{model_group_id}">client.model_groups.<a href="./src/scale_gp/resources/model_groups/model_groups.py">retrieve</a>(model_group_id) -> <a href="./src/scale_gp/types/model_group_response.py">ModelGroupResponse</a></code>
- <code title="patch /v4/model-groups/{model_group_id}">client.model_groups.<a href="./src/scale_gp/resources/model_groups/model_groups.py">update</a>(model_group_id, \*\*<a href="src/scale_gp/types/model_group_update_params.py">params</a>) -> <a href="./src/scale_gp/types/model_group_response.py">ModelGroupResponse</a></code>
- <code title="get /v4/model-groups">client.model_groups.<a href="./src/scale_gp/resources/model_groups/model_groups.py">list</a>(\*\*<a href="src/scale_gp/types/model_group_list_params.py">params</a>) -> <a href="./src/scale_gp/types/pagination_response_list_egp_api_backend_server_api_models_model_api_models_model_group_response.py">PaginationResponseListEgpAPIBackendServerAPIModelsModelAPIModelsModelGroupResponse</a></code>
- <code title="delete /v4/model-groups/{model_group_id}">client.model_groups.<a href="./src/scale_gp/resources/model_groups/model_groups.py">delete</a>(model_group_id) -> <a href="./src/scale_gp/types/shared/delete_response.py">DeleteResponse</a></code>

## Models

Types:

```python
from scale_gp.types.model_groups import ModelInstanceResponse
```

Methods:

- <code title="post /v4/model-groups/{model_group_id}/models/{model_instance_id}">client.model_groups.models.<a href="./src/scale_gp/resources/model_groups/models.py">create</a>(model_instance_id, \*, model_group_id) -> <a href="./src/scale_gp/types/model_instance_response.py">ModelInstanceResponse</a></code>

## UsageStatistics

Methods:

- <code title="get /v4/model-groups/{model_group_id}/usage-statistics">client.model_groups.usage_statistics.<a href="./src/scale_gp/resources/model_groups/usage_statistics.py">list</a>(model_group_id, \*\*<a href="src/scale_gp/types/model_groups/usage_statistic_list_params.py">params</a>) -> <a href="./src/scale_gp/types/shared/model_usage_response.py">ModelUsageResponse</a></code>

# Users

Types:

```python
from scale_gp.types import UserInfo
```

Methods:

- <code title="get /users/{user_id}">client.users.<a href="./src/scale_gp/resources/users.py">retrieve</a>(user_id) -> <a href="./src/scale_gp/types/user_info.py">UserInfo</a></code>
- <code title="get /user-info">client.users.<a href="./src/scale_gp/resources/users.py">info</a>() -> <a href="./src/scale_gp/types/user_info.py">UserInfo</a></code>

# Accounts

Types:

```python
from scale_gp.types import CreateAccountResponse
```

Methods:

- <code title="post /accounts">client.accounts.<a href="./src/scale_gp/resources/accounts.py">create</a>(\*\*<a href="src/scale_gp/types/account_create_params.py">params</a>) -> <a href="./src/scale_gp/types/create_account_response.py">CreateAccountResponse</a></code>

# QuestionSets

Types:

```python
from scale_gp.types import QuestionSetResponse, QuestionSetWithQuestions, QuestionSetListResponse
```

Methods:

- <code title="post /v4/question-sets">client.question_sets.<a href="./src/scale_gp/resources/question_sets.py">create</a>(\*\*<a href="src/scale_gp/types/question_set_create_params.py">params</a>) -> <a href="./src/scale_gp/types/question_set_response.py">QuestionSetResponse</a></code>
- <code title="get /v4/question-sets/{question_set_id}">client.question_sets.<a href="./src/scale_gp/resources/question_sets.py">retrieve</a>(question_set_id) -> <a href="./src/scale_gp/types/question_set_with_questions.py">QuestionSetWithQuestions</a></code>
- <code title="get /v4/question-sets">client.question_sets.<a href="./src/scale_gp/resources/question_sets.py">list</a>(\*\*<a href="src/scale_gp/types/question_set_list_params.py">params</a>) -> <a href="./src/scale_gp/types/question_set_list_response.py">QuestionSetListResponse</a></code>

# Evaluations

Types:

```python
from scale_gp.types import EvaluationResponse, EvaluationResponseWithViews, EvaluationListResponse
```

Methods:

- <code title="post /v4/evaluations">client.evaluations.<a href="./src/scale_gp/resources/evaluations/evaluations.py">create</a>(\*\*<a href="src/scale_gp/types/evaluation_create_params.py">params</a>) -> <a href="./src/scale_gp/types/evaluation_response.py">EvaluationResponse</a></code>
- <code title="get /v4/evaluations/{evaluation_id}">client.evaluations.<a href="./src/scale_gp/resources/evaluations/evaluations.py">retrieve</a>(evaluation_id, \*\*<a href="src/scale_gp/types/evaluation_retrieve_params.py">params</a>) -> <a href="./src/scale_gp/types/evaluation_response_with_views.py">EvaluationResponseWithViews</a></code>
- <code title="patch /v4/evaluations/{evaluation_id}">client.evaluations.<a href="./src/scale_gp/resources/evaluations/evaluations.py">update</a>(evaluation_id, \*\*<a href="src/scale_gp/types/evaluation_update_params.py">params</a>) -> <a href="./src/scale_gp/types/evaluation_response.py">EvaluationResponse</a></code>
- <code title="get /v4/evaluations">client.evaluations.<a href="./src/scale_gp/resources/evaluations/evaluations.py">list</a>(\*\*<a href="src/scale_gp/types/evaluation_list_params.py">params</a>) -> <a href="./src/scale_gp/types/evaluation_list_response.py">EvaluationListResponse</a></code>
- <code title="delete /v4/evaluations/{evaluation_id}">client.evaluations.<a href="./src/scale_gp/resources/evaluations/evaluations.py">delete</a>(evaluation_id) -> <a href="./src/scale_gp/types/shared/delete_response.py">DeleteResponse</a></code>
- <code title="post /v4/evaluations/{evaluation_id}/claim-task">client.evaluations.<a href="./src/scale_gp/resources/evaluations/evaluations.py">claim_task</a>(evaluation_id) -> <a href="./src/scale_gp/types/shared/task_response.py">TaskResponse</a></code>

## Tasks

Methods:

- <code title="patch /v4/evaluations/{evaluation_id}/tasks/{task_id}">client.evaluations.tasks.<a href="./src/scale_gp/resources/evaluations/tasks.py">update</a>(task_id, \*, evaluation_id, \*\*<a href="src/scale_gp/types/evaluations/task_update_params.py">params</a>) -> <a href="./src/scale_gp/types/shared/task_response.py">TaskResponse</a></code>

## ContributorMetrics

Types:

```python
from scale_gp.types.evaluations import (
    ContributorMetricsResponse,
    PaginationResponseContributorMetrics,
)
```

Methods:

- <code title="get /v4/evaluations/{evaluation_id}/contributor-metrics/{contributor_id}">client.evaluations.contributor_metrics.<a href="./src/scale_gp/resources/evaluations/contributor_metrics.py">retrieve</a>(contributor_id, \*, evaluation_id) -> <a href="./src/scale_gp/types/evaluations/contributor_metrics_response.py">ContributorMetricsResponse</a></code>
- <code title="get /v4/evaluations/{evaluation_id}/contributor-metrics">client.evaluations.contributor_metrics.<a href="./src/scale_gp/resources/evaluations/contributor_metrics.py">list</a>(evaluation_id, \*\*<a href="src/scale_gp/types/evaluations/contributor_metric_list_params.py">params</a>) -> <a href="./src/scale_gp/types/evaluations/pagination_response_contributor_metrics.py">PaginationResponseContributorMetrics</a></code>

## EvaluationMetrics

Types:

```python
from scale_gp.types.evaluations import EvaluationMetricsResponse
```

Methods:

- <code title="get /v4/evaluations/{evaluation_id}/evaluation-metrics">client.evaluations.evaluation_metrics.<a href="./src/scale_gp/resources/evaluations/evaluation_metrics.py">list</a>(evaluation_id) -> <a href="./src/scale_gp/types/evaluations/evaluation_metrics_response.py">EvaluationMetricsResponse</a></code>

## HybridEvalMetrics

Types:

```python
from scale_gp.types.evaluations import HybridEvaluationMetricsResponse
```

Methods:

- <code title="get /v4/evaluations/{evaluation_id}/hybrid-eval-metrics">client.evaluations.hybrid_eval_metrics.<a href="./src/scale_gp/resources/evaluations/hybrid_eval_metrics.py">list</a>(evaluation_id) -> <a href="./src/scale_gp/types/evaluations/hybrid_evaluation_metrics_response.py">HybridEvaluationMetricsResponse</a></code>

## TestCaseResults

Types:

```python
from scale_gp.types.evaluations import TestCaseResultListResponse, TestCaseResultBatchResponse
```

Methods:

- <code title="post /v4/evaluations/{evaluation_id}/test-case-results">client.evaluations.test_case_results.<a href="./src/scale_gp/resources/evaluations/test_case_results/test_case_results.py">create</a>(evaluation_id, \*\*<a href="src/scale_gp/types/evaluations/test_case_result_create_params.py">params</a>) -> <a href="./src/scale_gp/types/shared/test_case_result_response.py">TestCaseResultResponse</a></code>
- <code title="get /v4/evaluations/{evaluation_id}/test-case-results/{test_case_result_id}">client.evaluations.test_case_results.<a href="./src/scale_gp/resources/evaluations/test_case_results/test_case_results.py">retrieve</a>(test_case_result_id, \*, evaluation_id, \*\*<a href="src/scale_gp/types/evaluations/test_case_result_retrieve_params.py">params</a>) -> <a href="./src/scale_gp/types/shared/test_case_result_response_with_views.py">TestCaseResultResponseWithViews</a></code>
- <code title="patch /v4/evaluations/{evaluation_id}/test-case-results/{test_case_result_id}">client.evaluations.test_case_results.<a href="./src/scale_gp/resources/evaluations/test_case_results/test_case_results.py">update</a>(test_case_result_id, \*, evaluation_id, \*\*<a href="src/scale_gp/types/evaluations/test_case_result_update_params.py">params</a>) -> <a href="./src/scale_gp/types/shared/test_case_result_response.py">TestCaseResultResponse</a></code>
- <code title="get /v4/evaluations/{evaluation_id}/test-case-results">client.evaluations.test_case_results.<a href="./src/scale_gp/resources/evaluations/test_case_results/test_case_results.py">list</a>(evaluation_id, \*\*<a href="src/scale_gp/types/evaluations/test_case_result_list_params.py">params</a>) -> <a href="./src/scale_gp/types/evaluations/test_case_result_list_response.py">TestCaseResultListResponse</a></code>
- <code title="post /v4/evaluations/{evaluation_id}/test-case-results/batch">client.evaluations.test_case_results.<a href="./src/scale_gp/resources/evaluations/test_case_results/test_case_results.py">batch</a>(evaluation_id, \*\*<a href="src/scale_gp/types/evaluations/test_case_result_batch_params.py">params</a>) -> <a href="./src/scale_gp/types/evaluations/test_case_result_batch_response.py">TestCaseResultBatchResponse</a></code>

### History

Types:

```python
from scale_gp.types.evaluations.test_case_results import HistoryListResponse
```

Methods:

- <code title="get /v4/evaluations/{evaluation_id}/test-case-results/{test_case_result_id}/history/{num}">client.evaluations.test_case_results.history.<a href="./src/scale_gp/resources/evaluations/test_case_results/history.py">retrieve</a>(num, \*, evaluation_id, test_case_result_id) -> <a href="./src/scale_gp/types/shared/test_case_result_response.py">TestCaseResultResponse</a></code>
- <code title="get /v4/evaluations/{evaluation_id}/test-case-results/history/{num}">client.evaluations.test_case_results.history.<a href="./src/scale_gp/resources/evaluations/test_case_results/history.py">list</a>(num, \*, evaluation_id, \*\*<a href="src/scale_gp/types/evaluations/test_case_results/history_list_params.py">params</a>) -> <a href="./src/scale_gp/types/evaluations/test_case_results/history_list_response.py">HistoryListResponse</a></code>

# EvaluationConfigs

Types:

```python
from scale_gp.types import EvaluationConfigResponse, PaginationResponseEvaluationConfig
```

Methods:

- <code title="post /v4/evaluation-configs">client.evaluation_configs.<a href="./src/scale_gp/resources/evaluation_configs.py">create</a>(\*\*<a href="src/scale_gp/types/evaluation_config_create_params.py">params</a>) -> <a href="./src/scale_gp/types/evaluation_config_response.py">EvaluationConfigResponse</a></code>
- <code title="get /v4/evaluation-configs/{evaluation_config_id}">client.evaluation_configs.<a href="./src/scale_gp/resources/evaluation_configs.py">retrieve</a>(evaluation_config_id) -> <a href="./src/scale_gp/types/evaluation_config_response.py">EvaluationConfigResponse</a></code>
- <code title="get /v4/evaluation-configs">client.evaluation_configs.<a href="./src/scale_gp/resources/evaluation_configs.py">list</a>(\*\*<a href="src/scale_gp/types/evaluation_config_list_params.py">params</a>) -> <a href="./src/scale_gp/types/pagination_response_evaluation_config.py">PaginationResponseEvaluationConfig</a></code>
- <code title="delete /v4/evaluation-configs/{evaluation_config_id}">client.evaluation_configs.<a href="./src/scale_gp/resources/evaluation_configs.py">delete</a>(evaluation_config_id) -> <a href="./src/scale_gp/types/shared/delete_response.py">DeleteResponse</a></code>

# EvaluationDatasets

Types:

```python
from scale_gp.types import (
    AutoGeneratedDraftTestCaseApproveBatchResponse,
    EvaluationDatasetResponse,
    EvaluationDatasetResponse,
    PaginationResponseEvaluationDataset,
    PublishEvaluationDatasetDraftResponse,
)
```

Methods:

- <code title="post /v4/evaluation-datasets">client.evaluation_datasets.<a href="./src/scale_gp/resources/evaluation_datasets/evaluation_datasets.py">create</a>(\*\*<a href="src/scale_gp/types/evaluation_dataset_create_params.py">params</a>) -> <a href="./src/scale_gp/types/evaluation_dataset_response.py">EvaluationDatasetResponse</a></code>
- <code title="get /v4/evaluation-datasets/{evaluation_dataset_id}">client.evaluation_datasets.<a href="./src/scale_gp/resources/evaluation_datasets/evaluation_datasets.py">retrieve</a>(evaluation_dataset_id) -> <a href="./src/scale_gp/types/evaluation_dataset_response.py">EvaluationDatasetResponse</a></code>
- <code title="patch /v4/evaluation-datasets/{evaluation_dataset_id}">client.evaluation_datasets.<a href="./src/scale_gp/resources/evaluation_datasets/evaluation_datasets.py">update</a>(evaluation_dataset_id, \*\*<a href="src/scale_gp/types/evaluation_dataset_update_params.py">params</a>) -> <a href="./src/scale_gp/types/evaluation_dataset_response.py">EvaluationDatasetResponse</a></code>
- <code title="get /v4/evaluation-datasets">client.evaluation_datasets.<a href="./src/scale_gp/resources/evaluation_datasets/evaluation_datasets.py">list</a>(\*\*<a href="src/scale_gp/types/evaluation_dataset_list_params.py">params</a>) -> <a href="./src/scale_gp/types/pagination_response_evaluation_dataset.py">PaginationResponseEvaluationDataset</a></code>
- <code title="delete /v4/evaluation-datasets/{evaluation_dataset_id}">client.evaluation_datasets.<a href="./src/scale_gp/resources/evaluation_datasets/evaluation_datasets.py">delete</a>(evaluation_dataset_id) -> <a href="./src/scale_gp/types/shared/delete_response.py">DeleteResponse</a></code>
- <code title="post /v4/evaluation-datasets/{evaluation_dataset_id}/approve-batch">client.evaluation_datasets.<a href="./src/scale_gp/resources/evaluation_datasets/evaluation_datasets.py">approve_batch</a>(evaluation_dataset_id, \*\*<a href="src/scale_gp/types/evaluation_dataset_approve_batch_params.py">params</a>) -> <a href="./src/scale_gp/types/auto_generated_draft_test_case_approve_batch_response.py">AutoGeneratedDraftTestCaseApproveBatchResponse</a></code>
- <code title="post /v4/evaluation-datasets/{evaluation_dataset_id}/publish">client.evaluation_datasets.<a href="./src/scale_gp/resources/evaluation_datasets/evaluation_datasets.py">publish</a>(evaluation_dataset_id, \*\*<a href="src/scale_gp/types/evaluation_dataset_publish_params.py">params</a>) -> <a href="./src/scale_gp/types/publish_evaluation_dataset_draft_response.py">PublishEvaluationDatasetDraftResponse</a></code>

## EvaluationDatasetVersions

Types:

```python
from scale_gp.types.evaluation_datasets import (
    EvaluationDatasetVersionResponse,
    EvaluationDatasetVersionListResponse,
)
```

Methods:

- <code title="post /v4/evaluation-datasets/{evaluation_dataset_id}/evaluation-dataset-versions">client.evaluation_datasets.evaluation_dataset_versions.<a href="./src/scale_gp/resources/evaluation_datasets/evaluation_dataset_versions.py">create</a>(evaluation_dataset_id, \*\*<a href="src/scale_gp/types/evaluation_datasets/evaluation_dataset_version_create_params.py">params</a>) -> <a href="./src/scale_gp/types/evaluation_datasets/evaluation_dataset_version_response.py">EvaluationDatasetVersionResponse</a></code>
- <code title="get /v4/evaluation-datasets/{evaluation_dataset_id}/evaluation-dataset-versions/{evaluation_dataset_version_id}">client.evaluation_datasets.evaluation_dataset_versions.<a href="./src/scale_gp/resources/evaluation_datasets/evaluation_dataset_versions.py">retrieve</a>(evaluation_dataset_version_id, \*, evaluation_dataset_id) -> <a href="./src/scale_gp/types/evaluation_datasets/evaluation_dataset_version_response.py">EvaluationDatasetVersionResponse</a></code>
- <code title="get /v4/evaluation-datasets/{evaluation_dataset_id}/evaluation-dataset-versions">client.evaluation_datasets.evaluation_dataset_versions.<a href="./src/scale_gp/resources/evaluation_datasets/evaluation_dataset_versions.py">list</a>(evaluation_dataset_id, \*\*<a href="src/scale_gp/types/evaluation_datasets/evaluation_dataset_version_list_params.py">params</a>) -> <a href="./src/scale_gp/types/evaluation_datasets/evaluation_dataset_version_list_response.py">EvaluationDatasetVersionListResponse</a></code>

## TestCases

Types:

```python
from scale_gp.types.evaluation_datasets import TestCaseListResponse, TestCaseBatchResponse
```

Methods:

- <code title="post /v4/evaluation-datasets/{evaluation_dataset_id}/test-cases">client.evaluation_datasets.test_cases.<a href="./src/scale_gp/resources/evaluation_datasets/test_cases/test_cases.py">create</a>(evaluation_dataset_id, \*\*<a href="src/scale_gp/types/evaluation_datasets/test_case_create_params.py">params</a>) -> <a href="./src/scale_gp/types/shared/test_case_version_response.py">TestCaseVersionResponse</a></code>
- <code title="get /v4/evaluation-datasets/{evaluation_dataset_id}/test-cases/{test_case_id}">client.evaluation_datasets.test_cases.<a href="./src/scale_gp/resources/evaluation_datasets/test_cases/test_cases.py">retrieve</a>(test_case_id, \*, evaluation_dataset_id) -> <a href="./src/scale_gp/types/shared/test_case_version_response.py">TestCaseVersionResponse</a></code>
- <code title="patch /v4/evaluation-datasets/{evaluation_dataset_id}/test-cases/{test_case_id}">client.evaluation_datasets.test_cases.<a href="./src/scale_gp/resources/evaluation_datasets/test_cases/test_cases.py">update</a>(test_case_id, \*, evaluation_dataset_id, \*\*<a href="src/scale_gp/types/evaluation_datasets/test_case_update_params.py">params</a>) -> <a href="./src/scale_gp/types/shared/test_case_version_response.py">TestCaseVersionResponse</a></code>
- <code title="get /v4/evaluation-datasets/{evaluation_dataset_id}/test-cases">client.evaluation_datasets.test_cases.<a href="./src/scale_gp/resources/evaluation_datasets/test_cases/test_cases.py">list</a>(evaluation_dataset_id, \*\*<a href="src/scale_gp/types/evaluation_datasets/test_case_list_params.py">params</a>) -> <a href="./src/scale_gp/types/evaluation_datasets/test_case_list_response.py">TestCaseListResponse</a></code>
- <code title="delete /v4/evaluation-datasets/{evaluation_dataset_id}/test-cases/{test_case_id}">client.evaluation_datasets.test_cases.<a href="./src/scale_gp/resources/evaluation_datasets/test_cases/test_cases.py">delete</a>(test_case_id, \*, evaluation_dataset_id) -> <a href="./src/scale_gp/types/shared/delete_response.py">DeleteResponse</a></code>
- <code title="post /v4/evaluation-datasets/{evaluation_dataset_id}/test-cases/batch">client.evaluation_datasets.test_cases.<a href="./src/scale_gp/resources/evaluation_datasets/test_cases/test_cases.py">batch</a>(evaluation_dataset_id, \*\*<a href="src/scale_gp/types/evaluation_datasets/test_case_batch_params.py">params</a>) -> <a href="./src/scale_gp/types/evaluation_datasets/test_case_batch_response.py">TestCaseBatchResponse</a></code>

### History

Types:

```python
from scale_gp.types.evaluation_datasets.test_cases import HistoryListResponse
```

Methods:

- <code title="get /v4/evaluation-datasets/{evaluation_dataset_id}/test-cases/{test_case_id}/history/{num}">client.evaluation_datasets.test_cases.history.<a href="./src/scale_gp/resources/evaluation_datasets/test_cases/history.py">retrieve</a>(num, \*, evaluation_dataset_id, test_case_id) -> <a href="./src/scale_gp/types/shared/test_case_version_response.py">TestCaseVersionResponse</a></code>
- <code title="get /v4/evaluation-datasets/{evaluation_dataset_id}/test-cases/history/{num}">client.evaluation_datasets.test_cases.history.<a href="./src/scale_gp/resources/evaluation_datasets/test_cases/history.py">list</a>(num, \*, evaluation_dataset_id, \*\*<a href="src/scale_gp/types/evaluation_datasets/test_cases/history_list_params.py">params</a>) -> <a href="./src/scale_gp/types/evaluation_datasets/test_cases/history_list_response.py">HistoryListResponse</a></code>
- <code title="delete /v4/evaluation-datasets/{evaluation_dataset_id}/test-cases/{test_case_id}/history">client.evaluation_datasets.test_cases.history.<a href="./src/scale_gp/resources/evaluation_datasets/test_cases/history.py">delete</a>(test_case_id, \*, evaluation_dataset_id) -> <a href="./src/scale_gp/types/shared/delete_response.py">DeleteResponse</a></code>

## AutogeneratedDraftTestCases

Types:

```python
from scale_gp.types.evaluation_datasets import (
    AutoGeneratedDraftTestCaseResponse,
    AutogeneratedDraftTestCaseListResponse,
    AutogeneratedDraftTestCaseApproveResponse,
)
```

Methods:

- <code title="post /v4/evaluation-datasets/{evaluation_dataset_id}/autogenerated-draft-test-cases">client.evaluation_datasets.autogenerated_draft_test_cases.<a href="./src/scale_gp/resources/evaluation_datasets/autogenerated_draft_test_cases.py">create</a>(evaluation_dataset_id, \*\*<a href="src/scale_gp/types/evaluation_datasets/autogenerated_draft_test_case_create_params.py">params</a>) -> <a href="./src/scale_gp/types/evaluation_datasets/auto_generated_draft_test_case_response.py">AutoGeneratedDraftTestCaseResponse</a></code>
- <code title="get /v4/evaluation-datasets/{evaluation_dataset_id}/autogenerated-draft-test-cases/{autogenerated_draft_test_case_id}">client.evaluation_datasets.autogenerated_draft_test_cases.<a href="./src/scale_gp/resources/evaluation_datasets/autogenerated_draft_test_cases.py">retrieve</a>(autogenerated_draft_test_case_id, \*, evaluation_dataset_id) -> <a href="./src/scale_gp/types/evaluation_datasets/auto_generated_draft_test_case_response.py">AutoGeneratedDraftTestCaseResponse</a></code>
- <code title="patch /v4/evaluation-datasets/{evaluation_dataset_id}/autogenerated-draft-test-cases/{autogenerated_draft_test_case_id}">client.evaluation_datasets.autogenerated_draft_test_cases.<a href="./src/scale_gp/resources/evaluation_datasets/autogenerated_draft_test_cases.py">update</a>(autogenerated_draft_test_case_id, \*, evaluation_dataset_id, \*\*<a href="src/scale_gp/types/evaluation_datasets/autogenerated_draft_test_case_update_params.py">params</a>) -> <a href="./src/scale_gp/types/evaluation_datasets/auto_generated_draft_test_case_response.py">AutoGeneratedDraftTestCaseResponse</a></code>
- <code title="get /v4/evaluation-datasets/{evaluation_dataset_id}/autogenerated-draft-test-cases">client.evaluation_datasets.autogenerated_draft_test_cases.<a href="./src/scale_gp/resources/evaluation_datasets/autogenerated_draft_test_cases.py">list</a>(evaluation_dataset_id, \*\*<a href="src/scale_gp/types/evaluation_datasets/autogenerated_draft_test_case_list_params.py">params</a>) -> <a href="./src/scale_gp/types/evaluation_datasets/autogenerated_draft_test_case_list_response.py">AutogeneratedDraftTestCaseListResponse</a></code>
- <code title="delete /v4/evaluation-datasets/{evaluation_dataset_id}/autogenerated-draft-test-cases/{autogenerated_draft_test_case_id}">client.evaluation_datasets.autogenerated_draft_test_cases.<a href="./src/scale_gp/resources/evaluation_datasets/autogenerated_draft_test_cases.py">delete</a>(autogenerated_draft_test_case_id, \*, evaluation_dataset_id) -> <a href="./src/scale_gp/types/shared/delete_response.py">DeleteResponse</a></code>
- <code title="post /v4/evaluation-datasets/{evaluation_dataset_id}/autogenerated-draft-test-cases/{autogenerated_draft_test_case_id}/approve">client.evaluation_datasets.autogenerated_draft_test_cases.<a href="./src/scale_gp/resources/evaluation_datasets/autogenerated_draft_test_cases.py">approve</a>(autogenerated_draft_test_case_id, \*, evaluation_dataset_id, \*\*<a href="src/scale_gp/types/evaluation_datasets/autogenerated_draft_test_case_approve_params.py">params</a>) -> <a href="./src/scale_gp/types/evaluation_datasets/autogenerated_draft_test_case_approve_response.py">AutogeneratedDraftTestCaseApproveResponse</a></code>

## GenerationJobs

Types:

```python
from scale_gp.types.evaluation_datasets import (
    CreateEvaluationDatasetGenerationJobResponse,
    GetEvaluationDatasetGenerationJobResponse,
    ListEvaluationDatasetGenerationJobsResponse,
    GenerationJobCancelResponse,
)
```

Methods:

- <code title="post /v4/evaluation-datasets/{evaluation_dataset_id}/generation-jobs">client.evaluation_datasets.generation_jobs.<a href="./src/scale_gp/resources/evaluation_datasets/generation_jobs.py">create</a>(evaluation_dataset_id, \*\*<a href="src/scale_gp/types/evaluation_datasets/generation_job_create_params.py">params</a>) -> <a href="./src/scale_gp/types/evaluation_datasets/create_evaluation_dataset_generation_job_response.py">CreateEvaluationDatasetGenerationJobResponse</a></code>
- <code title="get /v4/evaluation-datasets/{evaluation_dataset_id}/generation-jobs/{generation_job_id}">client.evaluation_datasets.generation_jobs.<a href="./src/scale_gp/resources/evaluation_datasets/generation_jobs.py">retrieve</a>(generation_job_id, \*, evaluation_dataset_id) -> <a href="./src/scale_gp/types/evaluation_datasets/get_evaluation_dataset_generation_job_response.py">GetEvaluationDatasetGenerationJobResponse</a></code>
- <code title="get /v4/evaluation-datasets/{evaluation_dataset_id}/generation-jobs">client.evaluation_datasets.generation_jobs.<a href="./src/scale_gp/resources/evaluation_datasets/generation_jobs.py">list</a>(evaluation_dataset_id) -> <a href="./src/scale_gp/types/evaluation_datasets/list_evaluation_dataset_generation_jobs_response.py">ListEvaluationDatasetGenerationJobsResponse</a></code>
- <code title="post /v4/evaluation-datasets/{evaluation_dataset_id}/generation-jobs/{generation_job_id}/cancel">client.evaluation_datasets.generation_jobs.<a href="./src/scale_gp/resources/evaluation_datasets/generation_jobs.py">cancel</a>(generation_job_id, \*, evaluation_dataset_id) -> <a href="./src/scale_gp/types/evaluation_datasets/generation_job_cancel_response.py">object</a></code>

# StudioProjects

Types:

```python
from scale_gp.types import StudioProjectResponse, StudioProjectListResponse
```

Methods:

- <code title="post /v4/studio-projects">client.studio_projects.<a href="./src/scale_gp/resources/studio_projects.py">create</a>(\*\*<a href="src/scale_gp/types/studio_project_create_params.py">params</a>) -> <a href="./src/scale_gp/types/studio_project_response.py">StudioProjectResponse</a></code>
- <code title="get /v4/studio-projects/{studio_project_id}">client.studio_projects.<a href="./src/scale_gp/resources/studio_projects.py">retrieve</a>(studio_project_id) -> <a href="./src/scale_gp/types/studio_project_response.py">StudioProjectResponse</a></code>
- <code title="patch /v4/studio-projects/{studio_project_id}">client.studio_projects.<a href="./src/scale_gp/resources/studio_projects.py">update</a>(studio_project_id, \*\*<a href="src/scale_gp/types/studio_project_update_params.py">params</a>) -> <a href="./src/scale_gp/types/studio_project_response.py">StudioProjectResponse</a></code>
- <code title="get /v4/studio-projects">client.studio_projects.<a href="./src/scale_gp/resources/studio_projects.py">list</a>(\*\*<a href="src/scale_gp/types/studio_project_list_params.py">params</a>) -> <a href="./src/scale_gp/types/studio_project_list_response.py">StudioProjectListResponse</a></code>
- <code title="delete /v4/studio-projects/{studio_project_id}">client.studio_projects.<a href="./src/scale_gp/resources/studio_projects.py">delete</a>(studio_project_id) -> <a href="./src/scale_gp/types/shared/delete_response.py">DeleteResponse</a></code>

# ApplicationSpecs

Types:

```python
from scale_gp.types import ApplicationSpecResponse, ApplicationSpecListResponse
```

Methods:

- <code title="post /v4/application-specs">client.application_specs.<a href="./src/scale_gp/resources/application_specs.py">create</a>(\*\*<a href="src/scale_gp/types/application_spec_create_params.py">params</a>) -> <a href="./src/scale_gp/types/application_spec_response.py">ApplicationSpecResponse</a></code>
- <code title="get /v4/application-specs/{application_spec_id}">client.application_specs.<a href="./src/scale_gp/resources/application_specs.py">retrieve</a>(application_spec_id) -> <a href="./src/scale_gp/types/application_spec_response.py">ApplicationSpecResponse</a></code>
- <code title="patch /v4/application-specs/{application_spec_id}">client.application_specs.<a href="./src/scale_gp/resources/application_specs.py">update</a>(application_spec_id, \*\*<a href="src/scale_gp/types/application_spec_update_params.py">params</a>) -> <a href="./src/scale_gp/types/application_spec_response.py">ApplicationSpecResponse</a></code>
- <code title="get /v4/application-specs">client.application_specs.<a href="./src/scale_gp/resources/application_specs.py">list</a>(\*\*<a href="src/scale_gp/types/application_spec_list_params.py">params</a>) -> <a href="./src/scale_gp/types/application_spec_list_response.py">ApplicationSpecListResponse</a></code>
- <code title="delete /v4/application-specs/{application_spec_id}">client.application_specs.<a href="./src/scale_gp/resources/application_specs.py">delete</a>(application_spec_id) -> <a href="./src/scale_gp/types/shared/delete_response.py">DeleteResponse</a></code>

# Questions

Types:

```python
from scale_gp.types import QuestionResponse, QuestionListResponse
```

Methods:

- <code title="post /v4/questions">client.questions.<a href="./src/scale_gp/resources/questions.py">create</a>(\*\*<a href="src/scale_gp/types/question_create_params.py">params</a>) -> <a href="./src/scale_gp/types/question_response.py">QuestionResponse</a></code>
- <code title="get /v4/questions/{question_id}">client.questions.<a href="./src/scale_gp/resources/questions.py">retrieve</a>(question_id) -> <a href="./src/scale_gp/types/question_response.py">QuestionResponse</a></code>
- <code title="get /v4/questions">client.questions.<a href="./src/scale_gp/resources/questions.py">list</a>(\*\*<a href="src/scale_gp/types/question_list_params.py">params</a>) -> <a href="./src/scale_gp/types/question_list_response.py">QuestionListResponse</a></code>

# ModelTemplates

Types:

```python
from scale_gp.types import (
    ModelTemplateResponse,
    PaginationResponseListEgpAPIBackendServerAPIModelsModelAPIModelsModelTemplateResponse,
)
```

Methods:

- <code title="post /v4/model-templates">client.model_templates.<a href="./src/scale_gp/resources/model_templates.py">create</a>(\*\*<a href="src/scale_gp/types/model_template_create_params.py">params</a>) -> <a href="./src/scale_gp/types/model_template_response.py">ModelTemplateResponse</a></code>
- <code title="get /v4/model-templates/{model_template_id}">client.model_templates.<a href="./src/scale_gp/resources/model_templates.py">retrieve</a>(model_template_id) -> <a href="./src/scale_gp/types/model_template_response.py">ModelTemplateResponse</a></code>
- <code title="get /v4/model-templates">client.model_templates.<a href="./src/scale_gp/resources/model_templates.py">list</a>(\*\*<a href="src/scale_gp/types/model_template_list_params.py">params</a>) -> <a href="./src/scale_gp/types/pagination_response_list_egp_api_backend_server_api_models_model_api_models_model_template_response.py">PaginationResponseListEgpAPIBackendServerAPIModelsModelAPIModelsModelTemplateResponse</a></code>
- <code title="delete /v4/model-templates/{model_template_id}">client.model_templates.<a href="./src/scale_gp/resources/model_templates.py">delete</a>(model_template_id) -> <a href="./src/scale_gp/types/shared/delete_response.py">DeleteResponse</a></code>

# FineTuningJobs

Types:

```python
from scale_gp.types import (
    FineTuningJobEvent,
    FineTuningJobResponse,
    PaginationResponseListEgpAPIBackendServerAPIModelsFineTuningJobModelsFineTuningJobResponse,
)
```

Methods:

- <code title="post /v4/fine-tuning-jobs">client.fine_tuning_jobs.<a href="./src/scale_gp/resources/fine_tuning_jobs/fine_tuning_jobs.py">create</a>(\*\*<a href="src/scale_gp/types/fine_tuning_job_create_params.py">params</a>) -> <a href="./src/scale_gp/types/fine_tuning_job_response.py">FineTuningJobResponse</a></code>
- <code title="get /v4/fine-tuning-jobs/{fine_tuning_job_id}">client.fine_tuning_jobs.<a href="./src/scale_gp/resources/fine_tuning_jobs/fine_tuning_jobs.py">retrieve</a>(fine_tuning_job_id) -> <a href="./src/scale_gp/types/fine_tuning_job_response.py">FineTuningJobResponse</a></code>
- <code title="get /v4/fine-tuning-jobs">client.fine_tuning_jobs.<a href="./src/scale_gp/resources/fine_tuning_jobs/fine_tuning_jobs.py">list</a>(\*\*<a href="src/scale_gp/types/fine_tuning_job_list_params.py">params</a>) -> <a href="./src/scale_gp/types/pagination_response_list_egp_api_backend_server_api_models_fine_tuning_job_models_fine_tuning_job_response.py">PaginationResponseListEgpAPIBackendServerAPIModelsFineTuningJobModelsFineTuningJobResponse</a></code>
- <code title="delete /v4/fine-tuning-jobs/{fine_tuning_job_id}">client.fine_tuning_jobs.<a href="./src/scale_gp/resources/fine_tuning_jobs/fine_tuning_jobs.py">delete</a>(fine_tuning_job_id) -> <a href="./src/scale_gp/types/shared/delete_response.py">DeleteResponse</a></code>

## Events

Types:

```python
from scale_gp.types.fine_tuning_jobs import EventListResponse
```

Methods:

- <code title="get /v4/fine-tuning-jobs/{fine_tuning_job_id}/events">client.fine_tuning_jobs.events.<a href="./src/scale_gp/resources/fine_tuning_jobs/events.py">list</a>(fine_tuning_job_id) -> <a href="./src/scale_gp/types/fine_tuning_jobs/event_list_response.py">EventListResponse</a></code>

# TrainingDatasets

Types:

```python
from scale_gp.types import (
    PaginationResponseListEgpAPIBackendServerAPIModelsFineTuningJobModelsTrainingDatasetResponse,
    TrainingDatasetResponse,
)
```

Methods:

- <code title="post /v4/training-datasets">client.training_datasets.<a href="./src/scale_gp/resources/training_datasets/training_datasets.py">create</a>(\*\*<a href="src/scale_gp/types/training_dataset_create_params.py">params</a>) -> <a href="./src/scale_gp/types/training_dataset_response.py">TrainingDatasetResponse</a></code>
- <code title="get /v4/training-datasets/{training_dataset_id}">client.training_datasets.<a href="./src/scale_gp/resources/training_datasets/training_datasets.py">retrieve</a>(training_dataset_id) -> <a href="./src/scale_gp/types/training_dataset_response.py">TrainingDatasetResponse</a></code>
- <code title="get /v4/training-datasets">client.training_datasets.<a href="./src/scale_gp/resources/training_datasets/training_datasets.py">list</a>(\*\*<a href="src/scale_gp/types/training_dataset_list_params.py">params</a>) -> <a href="./src/scale_gp/types/pagination_response_list_egp_api_backend_server_api_models_fine_tuning_job_models_training_dataset_response.py">PaginationResponseListEgpAPIBackendServerAPIModelsFineTuningJobModelsTrainingDatasetResponse</a></code>
- <code title="delete /v4/training-datasets/{training_dataset_id}">client.training_datasets.<a href="./src/scale_gp/resources/training_datasets/training_datasets.py">delete</a>(training_dataset_id) -> <a href="./src/scale_gp/types/shared/delete_response.py">DeleteResponse</a></code>

## Contents

Types:

```python
from scale_gp.types.training_datasets import TrainingDatasetGenerationItem, ContentListResponse
```

Methods:

- <code title="get /v4/training-datasets/{training_dataset_id}/contents">client.training_datasets.contents.<a href="./src/scale_gp/resources/training_datasets/contents.py">list</a>(training_dataset_id) -> <a href="./src/scale_gp/types/training_datasets/content_list_response.py">ContentListResponse</a></code>

# ApplicationVariants

Types:

```python
from scale_gp.types import (
    ApplicationVariantCreateResponse,
    ApplicationVariantRetrieveResponse,
    ApplicationVariantListResponse,
)
```

Methods:

- <code title="post /v4/application-variants">client.application_variants.<a href="./src/scale_gp/resources/application_variants.py">create</a>(\*\*<a href="src/scale_gp/types/application_variant_create_params.py">params</a>) -> <a href="./src/scale_gp/types/application_variant_create_response.py">ApplicationVariantCreateResponse</a></code>
- <code title="get /v4/application-variants/{application_variant_id}">client.application_variants.<a href="./src/scale_gp/resources/application_variants.py">retrieve</a>(application_variant_id) -> <a href="./src/scale_gp/types/application_variant_retrieve_response.py">ApplicationVariantRetrieveResponse</a></code>
- <code title="get /v4/application-variants">client.application_variants.<a href="./src/scale_gp/resources/application_variants.py">list</a>(\*\*<a href="src/scale_gp/types/application_variant_list_params.py">params</a>) -> <a href="./src/scale_gp/types/application_variant_list_response.py">ApplicationVariantListResponse</a></code>
- <code title="delete /v4/application-variants/{application_variant_id}">client.application_variants.<a href="./src/scale_gp/resources/application_variants.py">delete</a>(application_variant_id) -> <a href="./src/scale_gp/types/shared/delete_response.py">DeleteResponse</a></code>

# ApplicationDeployments

Types:

```python
from scale_gp.types import (
    ApplicationDeploymentResponse,
    PaginationResponseListEgpAPIBackendServerAPIModelsApplicationModelsApplicationDeploymentResponse,
)
```

Methods:

- <code title="post /v4/application-deployments">client.application_deployments.<a href="./src/scale_gp/resources/application_deployments.py">create</a>(\*\*<a href="src/scale_gp/types/application_deployment_create_params.py">params</a>) -> <a href="./src/scale_gp/types/application_deployment_response.py">ApplicationDeploymentResponse</a></code>
- <code title="get /v4/application-deployments/{application_deployment_id}">client.application_deployments.<a href="./src/scale_gp/resources/application_deployments.py">retrieve</a>(application_deployment_id) -> <a href="./src/scale_gp/types/application_deployment_response.py">ApplicationDeploymentResponse</a></code>
- <code title="patch /v4/application-deployments/{application_deployment_id}">client.application_deployments.<a href="./src/scale_gp/resources/application_deployments.py">update</a>(application_deployment_id, \*\*<a href="src/scale_gp/types/application_deployment_update_params.py">params</a>) -> <a href="./src/scale_gp/types/application_deployment_response.py">ApplicationDeploymentResponse</a></code>
- <code title="get /v4/application-deployments">client.application_deployments.<a href="./src/scale_gp/resources/application_deployments.py">list</a>(\*\*<a href="src/scale_gp/types/application_deployment_list_params.py">params</a>) -> <a href="./src/scale_gp/types/pagination_response_list_egp_api_backend_server_api_models_application_models_application_deployment_response.py">PaginationResponseListEgpAPIBackendServerAPIModelsApplicationModelsApplicationDeploymentResponse</a></code>

# ApplicationVariantReports

Types:

```python
from scale_gp.types import (
    ApplicationVariantReportWithScoresResponse,
    ApplicationVariantReportWithScoresResponseWithViews,
    PaginationResponseListPydanticMainApplicationVariantReportWithScoresResponseWithViews,
)
```

Methods:

- <code title="post /v4/application-variant-reports">client.application_variant_reports.<a href="./src/scale_gp/resources/application_variant_reports.py">create</a>(\*\*<a href="src/scale_gp/types/application_variant_report_create_params.py">params</a>) -> <a href="./src/scale_gp/types/application_variant_report_with_scores_response.py">ApplicationVariantReportWithScoresResponse</a></code>
- <code title="get /v4/application-variant-reports/{application_variant_report_id}">client.application_variant_reports.<a href="./src/scale_gp/resources/application_variant_reports.py">retrieve</a>(application_variant_report_id, \*\*<a href="src/scale_gp/types/application_variant_report_retrieve_params.py">params</a>) -> <a href="./src/scale_gp/types/application_variant_report_with_scores_response_with_views.py">ApplicationVariantReportWithScoresResponseWithViews</a></code>
- <code title="get /v4/application-variant-reports">client.application_variant_reports.<a href="./src/scale_gp/resources/application_variant_reports.py">list</a>(\*\*<a href="src/scale_gp/types/application_variant_report_list_params.py">params</a>) -> <a href="./src/scale_gp/types/pagination_response_list_pydantic_main_application_variant_report_with_scores_response_with_views.py">PaginationResponseListPydanticMainApplicationVariantReportWithScoresResponseWithViews</a></code>

# ApplicationTestCaseOutputs

Types:

```python
from scale_gp.types import ApplicationTestCaseOutput, ApplicationTestCaseOutputListResponse
```

Methods:

- <code title="get /v4/application-test-case-outputs/{application_test_case_output_id}">client.application_test_case_outputs.<a href="./src/scale_gp/resources/application_test_case_outputs.py">retrieve</a>(application_test_case_output_id, \*\*<a href="src/scale_gp/types/application_test_case_output_retrieve_params.py">params</a>) -> <a href="./src/scale_gp/types/application_test_case_output.py">ApplicationTestCaseOutput</a></code>
- <code title="get /v4/application-test-case-outputs">client.application_test_case_outputs.<a href="./src/scale_gp/resources/application_test_case_outputs.py">list</a>(\*\*<a href="src/scale_gp/types/application_test_case_output_list_params.py">params</a>) -> <a href="./src/scale_gp/types/application_test_case_output_list_response.py">ApplicationTestCaseOutputListResponse</a></code>

# ApplicationSchemas

Types:

```python
from scale_gp.types import ApplicationNodeSchemaRegistryRecord, ApplicationSchemaListResponse
```

Methods:

- <code title="get /v4/application-schemas">client.application_schemas.<a href="./src/scale_gp/resources/application_schemas.py">list</a>(\*\*<a href="src/scale_gp/types/application_schema_list_params.py">params</a>) -> <a href="./src/scale_gp/types/application_schema_list_response.py">ApplicationSchemaListResponse</a></code>

# Applications

Types:

```python
from scale_gp.types import ApplicationProcessResponse, ApplicationValidateResponse
```

Methods:

- <code title="post /v4/applications/process">client.applications.<a href="./src/scale_gp/resources/applications/applications.py">process</a>(\*\*<a href="src/scale_gp/types/application_process_params.py">params</a>) -> <a href="./src/scale_gp/types/application_process_response.py">object</a></code>
- <code title="post /v4/applications/validate">client.applications.<a href="./src/scale_gp/resources/applications/applications.py">validate</a>(\*\*<a href="src/scale_gp/types/application_validate_params.py">params</a>) -> <a href="./src/scale_gp/types/application_validate_response.py">object</a></code>

## Variant

Types:

```python
from scale_gp.types.applications import VariantProcessResponse
```

Methods:

- <code title="post /v4/applications/{application_variant_id}/process">client.applications.variant.<a href="./src/scale_gp/resources/applications/variant/variant.py">process</a>(application_variant_id, \*\*<a href="src/scale_gp/types/applications/variant_process_params.py">params</a>) -> <a href="./src/scale_gp/types/applications/variant_process_response.py">object</a></code>

### Threads

Types:

```python
from scale_gp.types.applications.variant import (
    ApplicationInteraction,
    ChatThread,
    ChatThreadFeedback,
    ChatThreadHistory,
    ThreadListResponse,
    ThreadProcessResponse,
)
```

Methods:

- <code title="post /v4/applications/{application_variant_id}/threads">client.applications.variant.threads.<a href="./src/scale_gp/resources/applications/variant/threads.py">create</a>(\*, path_application_variant_id, \*\*<a href="src/scale_gp/types/applications/variant/thread_create_params.py">params</a>) -> <a href="./src/scale_gp/types/applications/variant/chat_thread.py">ChatThread</a></code>
- <code title="get /v4/applications/{application_variant_id}/threads">client.applications.variant.threads.<a href="./src/scale_gp/resources/applications/variant/threads.py">list</a>(application_variant_id) -> <a href="./src/scale_gp/types/applications/variant/thread_list_response.py">ThreadListResponse</a></code>
- <code title="post /v4/applications/{application_variant_id}/threads/{thread_id}/process">client.applications.variant.threads.<a href="./src/scale_gp/resources/applications/variant/threads.py">process</a>(thread_id, \*, application_variant_id, \*\*<a href="src/scale_gp/types/applications/variant/thread_process_params.py">params</a>) -> <a href="./src/scale_gp/types/applications/variant/thread_process_response.py">object</a></code>

## Interactions

Types:

```python
from scale_gp.types.applications import ApplicationInteractionEntry
```

Methods:

- <code title="get /v4/applications/{application_spec_id}/interactions">client.applications.interactions.<a href="./src/scale_gp/resources/applications/interactions/interactions.py">list</a>(application_spec_id, \*\*<a href="src/scale_gp/types/applications/interaction_list_params.py">params</a>) -> <a href="./src/scale_gp/types/applications/application_interaction_entry.py">ApplicationInteractionEntry</a></code>

### Spans

Types:

```python
from scale_gp.types.applications.interactions import ApplicationTraceDetail
```

Methods:

- <code title="get /v4/applications/{application_spec_id}/interactions/{application_interaction_id}/spans">client.applications.interactions.spans.<a href="./src/scale_gp/resources/applications/interactions/spans.py">list</a>(application_interaction_id, \*, application_spec_id, \*\*<a href="src/scale_gp/types/applications/interactions/span_list_params.py">params</a>) -> <a href="./src/scale_gp/types/applications/interactions/application_trace_detail.py">ApplicationTraceDetail</a></code>

## Dashboards

Types:

```python
from scale_gp.types.applications import DashboardRetrieveResponse
```

Methods:

- <code title="get /v4/applications/{application_spec_id}/dashboards/{dashboard_id}">client.applications.dashboards.<a href="./src/scale_gp/resources/applications/dashboards.py">retrieve</a>(dashboard_id, \*, application_spec_id) -> <a href="./src/scale_gp/types/applications/dashboard_retrieve_response.py">DashboardRetrieveResponse</a></code>

# Threads

Types:

```python
from scale_gp.types import ThreadDeleteResponse
```

Methods:

- <code title="patch /v4/threads/{thread_id}">client.threads.<a href="./src/scale_gp/resources/threads/threads.py">update</a>(thread_id, \*\*<a href="src/scale_gp/types/thread_update_params.py">params</a>) -> <a href="./src/scale_gp/types/applications/variant/chat_thread.py">ChatThread</a></code>
- <code title="delete /v4/threads/{thread_id}">client.threads.<a href="./src/scale_gp/resources/threads/threads.py">delete</a>(thread_id) -> <a href="./src/scale_gp/types/thread_delete_response.py">object</a></code>

## Messages

Methods:

- <code title="patch /v4/threads/{thread_id}/messages/{application_interaction_id}">client.threads.messages.<a href="./src/scale_gp/resources/threads/messages.py">update</a>(application_interaction_id, \*, thread_id, \*\*<a href="src/scale_gp/types/threads/message_update_params.py">params</a>) -> <a href="./src/scale_gp/types/applications/variant/application_interaction.py">ApplicationInteraction</a></code>
- <code title="get /v4/threads/{thread_id}/messages">client.threads.messages.<a href="./src/scale_gp/resources/threads/messages.py">list</a>(thread_id) -> <a href="./src/scale_gp/types/applications/variant/chat_thread_history.py">ChatThreadHistory</a></code>
- <code title="put /v4/threads/{thread_id}/messages/{application_interaction_id}/feedback">client.threads.messages.<a href="./src/scale_gp/resources/threads/messages.py">feedback</a>(\*, thread_id, path_application_interaction_id, \*\*<a href="src/scale_gp/types/threads/message_feedback_params.py">params</a>) -> <a href="./src/scale_gp/types/applications/variant/chat_thread_feedback.py">ChatThreadFeedback</a></code>

# Themes

Types:

```python
from scale_gp.types import ThemeResponse, ThemeListResponse
```

Methods:

- <code title="post /v4/themes">client.themes.<a href="./src/scale_gp/resources/themes.py">create</a>(\*\*<a href="src/scale_gp/types/theme_create_params.py">params</a>) -> <a href="./src/scale_gp/types/theme_response.py">ThemeResponse</a></code>
- <code title="get /v4/themes/{theme_id}">client.themes.<a href="./src/scale_gp/resources/themes.py">retrieve</a>(theme_id) -> <a href="./src/scale_gp/types/theme_response.py">ThemeResponse</a></code>
- <code title="get /v4/themes">client.themes.<a href="./src/scale_gp/resources/themes.py">list</a>(\*\*<a href="src/scale_gp/types/theme_list_params.py">params</a>) -> <a href="./src/scale_gp/types/theme_list_response.py">ThemeListResponse</a></code>
