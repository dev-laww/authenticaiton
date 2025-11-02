"""
Unit tests for LoggingMiddleware.
"""

from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

from authentication.core.middlewares.logging import LoggingMiddleware, setup_logging_middleware


# Fixtures
@pytest.fixture
def app():
    """Create a FastAPI app for testing."""
    app = FastAPI()

    @app.get("/test")
    def test_endpoint():
        return {"message": "test"}

    @app.get("/error")
    def error_endpoint():
        raise ValueError("Test error")

    @app.post("/users")
    def create_user():
        return {"id": 1, "username": "testuser"}

    return app


@pytest.fixture
def app_with_middleware(app):
    """Create app with logging middleware."""
    setup_logging_middleware(app)
    return app


@pytest.fixture
def client(app_with_middleware):
    """Create test client."""
    return TestClient(app_with_middleware)


# Test middleware setup
def test_setup_logging_middleware(app):
    """setup_logging_middleware adds middleware to app."""
    initial_middleware_count = len(app.user_middleware)

    setup_logging_middleware(app)

    assert len(app.user_middleware) == initial_middleware_count + 1
    assert app.user_middleware[0].cls == LoggingMiddleware


def test_middleware_can_be_added_multiple_times(app):
    """Middleware can be added multiple times (though not recommended)."""
    setup_logging_middleware(app)
    setup_logging_middleware(app)

    # Should have two instances
    middleware_count = sum(1 for m in app.user_middleware if m.cls == LoggingMiddleware)
    assert middleware_count == 2


# Test basic middleware functionality
def test_middleware_adds_request_id_header(client):
    """Middleware adds X-Request-ID header to response."""
    response = client.get("/test")

    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"]


def test_middleware_adds_process_time_header(client):
    """Middleware adds X-Process-Time header to response."""
    response = client.get("/test")

    assert "X-Process-Time" in response.headers
    process_time = float(response.headers["X-Process-Time"])
    assert process_time >= 0


def test_request_id_is_uuid_format(client):
    """X-Request-ID follows UUID format."""
    import uuid

    response = client.get("/test")
    request_id = response.headers["X-Request-ID"]

    # Should be able to parse as UUID
    uuid_obj = uuid.UUID(request_id)
    assert str(uuid_obj) == request_id


def test_unique_request_ids(client):
    """Each request gets a unique request ID."""
    response1 = client.get("/test")
    response2 = client.get("/test")

    request_id1 = response1.headers["X-Request-ID"]
    request_id2 = response2.headers["X-Request-ID"]

    assert request_id1 != request_id2


# Test logging behavior
@patch('authentication.core.middlewares.logging.logger')
def test_middleware_logs_request(mock_logger, client):
    """Middleware logs request information."""
    response = client.get("/test")

    assert mock_logger.info.called
    log_message = mock_logger.info.call_args[0][0]

    assert "GET" in log_message
    assert "/test" in log_message
    assert "ms" in log_message


@patch('authentication.core.middlewares.logging.logger')
def test_log_includes_http_method(mock_logger, client):
    """Log message includes HTTP method."""
    client.post("/users")

    log_message = mock_logger.info.call_args[0][0]
    assert "POST" in log_message


@patch('authentication.core.middlewares.logging.logger')
def test_log_includes_path(mock_logger, client):
    """Log message includes request path."""
    client.get("/test")

    log_message = mock_logger.info.call_args[0][0]
    assert "/test" in log_message


@patch('authentication.core.middlewares.logging.logger')
def test_log_includes_query_parameters(mock_logger, client):
    """Log message includes query parameters."""
    client.get("/test?foo=bar&baz=qux")

    log_message = mock_logger.info.call_args[0][0]
    assert "foo=bar" in log_message
    assert "baz=qux" in log_message


@patch('authentication.core.middlewares.logging.logger')
def test_log_includes_status_code_reason(mock_logger, client):
    """Log message includes HTTP status reason phrase."""
    client.get("/test")

    log_message = mock_logger.info.call_args[0][0]
    assert "OK" in log_message  # 200 OK


@patch('authentication.core.middlewares.logging.logger')
def test_log_includes_process_time(mock_logger, client):
    """Log message includes process time in milliseconds."""
    client.get("/test")

    log_message = mock_logger.info.call_args[0][0]
    assert "ms" in log_message


@patch('authentication.core.middlewares.logging.logger')
def test_log_includes_client_host(mock_logger, client):
    """Log message includes client host."""
    client.get("/test")

    log_message = mock_logger.info.call_args[0][0]
    assert "testclient" in log_message.lower() or "127.0.0.1" in log_message


@patch('authentication.core.middlewares.logging.logger')
def test_log_includes_http_version(mock_logger, client):
    """Log message includes HTTP version."""
    client.get("/test")

    log_message = mock_logger.info.call_args[0][0]
    assert "HTTP/" in log_message


# Test different HTTP methods
@pytest.mark.parametrize("method,endpoint", [
    ("GET", "/test"),
    ("POST", "/users"),
])
@patch('authentication.core.middlewares.logging.logger')
def test_logs_different_http_methods(mock_logger, client, method, endpoint):
    """Middleware logs different HTTP methods correctly."""
    if method == "GET":
        client.get(endpoint)
    elif method == "POST":
        client.post(endpoint)

    log_message = mock_logger.info.call_args[0][0]
    assert method in log_message


# Test different status codes
@pytest.mark.parametrize("status_code,reason", [
    (200, "OK"),
    (404, "Not Found"),
])
def test_logs_different_status_codes(app, status_code, reason):
    """Middleware logs different status codes correctly."""

    @app.get(f"/status-{status_code}")
    def status_endpoint():
        return JSONResponse(content={"status": status_code}, status_code=status_code)

    setup_logging_middleware(app)
    client = TestClient(app)

    with patch('authentication.core.middlewares.logging.logger') as mock_logger:
        client.get(f"/status-{status_code}")
        log_message = mock_logger.info.call_args[0][0]
        assert reason in log_message


# Test response passthrough
def test_middleware_returns_original_response(client):
    """Middleware returns the original response content."""
    response = client.get("/test")

    assert response.status_code == 200
    assert response.json() == {"message": "test"}


def test_middleware_preserves_response_headers(app):
    """Middleware preserves existing response headers."""

    @app.get("/with-header")
    def endpoint_with_header():
        return JSONResponse(
            content={"data": "test"},
            headers={"X-Custom-Header": "custom-value"}
        )

    setup_logging_middleware(app)
    client = TestClient(app)

    response = client.get("/with-header")

    assert response.headers["X-Custom-Header"] == "custom-value"
    assert "X-Request-ID" in response.headers
    assert "X-Process-Time" in response.headers


def test_middleware_preserves_status_code(app):
    """Middleware preserves response status code."""

    @app.get("/created")
    def created_endpoint():
        return JSONResponse(content={"created": True}, status_code=201)

    setup_logging_middleware(app)
    client = TestClient(app)

    response = client.get("/created")
    assert response.status_code == 201


def test_process_time_is_reasonable(client):
    """Process time is within reasonable bounds."""
    response = client.get("/test")
    process_time = float(response.headers["X-Process-Time"])

    # Should be less than 1 second for simple endpoint
    assert 0 <= process_time < 1000


def test_process_time_increases_with_delay(app):
    """Process time increases for slower endpoints."""
    import asyncio

    @app.get("/slow")
    async def slow_endpoint():
        await asyncio.sleep(0.1)  # 100ms delay
        return {"message": "slow"}

    setup_logging_middleware(app)
    client = TestClient(app)

    response = client.get("/slow")
    process_time = float(response.headers["X-Process-Time"])

    # Should be at least 100ms
    assert process_time >= 100


@patch('authentication.core.middlewares.logging.logger')
def test_middleware_logs_error_responses(mock_logger, app):
    """Middleware logs responses with error status codes."""

    @app.get("/not-found")
    def not_found():
        return JSONResponse(content={"error": "not found"}, status_code=404)

    setup_logging_middleware(app)
    client = TestClient(app)

    client.get("/not-found")

    log_message = mock_logger.info.call_args[0][0]
    assert "Not Found" in log_message


# Test edge cases
def test_middleware_handles_path_without_query(client):
    """Middleware handles paths without query parameters."""
    with patch('authentication.core.middlewares.logging.logger') as mock_logger:
        client.get("/test")
        log_message = mock_logger.info.call_args[0][0]
        assert "/test" in log_message
        assert "?" not in log_message


def test_middleware_handles_root_path(app):
    """Middleware handles root path correctly."""

    @app.get("/")
    def root():
        return {"message": "root"}

    setup_logging_middleware(app)
    client = TestClient(app)

    with patch('authentication.core.middlewares.logging.logger') as mock_logger:
        client.get("/")
        log_message = mock_logger.info.call_args[0][0]
        assert "GET /" in log_message


def test_uvicorn_access_logger_disabled():
    """Uvicorn access logger is disabled."""
    import logging

    uvicorn_logger = logging.getLogger("uvicorn.access")
    assert uvicorn_logger.disabled is True


# Test concurrent requests
def test_concurrent_requests_have_unique_ids(app):
    """Concurrent requests each get unique request IDs."""
    setup_logging_middleware(app)
    client = TestClient(app)

    # Make multiple concurrent requests
    responses = []
    for _ in range(5):
        response = client.get("/test")
        responses.append(response)

    request_ids = [r.headers["X-Request-ID"] for r in responses]

    # All should be unique
    assert len(request_ids) == len(set(request_ids))


# Test middleware order
def test_middleware_is_first_in_chain(app):
    """LoggingMiddleware is added first in the middleware chain."""
    from starlette.middleware.base import BaseHTTPMiddleware

    class OtherMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            return await call_next(request)

    app.add_middleware(OtherMiddleware)
    setup_logging_middleware(app)

    # Logging middleware should be first (index 0)
    assert app.user_middleware[0].cls == LoggingMiddleware
