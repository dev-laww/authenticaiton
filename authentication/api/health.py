from typing import Annotated

from fastapi import Depends

from ..controllers.health import HealthController
from ..core.routing import AppRouter, get


class HealthRouter(AppRouter):
    controller: Annotated[HealthController, Depends()]

    @get("")
    async def get_health_status(self):
        return await self.controller.check_health()

    @get("", version="2")
    async def get_health_status_v2(self):
        return {"status": "healthy", "version": "v2"}


router = HealthRouter(prefix="/health")
