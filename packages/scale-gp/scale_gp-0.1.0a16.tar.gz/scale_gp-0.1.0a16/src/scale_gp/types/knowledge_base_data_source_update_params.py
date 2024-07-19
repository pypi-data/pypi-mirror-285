# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypedDict

__all__ = [
    "KnowledgeBaseDataSourceUpdateParams",
    "DataSourceAuthConfig",
    "DataSourceAuthConfigSharePointDataSourceAuthConfig",
    "DataSourceAuthConfigAzureBlobStorageDataSourceAuthConfig",
    "DataSourceAuthConfigGoogleDriveDataSourceAuthConfig",
    "DataSourceAuthConfigS3DataSourceAuthConfig",
    "DataSourceAuthConfigConfluenceDataSourceAuthConfig",
    "DataSourceAuthConfigSlackDataSourceAuthConfig",
]


class KnowledgeBaseDataSourceUpdateParams(TypedDict, total=False):
    data_source_auth_config: DataSourceAuthConfig

    description: str

    name: str


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
