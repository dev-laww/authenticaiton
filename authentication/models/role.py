import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

from .role_permission import RolePermission
from .user_role import UserRole
from ..core.utils import get_current_utc_datetime

if TYPE_CHECKING:
    from .user import User
    from .permission import Permission


class Role(SQLModel, table=True):
    __tablename__ = "roles"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
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

    permissions: List["Permission"] = Relationship(
        back_populates="roles",
        link_model=RolePermission,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    users: List["User"] = Relationship(
        back_populates="roles",
        link_model=UserRole,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
