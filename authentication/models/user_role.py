import datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlmodel import Field, SQLModel

from ..core.utils import get_current_utc_datetime


class UserRole(SQLModel, table=True):
    __tablename__ = "user_roles"

    user_id: Optional[UUID] = Field(
        default=None, foreign_key="users.id", primary_key=True
    )
    role_id: Optional[UUID] = Field(
        default=None, foreign_key="roles.id", primary_key=True
    )
    assigned_at: datetime.datetime = Field(
        default_factory=get_current_utc_datetime,
        sa_column=sa.Column(
            sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
