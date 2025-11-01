from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .core import settings
from .core.routing import FileRouter, Extractor, RouterMetadata, AppRouter


class AppRouteExtractor(Extractor):
    def extract(self, module: Any) -> list[RouterMetadata]:
        routers = []

        if not hasattr(module, "routable"):
            return routers

        routable = getattr(module, "routable")

        if not isinstance(routable, AppRouter):
            return routers

        router = routable.router

        routers.append(RouterMetadata(router=router))

        return routers


def create_app():
    app = FastAPI(
        title=settings.app_name,
        default_response_class=JSONResponse
    )

    @app.get("/")
    async def root():
        return {
            "message": "Authentication Service is running"
        }

    extractor = AppRouteExtractor()
    file_router = FileRouter(
        base_path="./api",
        extractor=extractor
    )

    print(file_router.stats)

    app.include_router(file_router)

    return app
