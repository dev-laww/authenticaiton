import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from authentication.core.middlewares.rate_limit import setup_rate_limiting, limit, limiter  # noqa


@pytest.fixture
def app():
    """Create a fresh FastAPI app for each test."""
    return FastAPI()


# Tests for limiter initialization

def test_limiter_exists():
    """Test that the limiter instance exists."""
    assert limiter is not None
    assert isinstance(limiter, Limiter)


def test_limiter_key_function():
    """Test that the limiter uses get_remote_address as key function."""
    assert limiter._key_func == get_remote_address


# Tests for setup_rate_limiting function

def test_setup_adds_limiter_to_app_state(app):
    """Test that limiter is added to app state."""
    setup_rate_limiting(app)

    assert hasattr(app.state, 'limiter')
    assert app.state.limiter is limiter


def test_setup_adds_slowapi_middleware(app):
    """Test that SlowAPIMiddleware is added to the app."""
    initial_middleware_count = len(app.user_middleware)

    setup_rate_limiting(app)

    assert len(app.user_middleware) == initial_middleware_count + 1
    middleware_classes = [m.cls for m in app.user_middleware]
    assert SlowAPIMiddleware in middleware_classes


def test_setup_called_multiple_times(app):
    """Test that calling setup multiple times adds limiter correctly."""
    setup_rate_limiting(app)

    first_limiter = app.state.limiter

    setup_rate_limiting(app)

    # Limiter should be the same instance
    assert app.state.limiter is first_limiter


# Tests for limit decorator

def test_limit_returns_callable():
    """Test that limit returns a callable decorator."""
    decorator = limit("10/minute")
    assert callable(decorator)


def test_limit_decorator_with_route(app):
    """Test that limit decorator can be applied to a route."""
    setup_rate_limiting(app)

    @app.get("/test")
    @limit("5/minute")
    async def test_route(request: Request):
        return {"message": "success"}

    # Test that the route exists and works
    client = TestClient(app)
    response = client.get("/test")
    assert response.status_code == 200
    assert response.json() == {"message": "success"}


def test_limit_with_different_rates():
    """Test that limit accepts different rate formats."""
    rates = ["10/minute", "100/hour", "1000/day", "5/second"]

    for rate in rates:
        decorator = limit(rate)
        assert callable(decorator)


def test_limit_decorator_applies_rate_limiting(app):
    """Test that limit decorator actually enforces rate limits."""
    setup_rate_limiting(app)

    @app.get("/limited")
    @limit("2/minute")
    async def limited_route(request: Request):
        return {"message": "success"}

    client = TestClient(app)

    # First two requests should succeed
    response1 = client.get("/limited")
    assert response1.status_code == 200

    response2 = client.get("/limited")
    assert response2.status_code == 200

    # Third request should be rate limited
    response3 = client.get("/limited")
    assert response3.status_code == 429  # Too Many Requests


def test_multiple_routes_with_different_limits(app):
    """Test multiple routes with different rate limits."""
    setup_rate_limiting(app)

    @app.get("/route1")
    @limit("5/minute")
    async def route1(request: Request):
        return {"route": "1"}

    @app.get("/route2")
    @limit("10/minute")
    async def route2(request: Request):
        return {"route": "2"}

    client = TestClient(app)

    # Both routes should work
    response1 = client.get("/route1")
    assert response1.status_code == 200
    assert response1.json() == {"route": "1"}

    response2 = client.get("/route2")
    assert response2.status_code == 200
    assert response2.json() == {"route": "2"}


def test_route_without_rate_limit_uses_default(app):
    """Test that routes without explicit limits use default limits."""
    setup_rate_limiting(app)

    @app.get("/default")
    async def default_route():
        return {"message": "default"}

    client = TestClient(app)
    response = client.get("/default")

    # Should work without issues (default limits are high)
    assert response.status_code == 200
