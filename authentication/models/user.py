import datetime
from typing import Optional, TYPE_CHECKING, List
from uuid import UUID, uuid4

import sqlalchemy as sa
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from .user_role import UserRole
from ..core.utils import get_current_utc_datetime

if TYPE_CHECKING:
    from .role import Role
    from .account import Account
    from .session import Session


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    email: EmailStr = Field(unique=True, index=True)
    email_verified: bool = Field(default=False)
    image: Optional[str] = Field(default=None)
    created_at: datetime.datetime = Field(
        default_factory=get_current_utc_datetime,
        sa_column=sa.Column(
            sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    updated_at: datetime.datetime = Field(
        default_factory=get_current_utc_datetime,
        sa_column=sa.Column(
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    roles: List["Role"] = Relationship(
        back_populates="users",
        link_model=UserRole,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    accounts: List["Account"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )

    sessions: List["Session"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
