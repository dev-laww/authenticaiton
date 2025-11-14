from typing import Optional, List, TYPE_CHECKING

from sqlmodel import Field, Relationship

from .role_permission import RolePermission
from .user_role import UserRole
from ..core.base import BaseDBModel

if TYPE_CHECKING:
    from .user import User
    from .permission import Permission


class Role(BaseDBModel, table=True):
    __tablename__ = "roles"

    name: str = Field(unique=True, index=True)
    description: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)

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
