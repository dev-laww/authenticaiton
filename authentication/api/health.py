from typing import Annotated

from fastapi import Depends

from ..controllers.health import HealthController
from ..core.routing import AppRouter, get


class HealthRouter(AppRouter):
    controller: Annotated[HealthController, Depends()]

    @get("")
    async def get_health_status(self):
        return await self.controller.check_health()


router = HealthRouter(prefix="/health")
