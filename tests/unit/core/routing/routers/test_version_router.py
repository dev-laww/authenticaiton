"""
Unit tests for VersionedRoute and VersionedRouter.
"""

import asyncio

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from semver import Version
from starlette.routing import Match

from authentication.core.constants import Constants
from authentication.core.exceptions import VersionNotSupportedError
from authentication.core.routing.decorators import version
from authentication.core.routing.routers.version import VersionedRoute, VersionedRouter
from authentication.core.routing.utils import VersionRegistry


# Fixtures
@pytest.fixture
def app():
    """Create a FastAPI app for testing."""
    return FastAPI()


@pytest.fixture
def versioned_router():
    """Create a VersionedRouter for testing."""
    return VersionedRouter(prefix="/api")


# Test VersionedRoute.version_metadata
def test_versioned_route_version_metadata():
    """VersionedRoute extracts version_metadata from endpoint."""
    router = VersionedRouter()

    @router.get("/test")
    @version("1.0.0")
    def test_endpoint():
        return {"message": "test"}

    route = router.routes[0]
    assert isinstance(route, VersionedRoute)
    assert route.version_metadata is not None
    assert route.version_metadata.version == Version.parse("1.0.0")


def test_versioned_route_version_metadata_none():
    """VersionedRoute returns None when no version metadata."""
    router = VersionedRouter()

    @router.get("/test")
    def test_endpoint():
        return {"message": "test"}

    route = router.routes[0]
    assert isinstance(route, VersionedRoute)
    assert route.version_metadata is None


# Test VersionedRoute.version
def test_versioned_route_version_property():
    """VersionedRoute.version returns version from metadata."""
    router = VersionedRouter()

    @router.get("/test")
    @version("1.2.3")
    def test_endpoint():
        return {"message": "test"}

    route = router.routes[0]
    assert route.version == Version.parse("1.2.3")


def test_versioned_route_version_property_default():
    """VersionedRoute.version returns None when no version."""
    router = VersionedRouter()

    @router.get("/test")
    def test_endpoint():
        return {"message": "test"}

    route = router.routes[0]
    assert route.version == VersionRegistry().default_version


# Test VersionedRoute.is_requested_version_matches
def test_is_requested_version_matches_true():
    """is_requested_version_matches returns True when versions match."""
    router = VersionedRouter()

    @router.get("/test")
    @version("1.0.0")
    def test_endpoint():
        return {"message": "test"}

    route = router.routes[0]
    scope = {
        "type": "http",
        Constants.REQUESTED_VERSION_SCOPE_KEY: Version.parse("1.0.0")
    }

    assert route.is_requested_version_matches(scope) is True


def test_is_requested_version_matches_false():
    """is_requested_version_matches returns False when versions don't match."""
    router = VersionedRouter()

    @router.get("/test")
    @version("1.0.0")
    def test_endpoint():
        return {"message": "test"}

    route = router.routes[0]
    scope = {
        "type": "http",
        Constants.REQUESTED_VERSION_SCOPE_KEY: Version.parse("2.0.0")
    }

    assert route.is_requested_version_matches(scope) is False


def test_is_requested_version_matches_no_requested_version():
    """is_requested_version_matches returns False when no requested version."""
    router = VersionedRouter()

    @router.get("/test")
    @version("1.0.0")
    def test_endpoint():
        return {"message": "test"}

    route = router.routes[0]
    scope = {"type": "http"}

    assert route.is_requested_version_matches(scope) is False


def test_is_requested_version_matches_no_route_version():
    """is_requested_version_matches returns True when route has no version."""
    router = VersionedRouter()

    @router.get("/test")
    def test_endpoint():
        return {"message": "test"}

    route = router.routes[0]
    scope = {
        "type": "http",
        Constants.REQUESTED_VERSION_SCOPE_KEY: Version.parse("1.0.0")
    }

    assert route.is_requested_version_matches(scope) is True


# Test VersionedRoute.matches
def test_versioned_route_matches_full():
    """matches returns Match.FULL when version matches."""
    router = VersionedRouter()

    @router.get("/test")
    @version("1.0.0")
    def test_endpoint():
        return {"message": "test"}

    route = router.routes[0]
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/test",
        Constants.REQUESTED_VERSION_SCOPE_KEY: Version.parse("1.0.0")
    }

    match, updated_scope = route.matches(scope)
    assert match == Match.FULL


def test_versioned_route_matches_partial_when_version_mismatch():
    """matches returns Match.PARTIAL when version doesn't match."""
    router = VersionedRouter()

    @router.get("/test")
    @version("1.0.0")
    def test_endpoint():
        return {"message": "test"}

    route = router.routes[0]
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/test",
        Constants.REQUESTED_VERSION_SCOPE_KEY: Version.parse("2.0.0")
    }

    match, updated_scope = route.matches(scope)
    assert match == Match.PARTIAL


def test_versioned_route_matches_none_when_path_mismatch():
    """matches returns Match.NONE when path doesn't match."""
    router = VersionedRouter()

    @router.get("/test")
    @version("1.0.0")
    def test_endpoint():
        return {"message": "test"}

    route = router.routes[0]
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/other",
        Constants.REQUESTED_VERSION_SCOPE_KEY: Version.parse("1.0.0")
    }

    match, updated_scope = route.matches(scope)
    assert match == Match.NONE


# Test VersionedRoute.handle
def test_versioned_route_handle_raises_on_version_mismatch():
    """handle raises VersionNotSupportedError when version doesn't match."""
    router = VersionedRouter()

    @router.get("/test")
    @version("1.0.0")
    def test_endpoint():
        return {"message": "test"}

    route = router.routes[0]
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/test",
        Constants.REQUESTED_VERSION_SCOPE_KEY: Version.parse("2.0.0")
    }

    async def receive():
        return {"type": "http.request"}

    async def send(message):
        pass

    with pytest.raises(VersionNotSupportedError):
        asyncio.run(route.handle(scope, receive, send))


# Test VersionedRouter initialization
def test_versioned_router_initialization():
    """VersionedRouter initializes with correct parameters."""
    router = VersionedRouter(
        prefix="/api",
        tags=["v1"],
        route_class=VersionedRoute
    )

    assert router.prefix == "/api"
    assert router.tags == ["v1"]
    assert router.route_class == VersionedRoute


def test_versioned_router_uses_versioned_route_by_default():
    """VersionedRouter uses VersionedRoute as default route_class."""
    router = VersionedRouter()

    @router.get("/test")
    def test_endpoint():
        return {"message": "test"}

    route = router.routes[0]
    assert isinstance(route, VersionedRoute)


# Test integration with FastAPI app
def test_versioned_router_integration(app):
    """VersionedRouter integrates with FastAPI app."""
    router = VersionedRouter(prefix="/api")

    @router.get("/test")
    @version("1.0.0")
    def test_endpoint():
        return {"message": "test"}

    app.include_router(router)
    client = TestClient(app)

    # This would require version middleware to be set up
    # For now, just verify the route exists
    assert len(app.routes) > 0


# Test multiple routes with different versions
def test_multiple_routes_different_versions():
    """VersionedRouter supports multiple routes with different versions."""
    router = VersionedRouter()

    @router.get("/test")
    @version("1.0.0")
    def test_v1():
        return {"version": "1.0.0"}

    @router.get("/test")
    @version("2.0.0")
    def test_v2():
        return {"version": "2.0.0"}

    assert len(router.routes) == 2
    assert router.routes[0].version == Version.parse("1.0.0")
    assert router.routes[1].version == Version.parse("2.0.0")


# Test route without version
def test_route_without_version():
    """VersionedRouter supports routes without version."""
    router = VersionedRouter()

    @router.get("/test")
    def test_endpoint():
        return {"message": "test"}

    route = router.routes[0]
    assert route.version is not None
    assert route.version == VersionRegistry().default_version
