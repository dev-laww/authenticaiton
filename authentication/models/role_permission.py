import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Field

from ..core.base import BaseDBModel


class RolePermission(BaseDBModel, table=True):
    __tablename__ = "role_permissions"

    role_id: Optional[UUID] = Field(
        default=None, foreign_key="roles.id", primary_key=True
    )
    permission_id: Optional[UUID] = Field(
        default=None, foreign_key="permissions.id", primary_key=True
    )

    @property
    def granted_at(self) -> datetime.datetime:
        return self.created_at
