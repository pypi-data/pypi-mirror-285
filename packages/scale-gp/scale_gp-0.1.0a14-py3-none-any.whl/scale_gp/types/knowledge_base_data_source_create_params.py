# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypedDict

__all__ = [
    "KnowledgeBaseDataSourceCreateParams",
    "DataSourceConfig",
    "DataSourceConfigS3DataSourceConfig",
    "DataSourceConfigSharePointDataSourceConfig",
    "DataSourceConfigGoogleDriveDataSourceConfig",
    "DataSourceConfigAzureBlobStorageDataSourceConfig",
    "DataSourceConfigConfluenceDataSourceConfig",
    "DataSourceConfigSlackDataSourceConfig",
    "DataSourceAuthConfig",
    "DataSourceAuthConfigSharePointDataSourceAuthConfig",
    "DataSourceAuthConfigAzureBlobStorageDataSourceAuthConfig",
    "DataSourceAuthConfigGoogleDriveDataSourceAuthConfig",
    "DataSourceAuthConfigS3DataSourceAuthConfig",
    "DataSourceAuthConfigConfluenceDataSourceAuthConfig",
    "DataSourceAuthConfigSlackDataSourceAuthConfig",
]


class KnowledgeBaseDataSourceCreateParams(TypedDict, total=False):
    account_id: Required[str]
    """The ID of the account that owns the given entity."""

    data_source_config: Required[DataSourceConfig]

    name: Required[str]

    data_source_auth_config: DataSourceAuthConfig

    description: str


class DataSourceConfigS3DataSourceConfig(TypedDict, total=False):
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


class DataSourceConfigSharePointDataSourceConfig(TypedDict, total=False):
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


class DataSourceConfigGoogleDriveDataSourceConfig(TypedDict, total=False):
    drive_id: Required[str]
    """ID associated with the Google Drive to retrieve contents from"""

    source: Required[Literal["GoogleDrive"]]


class DataSourceConfigAzureBlobStorageDataSourceConfig(TypedDict, total=False):
    container_url: Required[str]
    """
    The full URL of the container such as
    'https://your-account-name.blob.core.windows.net/your-container-name'
    """

    source: Required[Literal["AzureBlobStorage"]]


class DataSourceConfigConfluenceDataSourceConfig(TypedDict, total=False):
    source: Required[Literal["Confluence"]]

    space_key: Required[str]
    """Confluence space key to retrieve contents from.

    See https://support.atlassian.com/confluence-cloud/docs/choose-a-space-key
    """


class DataSourceConfigSlackDataSourceConfig(TypedDict, total=False):
    channel_id: Required[str]
    """Slack Channel or Conversation ID to retrieve history from.

    Open channel details and find the ID at bottom of 'About' section.
    """

    source: Required[Literal["Slack"]]


DataSourceConfig = Union[
    DataSourceConfigS3DataSourceConfig,
    DataSourceConfigSharePointDataSourceConfig,
    DataSourceConfigGoogleDriveDataSourceConfig,
    DataSourceConfigAzureBlobStorageDataSourceConfig,
    DataSourceConfigConfluenceDataSourceConfig,
    DataSourceConfigSlackDataSourceConfig,
]


class DataSourceAuthConfigSharePointDataSourceAuthConfig(TypedDict, total=False):
    client_secret: Required[str]
    """Secret for the app registration associated with this SharePoint site"""

    source: Required[Literal["SharePoint"]]

    encrypted: bool


class DataSourceAuthConfigAzureBlobStorageDataSourceAuthConfig(TypedDict, total=False):
    blob_sas_token: Required[str]
    """Shared Access Signature token for the Azure Blob Storage container"""

    source: Required[Literal["AzureBlobStorage"]]

    encrypted: bool


class DataSourceAuthConfigGoogleDriveDataSourceAuthConfig(TypedDict, total=False):
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


class DataSourceAuthConfigS3DataSourceAuthConfig(TypedDict, total=False):
    source: Required[Literal["S3"]]

    encrypted: bool

    external_id: str
    """External ID defined by the customer for the IAM role"""

    s3_role: str
    """Name of the role that a client will be initialized via AssumeRole of AWS sts"""


class DataSourceAuthConfigConfluenceDataSourceAuthConfig(TypedDict, total=False):
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


class DataSourceAuthConfigSlackDataSourceAuthConfig(TypedDict, total=False):
    bot_token: Required[str]
    """Your Slack app's Bot OAuth token. See https://api.slack.com/quickstart"""

    source: Required[Literal["Slack"]]

    encrypted: bool


DataSourceAuthConfig = Union[
    DataSourceAuthConfigSharePointDataSourceAuthConfig,
    DataSourceAuthConfigAzureBlobStorageDataSourceAuthConfig,
    DataSourceAuthConfigGoogleDriveDataSourceAuthConfig,
    DataSourceAuthConfigS3DataSourceAuthConfig,
    DataSourceAuthConfigConfluenceDataSourceAuthConfig,
    DataSourceAuthConfigSlackDataSourceAuthConfig,
]
