# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["UserInfo", "Account", "AccountAccount"]


class AccountAccount(BaseModel):
    id: str

    name: str


class Account(BaseModel):
    account: AccountAccount
    """The account associated with the user sending the request."""

    role: Literal["manager", "admin", "member", "labeler", "disabled", "invited", "viewer"]
    """An enumeration."""


class UserInfo(BaseModel):
    id: str
    """User id"""

    accounts: List[Account]
    """A list of accounts that the selected user has access to"""

    email: str
    """E-mail address"""

    first_name: Optional[str] = None
    """First name"""

    is_organization_admin: Optional[bool] = None
    """True if the current user is an organization admin."""

    last_name: Optional[str] = None
    """Last name"""
