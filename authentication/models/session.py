import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlmodel import SQLModel, Field, Relationship

from authentication.core.utils import get_current_utc_datetime

if TYPE_CHECKING:
    from .user import User


class Session(SQLModel, table=True):
    __tablename__ = "sessions"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    token: str
    expires_at: datetime.datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime.datetime = Field(
        default_factory=get_current_utc_datetime,
        sa_column=sa.Column(
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False
        )
    )
    updated_at: datetime.datetime = Field(
        default_factory=get_current_utc_datetime,
        sa_column=sa.Column(
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False
        )
    )

    user: "User" = Relationship(back_populates="sessions", sa_relationship_kwargs={"lazy": "selectin"})
