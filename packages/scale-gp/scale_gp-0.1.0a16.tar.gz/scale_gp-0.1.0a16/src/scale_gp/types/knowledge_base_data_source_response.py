# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from datetime import datetime
from typing_extensions import Literal, Annotated

from .._utils import PropertyInfo
from .._models import BaseModel

__all__ = [
    "KnowledgeBaseDataSourceResponse",
    "DataSourceConfig",
    "DataSourceConfigS3DataSourceConfig",
    "DataSourceConfigSharePointDataSourceConfig",
    "DataSourceConfigGoogleDriveDataSourceConfig",
    "DataSourceConfigAzureBlobStorageDataSourceConfig",
    "DataSourceConfigConfluenceDataSourceConfig",
    "DataSourceConfigSlackDataSourceConfig",
]


class DataSourceConfigS3DataSourceConfig(BaseModel):
    aws_account_id: str
    """AWS account ID that owns the S3 bucket."""

    aws_region: str
    """AWS region where the S3 bucket is located."""

    s3_bucket: str
    """Name of the S3 bucket where the data is stored."""

    source: Literal["S3"]

    s3_prefix: Optional[str] = None
    """Prefix of the S3 bucket where the data is stored.

    If not specified, the entire bucket will be used.
    """


class DataSourceConfigSharePointDataSourceConfig(BaseModel):
    client_id: str
    """Client ID associated with this SharePoint site"""

    site_id: str
    """
    Site ID for this SharePoint site, can be found at
    https://[hostname].sharepoint.com/sites/[site name]/\\__api/site/id
    """

    source: Literal["SharePoint"]

    tenant_id: str
    """Tenant ID that the SharePoint site is within"""

    folder_path: Optional[str] = None
    """Nested folder path to read files from the root of the site.

    Please omit the leading slash. Example: 'Documents/sub_directory'
    """

    recursive: Optional[bool] = None
    """Recurse through the folder contents, default is True."""


class DataSourceConfigGoogleDriveDataSourceConfig(BaseModel):
    drive_id: str
    """ID associated with the Google Drive to retrieve contents from"""

    source: Literal["GoogleDrive"]


class DataSourceConfigAzureBlobStorageDataSourceConfig(BaseModel):
    container_url: str
    """
    The full URL of the container such as
    'https://your-account-name.blob.core.windows.net/your-container-name'
    """

    source: Literal["AzureBlobStorage"]


class DataSourceConfigConfluenceDataSourceConfig(BaseModel):
    source: Literal["Confluence"]

    space_key: str
    """Confluence space key to retrieve contents from.

    See https://support.atlassian.com/confluence-cloud/docs/choose-a-space-key
    """


class DataSourceConfigSlackDataSourceConfig(BaseModel):
    channel_id: str
    """Slack Channel or Conversation ID to retrieve history from.

    Open channel details and find the ID at bottom of 'About' section.
    """

    source: Literal["Slack"]


DataSourceConfig = Annotated[
    Union[
        DataSourceConfigS3DataSourceConfig,
        DataSourceConfigSharePointDataSourceConfig,
        DataSourceConfigGoogleDriveDataSourceConfig,
        DataSourceConfigAzureBlobStorageDataSourceConfig,
        DataSourceConfigConfluenceDataSourceConfig,
        DataSourceConfigSlackDataSourceConfig,
    ],
    PropertyInfo(discriminator="source"),
]


class KnowledgeBaseDataSourceResponse(BaseModel):
    id: str
    """The unique identifier of the entity."""

    account_id: str
    """The ID of the account that owns the given entity."""

    created_at: datetime
    """The date and time when the entity was created in ISO format."""

    created_by_user_id: str
    """The user who originally created the entity."""

    data_source_config: DataSourceConfig

    name: str

    updated_at: datetime
    """The date and time when the entity was last updated in ISO format."""

    description: Optional[str] = None
