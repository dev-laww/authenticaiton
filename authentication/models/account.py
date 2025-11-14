from typing import Optional, TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship

from ..core.base import BaseDBModel

if TYPE_CHECKING:
    from .user import User


class Account(BaseDBModel, table=True):
    __tablename__ = "accounts"

    user_id: UUID = Field(foreign_key="users.id", index=True)
    account_id: str
    provider_id: str
    access_token: Optional[str]
    refresh_token: Optional[str]
    scope: Optional[str]
    id_token: Optional[str]
    password: Optional[str]

    user: "User" = Relationship(
        back_populates="accounts", sa_relationship_kwargs={"lazy": "selectin"}
    )
