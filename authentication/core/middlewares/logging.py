import logging
import time
from http import HTTPStatus
from typing import Callable, Any
from uuid import uuid4

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from ..logging import logger

logging.getLogger("uvicorn.access").disabled = True


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests"""

    async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Any:
        request_id = str(uuid4())
        current_time = time.time()

        response: Response = await call_next(request)

        process_time = time.time() - current_time
        process_time_ms = round(process_time * 1000, 2)

        response.headers["X-Process-Time"] = str(process_time_ms)
        response.headers["X-Request-ID"] = request_id

        method = request.method
        host = request.client.host
        path = request.url.path

        if request.url.query:
            path += f"?{request.url.query}"

        http_version = request.scope.get("http_version", "unknown")
        status = response.status_code
        reason = HTTPStatus(status).phrase

        logger.info(f"[{host} - HTTP/{http_version}] {method} {path} {reason} - {process_time_ms}ms")

        return response


def setup_logging_middleware(app: FastAPI) -> None:
    app.add_middleware(LoggingMiddleware)
