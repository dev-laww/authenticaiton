import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlmodel import SQLModel, Field, Relationship

from authentication.core.utils import get_current_utc_datetime

if TYPE_CHECKING:
    from .user import User


class Account(SQLModel, table=True):
    __tablename__ = "accounts"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    account_id: str
    provider_id: str
    access_token: Optional[str]
    refresh_token: Optional[str]
    scope: Optional[str]
    id_token: Optional[str]
    password: Optional[str]
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

    user: "User" = Relationship(
        back_populates="accounts", sa_relationship_kwargs={"lazy": "selectin"}
    )
