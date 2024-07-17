# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = [
    "UploadCreateParams",
    "CreateKnowledgeBaseV2UploadFromDataSourceRequest",
    "CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceConfig",
    "CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceConfigS3DataSourceConfig",
    "CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceConfigSharePointDataSourceConfig",
    "CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceConfigGoogleDriveDataSourceConfig",
    "CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceConfigAzureBlobStorageDataSourceConfig",
    "CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceConfigConfluenceDataSourceConfig",
    "CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceConfigSlackDataSourceConfig",
    "CreateKnowledgeBaseV2UploadFromDataSourceRequestChunkingStrategyConfig",
    "CreateKnowledgeBaseV2UploadFromDataSourceRequestChunkingStrategyConfigCharacterChunkingStrategyConfig",
    "CreateKnowledgeBaseV2UploadFromDataSourceRequestChunkingStrategyConfigTokenChunkingStrategyConfig",
    "CreateKnowledgeBaseV2UploadFromDataSourceRequestChunkingStrategyConfigCustomChunkingStrategyConfig",
    "CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceAuthConfig",
    "CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceAuthConfigSharePointDataSourceAuthConfig",
    "CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceAuthConfigAzureBlobStorageDataSourceAuthConfig",
    "CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceAuthConfigGoogleDriveDataSourceAuthConfig",
    "CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceAuthConfigS3DataSourceAuthConfig",
    "CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceAuthConfigConfluenceDataSourceAuthConfig",
    "CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceAuthConfigSlackDataSourceAuthConfig",
    "CreateKnowledgeBaseV2UploadFromLocalChunksRequest",
    "CreateKnowledgeBaseV2UploadFromLocalChunksRequestDataSourceConfig",
    "CreateKnowledgeBaseV2UploadFromLocalChunksRequestChunk",
    "CreateKnowledgeBaseV2UploadFromDataSourceIDRequest",
    "CreateKnowledgeBaseV2UploadFromDataSourceIDRequestChunkingStrategyConfig",
    "CreateKnowledgeBaseV2UploadFromDataSourceIDRequestChunkingStrategyConfigCharacterChunkingStrategyConfig",
    "CreateKnowledgeBaseV2UploadFromDataSourceIDRequestChunkingStrategyConfigTokenChunkingStrategyConfig",
    "CreateKnowledgeBaseV2UploadFromDataSourceIDRequestChunkingStrategyConfigCustomChunkingStrategyConfig",
]


class CreateKnowledgeBaseV2UploadFromDataSourceRequest(TypedDict, total=False):
    data_source_config: Required[CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceConfig]
    """Configuration for the data source which describes where to find the data."""

    chunking_strategy_config: CreateKnowledgeBaseV2UploadFromDataSourceRequestChunkingStrategyConfig
    """Configuration for the chunking strategy which describes how to chunk the data."""

    data_source_auth_config: CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceAuthConfig
    """
    Configuration for the data source which describes how to authenticate to the
    data source.
    """

    force_reupload: bool
    """Force reingest, regardless the change of the source file."""


class CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceConfigS3DataSourceConfig(TypedDict, total=False):
    aws_account_id: Required[str]
    """AWS account ID that owns the S3 bucket."""

    aws_region: Required[str]
    """AWS region where the S3 bucket is located."""

    s3_bucket: Required[str]
    """Name of the S3 bucket where the data is stored."""

    source: Required[Literal["S3"]]

    s3_prefix: str
    """Prefix of the S3 bucket where the data is stored.

    If not specified, the entire bucket will be used.
    """


class CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceConfigSharePointDataSourceConfig(
    TypedDict, total=False
):
    client_id: Required[str]
    """Client ID associated with this SharePoint site"""

    site_id: Required[str]
    """
    Site ID for this SharePoint site, can be found at
    https://[hostname].sharepoint.com/sites/[site name]/\\__api/site/id
    """

    source: Required[Literal["SharePoint"]]

    tenant_id: Required[str]
    """Tenant ID that the SharePoint site is within"""

    folder_path: str
    """Nested folder path to read files from the root of the site.

    Please omit the leading slash. Example: 'Documents/sub_directory'
    """

    recursive: bool
    """Recurse through the folder contents, default is True."""


class CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceConfigGoogleDriveDataSourceConfig(
    TypedDict, total=False
):
    drive_id: Required[str]
    """ID associated with the Google Drive to retrieve contents from"""

    source: Required[Literal["GoogleDrive"]]


class CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceConfigAzureBlobStorageDataSourceConfig(
    TypedDict, total=False
):
    container_url: Required[str]
    """
    The full URL of the container such as
    'https://your-account-name.blob.core.windows.net/your-container-name'
    """

    source: Required[Literal["AzureBlobStorage"]]


class CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceConfigConfluenceDataSourceConfig(
    TypedDict, total=False
):
    source: Required[Literal["Confluence"]]

    space_key: Required[str]
    """Confluence space key to retrieve contents from.

    See https://support.atlassian.com/confluence-cloud/docs/choose-a-space-key
    """


class CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceConfigSlackDataSourceConfig(TypedDict, total=False):
    channel_id: Required[str]
    """Slack Channel or Conversation ID to retrieve history from.

    Open channel details and find the ID at bottom of 'About' section.
    """

    source: Required[Literal["Slack"]]


CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceConfig = Union[
    CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceConfigS3DataSourceConfig,
    CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceConfigSharePointDataSourceConfig,
    CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceConfigGoogleDriveDataSourceConfig,
    CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceConfigAzureBlobStorageDataSourceConfig,
    CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceConfigConfluenceDataSourceConfig,
    CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceConfigSlackDataSourceConfig,
]


class CreateKnowledgeBaseV2UploadFromDataSourceRequestChunkingStrategyConfigCharacterChunkingStrategyConfig(
    TypedDict, total=False
):
    strategy: Required[Literal["character"]]

    chunk_overlap: int
    """Number of characters to overlap between chunks.

    If not specified, an overlap of 200 will be used. For example if the chunk size
    is 3 and the overlap size is 1, and the text to chunk is 'abcde', the chunks
    will be 'abc', 'cde'.
    """

    chunk_size: int
    """Maximum number of characters in each chunk.

    If not specified, a chunk size of 1000 will be used.
    """

    separator: str
    """Character designating breaks in input data.

    Text data will first be split into sections by this separator, then each section
    will be split into chunks of size `chunk_size`.
    """


class CreateKnowledgeBaseV2UploadFromDataSourceRequestChunkingStrategyConfigTokenChunkingStrategyConfig(
    TypedDict, total=False
):
    strategy: Required[Literal["token"]]

    chunk_overlap: int
    """Number of tokens to overlap between chunks.

    If not specified, an overlap of 0 will be used. Not this if only followed
    approximately.
    """

    max_chunk_size: int
    """Maximum number of tokens in each chunk.

    If not specified, a maximum chunk size of 600 will be used.
    """

    separator: str
    """Character designating breaks in input data.

    Text data will first be split into sections by this separator, then each section
    will be split into chunks of size `chunk_size`.
    """

    target_chunk_size: int
    """Target number of tokens in each chunk.

    If not specified, a target chunk size of 200 will be used.
    """


class CreateKnowledgeBaseV2UploadFromDataSourceRequestChunkingStrategyConfigCustomChunkingStrategyConfig(
    TypedDict, total=False
):
    endpoint: Required[str]
    """Endpoint path to call for custom chunking"""

    strategy: Required[Literal["custom"]]

    params: object
    """Parameters that will be appended to the body of the request for the chunk."""


CreateKnowledgeBaseV2UploadFromDataSourceRequestChunkingStrategyConfig = Union[
    CreateKnowledgeBaseV2UploadFromDataSourceRequestChunkingStrategyConfigCharacterChunkingStrategyConfig,
    CreateKnowledgeBaseV2UploadFromDataSourceRequestChunkingStrategyConfigTokenChunkingStrategyConfig,
    CreateKnowledgeBaseV2UploadFromDataSourceRequestChunkingStrategyConfigCustomChunkingStrategyConfig,
]


class CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceAuthConfigSharePointDataSourceAuthConfig(
    TypedDict, total=False
):
    client_secret: Required[str]
    """Secret for the app registration associated with this SharePoint site"""

    source: Required[Literal["SharePoint"]]

    encrypted: bool


class CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceAuthConfigAzureBlobStorageDataSourceAuthConfig(
    TypedDict, total=False
):
    blob_sas_token: Required[str]
    """Shared Access Signature token for the Azure Blob Storage container"""

    source: Required[Literal["AzureBlobStorage"]]

    encrypted: bool


class CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceAuthConfigGoogleDriveDataSourceAuthConfig(
    TypedDict, total=False
):
    client_email: Required[str]
    """
    Client email to use for google drive, set to override client email set in env
    vars
    """

    client_id: Required[str]
    """Client id to use for google drive, set to override client id set in env vars"""

    private_key: Required[str]
    """
    Private key to use for google drive, set to override private key set in env vars
    """

    source: Required[Literal["GoogleDrive"]]

    token_uri: Required[str]
    """Token uri to use for google drive, set to override token uri set in env vars"""

    encrypted: bool


class CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceAuthConfigS3DataSourceAuthConfig(
    TypedDict, total=False
):
    source: Required[Literal["S3"]]

    encrypted: bool

    external_id: str
    """External ID defined by the customer for the IAM role"""

    s3_role: str
    """Name of the role that a client will be initialized via AssumeRole of AWS sts"""


class CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceAuthConfigConfluenceDataSourceAuthConfig(
    TypedDict, total=False
):
    api_key: Required[str]
    """
    API key to use for Confluence, set this to override api key configured in env
    vars.
    """

    atlassian_domain: Required[str]
    """
    Your Confluence API server's full domain, set to override domain configured in
    env vars. E.g. 'https://[your-company].atlassian.net'
    """

    client_email: Required[str]
    """
    Client email to use for Confluence, set to override client email set in env
    vars.
    """

    source: Required[Literal["Confluence"]]

    encrypted: bool


class CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceAuthConfigSlackDataSourceAuthConfig(
    TypedDict, total=False
):
    bot_token: Required[str]
    """Your Slack app's Bot OAuth token. See https://api.slack.com/quickstart"""

    source: Required[Literal["Slack"]]

    encrypted: bool


CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceAuthConfig = Union[
    CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceAuthConfigSharePointDataSourceAuthConfig,
    CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceAuthConfigAzureBlobStorageDataSourceAuthConfig,
    CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceAuthConfigGoogleDriveDataSourceAuthConfig,
    CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceAuthConfigS3DataSourceAuthConfig,
    CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceAuthConfigConfluenceDataSourceAuthConfig,
    CreateKnowledgeBaseV2UploadFromDataSourceRequestDataSourceAuthConfigSlackDataSourceAuthConfig,
]


class CreateKnowledgeBaseV2UploadFromLocalChunksRequest(TypedDict, total=False):
    data_source_config: Required[CreateKnowledgeBaseV2UploadFromLocalChunksRequestDataSourceConfig]
    """Configuration for the data source which describes where to find the data."""

    chunks: Iterable[CreateKnowledgeBaseV2UploadFromLocalChunksRequestChunk]
    """List of chunks."""

    force_reupload: bool
    """Force reingest, regardless the change of the source file."""


class CreateKnowledgeBaseV2UploadFromLocalChunksRequestDataSourceConfig(TypedDict, total=False):
    artifact_name: Required[str]
    """The file name assigned to the artifact, containing a file extension.

    Adding an extension is mandatory, to allow detecting file types for text
    extraction.
    """

    artifact_uri: Required[str]
    """
    A unique identifier for an artifact within the knowledge base, such as full path
    in a directory or file system.
    """

    source: Required[Literal["LocalChunks"]]

    deduplication_strategy: Literal["Overwrite", "Fail"]
    """An enumeration."""


class CreateKnowledgeBaseV2UploadFromLocalChunksRequestChunk(TypedDict, total=False):
    chunk_position: Required[int]
    """Position of the chunk in the artifact."""

    text: Required[str]
    """Associated text of the chunk."""

    metadata: object
    """Additional metadata associated with the chunk."""


class CreateKnowledgeBaseV2UploadFromDataSourceIDRequest(TypedDict, total=False):
    chunking_strategy_config: Required[CreateKnowledgeBaseV2UploadFromDataSourceIDRequestChunkingStrategyConfig]
    """Configuration for the chunking strategy which describes how to chunk the data."""

    data_source_id: Required[str]
    """Id of the data source to fetch."""

    force_reupload: bool
    """Force reingest, regardless the change of the source file."""


class CreateKnowledgeBaseV2UploadFromDataSourceIDRequestChunkingStrategyConfigCharacterChunkingStrategyConfig(
    TypedDict, total=False
):
    strategy: Required[Literal["character"]]

    chunk_overlap: int
    """Number of characters to overlap between chunks.

    If not specified, an overlap of 200 will be used. For example if the chunk size
    is 3 and the overlap size is 1, and the text to chunk is 'abcde', the chunks
    will be 'abc', 'cde'.
    """

    chunk_size: int
    """Maximum number of characters in each chunk.

    If not specified, a chunk size of 1000 will be used.
    """

    separator: str
    """Character designating breaks in input data.

    Text data will first be split into sections by this separator, then each section
    will be split into chunks of size `chunk_size`.
    """


class CreateKnowledgeBaseV2UploadFromDataSourceIDRequestChunkingStrategyConfigTokenChunkingStrategyConfig(
    TypedDict, total=False
):
    strategy: Required[Literal["token"]]

    chunk_overlap: int
    """Number of tokens to overlap between chunks.

    If not specified, an overlap of 0 will be used. Not this if only followed
    approximately.
    """

    max_chunk_size: int
    """Maximum number of tokens in each chunk.

    If not specified, a maximum chunk size of 600 will be used.
    """

    separator: str
    """Character designating breaks in input data.

    Text data will first be split into sections by this separator, then each section
    will be split into chunks of size `chunk_size`.
    """

    target_chunk_size: int
    """Target number of tokens in each chunk.

    If not specified, a target chunk size of 200 will be used.
    """


class CreateKnowledgeBaseV2UploadFromDataSourceIDRequestChunkingStrategyConfigCustomChunkingStrategyConfig(
    TypedDict, total=False
):
    endpoint: Required[str]
    """Endpoint path to call for custom chunking"""

    strategy: Required[Literal["custom"]]

    params: object
    """Parameters that will be appended to the body of the request for the chunk."""


CreateKnowledgeBaseV2UploadFromDataSourceIDRequestChunkingStrategyConfig = Union[
    CreateKnowledgeBaseV2UploadFromDataSourceIDRequestChunkingStrategyConfigCharacterChunkingStrategyConfig,
    CreateKnowledgeBaseV2UploadFromDataSourceIDRequestChunkingStrategyConfigTokenChunkingStrategyConfig,
    CreateKnowledgeBaseV2UploadFromDataSourceIDRequestChunkingStrategyConfigCustomChunkingStrategyConfig,
]

UploadCreateParams = Union[
    CreateKnowledgeBaseV2UploadFromDataSourceRequest,
    CreateKnowledgeBaseV2UploadFromLocalChunksRequest,
    CreateKnowledgeBaseV2UploadFromDataSourceIDRequest,
]
