from typing import Annotated

from fastapi import Depends

from ..core.base import Controller
from ..core.database import Repository
from ..core.database.repository import get_repository
from ..core.response import Response
from ..models import Role
from ..schemas import Role as CreateRole
from ..schemas.common import PaginationParams, PaginatedResponse, PaginationInfo


class AdminController(Controller):
    def __init__(
        self,
        role_repository: Annotated[Repository[Role], Depends(get_repository(Role))],
    ):
        self.role_repository = role_repository

    async def get_roles(self, pagination: PaginationParams):
        roles = await self.role_repository.all(
            skip=pagination.offset, limit=pagination.limit
        )
        total = await self.role_repository.count()
        page_count = (total + pagination.limit - 1) // pagination.limit
        has_next = pagination.page < page_count
        has_previous = pagination.page > 1

        pagination = PaginationInfo(
            total_items=total,
            total_pages=page_count,
            current_page=pagination.page,
            items_per_page=pagination.limit,
            has_next=has_next,
            has_previous=has_previous,
            next_page_url=f"/admin/roles?page={pagination.page + 1}&limit={pagination.limit}"
            if has_next
            else None,
            previous_page_url=f"/admin/roles?page={pagination.page - 1}&limit={pagination.limit}"
            if has_previous
            else None,
        )

        return Response.ok(
            message="Roles retrieved successfully",
            data=PaginatedResponse(
                pagination=pagination,
                items=roles,
            ),
        )

    async def create_role(self, role: CreateRole):
        new_role = Role.model_validate(role)
        created_role = await self.role_repository.create(new_role)

        return Response.created(
            message="Role created successfully",
            data=created_role,
        )
