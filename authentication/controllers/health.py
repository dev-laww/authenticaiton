from ..core.base import Controller


class HealthController(Controller):
    """
    Controller for handling health check requests.
    """

    async def check_health(self):  # noqa
        return {"status": "healthy"}
