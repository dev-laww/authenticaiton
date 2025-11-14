import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING, List
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

from .role_permission import RolePermission
from ..core.utils import get_current_utc_datetime

if TYPE_CHECKING:
    from .role import Role


class Action(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    UPDATE = "update"


class Permission(SQLModel, table=True):
    __tablename__ = "permissions"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    resource: str = Field(index=True)
    action: Action = Field(
        sa_column=sa.Column(sa.Enum(Action), nullable=False, index=True)
    )
    description: Optional[str] = Field(default=None)
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
        back_populates="permissions",
        link_model=RolePermission,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    @property
    def name(self):
        return f"{self.action.value}:{self.resource}"
