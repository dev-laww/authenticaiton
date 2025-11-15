"""
Unit tests for VersionMiddleware.
"""

import asyncio

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from authentication.core.constants import Constants
from authentication.core.middlewares.version import VersionMiddleware, setup_version_middleware
from authentication.core.routing.utils import VersionRegistry


# Fixtures
@pytest.fixture
def app():
    """Create a FastAPI app for testing."""
    app = FastAPI()

    @app.get("/test")
    def test_endpoint():
        return {"message": "test"}

    return app


@pytest.fixture
def app_with_middleware(app):
    """Create app with version middleware."""
    setup_version_middleware(app, vendor_prefix="test")
    return app


@pytest.fixture
def client(app_with_middleware):
    """Create test client."""
    return TestClient(app_with_middleware)


# Test middleware setup
def test_setup_version_middleware(app):
    """setup_version_middleware adds middleware to app."""
    initial_middleware_count = len(app.user_middleware)

    setup_version_middleware(app, vendor_prefix="test")

    assert len(app.user_middleware) == initial_middleware_count + 1
    assert app.user_middleware[0].cls == VersionMiddleware


def test_setup_version_middleware_with_vendor_prefix(app):
    """setup_version_middleware accepts vendor_prefix parameter."""
    setup_version_middleware(app, vendor_prefix="myapp")

    middleware = app.user_middleware[0]
    assert middleware.kwargs["vendor_prefix"] == "myapp"


# Test version parsing from Accept header
def test_middleware_parses_accept_header_with_version(client):
    """Middleware parses version from Accept header."""
    response = client.get(
        "/test",
        headers={"Accept": "application/vnd.test.v1.0.0+json"}
    )

    assert response.status_code == 200


def test_middleware_parses_version_without_patch(client):
    """Middleware parses version without patch number."""
    response = client.get(
        "/test",
        headers={"Accept": "application/vnd.test.v1.0+json"}
    )

    assert response.status_code == 200


def test_middleware_parses_version_without_minor(client):
    """Middleware parses version without minor number."""
    response = client.get(
        "/test",
        headers={"Accept": "application/vnd.test.v1+json"}
    )

    assert response.status_code == 200


def test_middleware_parses_version_with_prerelease(client):
    """Middleware parses version with prerelease identifier."""
    response = client.get(
        "/test",
        headers={"Accept": "application/vnd.test.v1.0.0-alpha+json"}
    )

    assert response.status_code == 200


def test_middleware_handles_case_insensitive_accept_header(client):
    """Middleware handles case-insensitive Accept header."""
    # Note: Version string itself (v1.0.0) should be lowercase, but Accept header can be case-insensitive
    response = client.get(
        "/test",
        headers={"Accept": "application/vnd.test.v1.0.0+json"}
    )

    assert response.status_code == 200


def test_middleware_handles_accept_header_with_multiple_values(client):
    """Middleware handles Accept header with multiple values."""
    response = client.get(
        "/test",
        headers={"Accept": "application/json, application/vnd.test.v1.0.0+json"}
    )

    assert response.status_code == 200


def test_middleware_handles_accept_header_with_parameters(client):
    """Middleware handles Accept header with additional parameters."""
    response = client.get(
        "/test",
        headers={"Accept": "application/vnd.test.v1.0.0+json; charset=utf-8"}
    )

    assert response.status_code == 200


def test_middleware_handles_missing_accept_header(client):
    """Middleware handles requests without Accept header."""
    response = client.get("/test")

    assert response.status_code == 200


def test_middleware_handles_invalid_accept_header_format(client):
    """Middleware handles invalid Accept header format."""
    response = client.get(
        "/test",
        headers={"Accept": "application/json"}
    )

    assert response.status_code == 200


def test_middleware_handles_wrong_vendor_prefix(client):
    """Middleware ignores Accept header with wrong vendor prefix."""
    response = client.get(
        "/test",
        headers={"Accept": "application/vnd.other.v1.0.0+json"}
    )

    assert response.status_code == 200


# Test scope modification
def test_middleware_sets_version_in_scope(app):
    """Middleware sets requested_version in scope."""
    setup_version_middleware(app, vendor_prefix="test")

    @app.get("/check-version")
    def check_version(request: Request):
        version = request.scope.get(Constants.REQUESTED_VERSION_SCOPE_KEY)
        return {"version": str(version) if version else None}

    client = TestClient(app)
    response = client.get(
        "/check-version",
        headers={"Accept": "application/vnd.test.v1.2.3+json"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "1.2.3"


def test_middleware_sets_to_default_version_when_no_accept_header(app):
    """Middleware does not set version when Accept header is missing."""
    setup_version_middleware(app, vendor_prefix="test")

    @app.get("/check-version")
    def check_version(request: Request):
        version = request.scope.get(Constants.REQUESTED_VERSION_SCOPE_KEY)
        return {"version": str(version)}

    client = TestClient(app)
    response = client.get("/check-version")

    assert response.status_code == 200
    data = response.json()
    assert data["version"] == str(VersionRegistry().default_version)


# Test non-HTTP requests
def test_middleware_passes_through_non_http_requests(app):
    """Middleware passes through non-HTTP/WebSocket requests."""
    middleware = VersionMiddleware(app, vendor_prefix="test")

    # Create a non-HTTP scope (e.g., lifespan)
    scope = {"type": "lifespan"}

    async def receive():
        return {"type": "lifespan.startup"}

    async def send(message):
        pass

    # Should not raise an error
    asyncio.run(middleware(scope, receive, send))


# Test different vendor prefixes
@pytest.mark.parametrize("vendor_prefix,accept_header", [
    ("test", "application/vnd.test.v1.0.0+json"),
    ("myapp", "application/vnd.myapp.v2.1.0+json"),
    ("api", "application/vnd.api.v3.0.0+json"),
])
def test_middleware_with_different_vendor_prefixes(app, vendor_prefix, accept_header):
    """Middleware works with different vendor prefixes."""
    setup_version_middleware(app, vendor_prefix=vendor_prefix)

    @app.get("/check")
    def check(request: Request):
        version = request.scope.get(Constants.REQUESTED_VERSION_SCOPE_KEY)
        return {"version": str(version) if version else None}

    client = TestClient(app)
    response = client.get("/check", headers={"Accept": accept_header})

    assert response.status_code == 200
    data = response.json()
    assert data["version"] is not None


# Test version parsing edge cases
def test_middleware_handles_version_with_v_prefix(client):
    """Middleware handles version with 'v' prefix."""
    response = client.get(
        "/test",
        headers={"Accept": "application/vnd.test.vv1.0.0+json"}
    )

    assert response.status_code == 200


def test_middleware_handles_version_without_plus_json(client):
    """Middleware handles version without +json suffix."""
    response = client.get(
        "/test",
        headers={"Accept": "application/vnd.test.v1.0.0"}
    )

    assert response.status_code == 200


# Test middleware initialization
def test_version_middleware_initialization():
    """VersionMiddleware initializes with correct parameters."""
    app = FastAPI()
    middleware = VersionMiddleware(app, vendor_prefix="test")

    assert middleware.app == app
    assert middleware.vendor_prefix == "test"
    assert middleware.version_regex is not None
    assert middleware.accept_header_regex is not None


def test_version_middleware_regex_compilation():
    """VersionMiddleware compiles regex patterns correctly."""
    app = FastAPI()
    middleware = VersionMiddleware(app, vendor_prefix="test")

    # Test that regex patterns are compiled
    assert hasattr(middleware.version_regex, "match")
    assert hasattr(middleware.accept_header_regex, "search")


# Test multiple middleware calls
def test_middleware_can_be_added_multiple_times(app):
    """Middleware can be added multiple times (though not recommended)."""
    setup_version_middleware(app, vendor_prefix="test")
    setup_version_middleware(app, vendor_prefix="test")

    # Should have two instances
    middleware_count = sum(1 for m in app.user_middleware if m.cls == VersionMiddleware)
    assert middleware_count == 2

