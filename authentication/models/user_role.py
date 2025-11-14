from typing import Optional
from uuid import UUID

from sqlmodel import Field

from ..core.base import BaseDBModel


class UserRole(BaseDBModel, table=True):
    __tablename__ = "user_roles"

    user_id: Optional[UUID] = Field(
        default=None, foreign_key="users.id", primary_key=True
    )
    role_id: Optional[UUID] = Field(
        default=None, foreign_key="roles.id", primary_key=True
    )

    @property
    def assigned_at(self):
        return self.created_at
