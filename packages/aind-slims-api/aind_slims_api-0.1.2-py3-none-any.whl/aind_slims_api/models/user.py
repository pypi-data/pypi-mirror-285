"""Contains a model for a user."""

from typing import Optional

from pydantic import Field

from aind_slims_api.models.base import SlimsBaseModel


# TODO: Tighten this up once users are more commonly used
class SlimsUser(SlimsBaseModel):
    """Model for user information in SLIMS

    Examples
    --------
    >>> from aind_slims_api.core import SlimsClient
    >>> client = SlimsClient()
    >>> user = client.fetch_model(SlimsUser, username="LKim")
    """

    username: str = Field(..., alias="user_userName")
    first_name: Optional[str] = Field("", alias="user_firstName")
    last_name: Optional[str] = Field("", alias="user_lastName")
    full_name: Optional[str] = Field("", alias="user_fullName")
    email: Optional[str] = Field("", alias="user_email")
    pk: int = Field(..., alias="user_pk")

    _slims_table = "User"
