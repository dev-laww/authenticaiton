"""
Unit tests for AppRouter with class-based dependency injection support.
"""

from typing import Annotated

import pytest
from fastapi import Depends
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Adjust import path according to your project structure
from authentication.core.routing import AppRouter, route


# Fixtures for mock dependencies
@pytest.fixture
def mock_db():
    """Mock database session."""

    class MockDB:
        def query(self, model):
            return self

        def filter_by(self, **kwargs):
            return self

        def offset(self, n):
            return self

        def limit(self, n):
            return self

        def first(self):
            return {"id": 1, "name": "Test Item"}

        def all(self):
            return [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]

    return MockDB()


@pytest.fixture
def mock_user():
    """Mock authenticated user."""

    class User:
        id = 1
        username = "testuser"

    return User()


@pytest.fixture
def get_mock_db(mock_db):
    """Dependency function that returns mock db."""

    def _get_db():
        return mock_db

    return _get_db


@pytest.fixture
def get_mock_user(mock_user):
    """Dependency function that returns mock user."""

    def _get_user():
        return mock_user

    return _get_user


# Test basic initialization
def test_router_initialization():
    """Router initializes with correct parameters."""

    class TestRouter(AppRouter):
        def __init__(self):
            super().__init__(prefix="/test", tags=["test"])

    router = TestRouter()
    assert router.http_router.prefix == "/test"
    assert router.http_router.tags == ["test"]


def test_router_without_dependencies():
    """Router works without any dependencies."""

    class SimpleRouter(AppRouter):
        def __init__(self):
            super().__init__(prefix="/simple")

        @route(path="/hello", methods=["GET"])
        def hello(self):
            return {"message": "Hello World"}

    router = SimpleRouter()
    assert router.http_router is not None


# Test dependency patterns
def test_annotated_empty_depends(get_mock_db):
    """Annotated with empty Depends() uses type as dependency."""
    from fastapi.params import Depends as DependsClass

    class TestRouter(AppRouter):
        db: Annotated[type(get_mock_db()), Depends()]

        def __init__(self):
            super().__init__(prefix="/test")

        @route(path="/items", methods=["GET"])
        def get_items(self):
            return self.db.all()

    router = TestRouter()
    deps = router._get_class_dependencies()

    assert "db" in deps
    assert isinstance(deps["db"][1], DependsClass)


def test_annotated_explicit_dependency(get_mock_db):
    """Annotated with explicit dependency function."""

    class TestRouter(AppRouter):
        db: Annotated[type(get_mock_db()), Depends(get_mock_db)]

        def __init__(self):
            super().__init__(prefix="/test")

        @route(path="/users", methods=["GET"])
        def get_users(self):
            return self.db.all()

    router = TestRouter()
    deps = router._get_class_dependencies()

    assert "db" in deps
    assert deps["db"][1].dependency == get_mock_db


def test_traditional_depends_pattern(get_mock_db):
    """Traditional pattern without Annotated."""
    MockDB = type(get_mock_db())

    class TestRouter(AppRouter):
        db: MockDB = Depends(get_mock_db)

        def __init__(self):
            super().__init__(prefix="/test")

        @route(path="/data", methods=["GET"])
        def get_data(self):
            return self.db.all()

    router = TestRouter()
    deps = router._get_class_dependencies()

    assert len(deps) > 0


def test_multiple_dependencies(get_mock_db, get_mock_user):
    """Multiple dependencies in a single router."""
    MockDB = type(get_mock_db())
    MockUser = type(get_mock_user())

    class TestRouter(AppRouter):
        db: Annotated[MockDB, Depends(get_mock_db)]
        current_user: Annotated[MockUser, Depends(get_mock_user)]

        def __init__(self):
            super().__init__(prefix="/test")

        @route(path="/profile", methods=["GET"])
        def get_profile(self):
            return {"user": self.current_user.username}

    router = TestRouter()
    deps = router._get_class_dependencies()

    assert "db" in deps
    assert "current_user" in deps
    assert len(deps) == 2


# Test route registration
def test_route_metadata():
    """Route decorator attaches metadata correctly."""
    from authentication.core.constants import Constants

    class TestRouter(AppRouter):
        def __init__(self):
            super().__init__(prefix="/test")

        @route(path="/endpoint", methods=["POST"])
        def test_endpoint(self):
            return {"status": "ok"}

    router = TestRouter()
    method = getattr(router, "test_endpoint")

    assert hasattr(method, Constants.ROUTE_METADATA_ATTR)


def test_multiple_routes_registered():
    """Multiple routes are registered to http_router."""

    class TestRouter(AppRouter):
        def __init__(self):
            super().__init__(prefix="/test")

        @route(path="/a", methods=["GET"])
        def route_a(self):
            return {"route": "a"}

        @route(path="/b", methods=["POST"])
        def route_b(self):
            return {"route": "b"}

    router = TestRouter()
    assert len(router.http_router.routes) >= 2


def test_async_route_support():
    """Async routes are properly supported."""
    import inspect

    class TestRouter(AppRouter):
        def __init__(self):
            super().__init__(prefix="/test")

        @route(path="/async", methods=["GET"])
        async def async_endpoint(self):
            return {"async": True}

    router = TestRouter()
    method = getattr(router, "async_endpoint")

    assert inspect.iscoroutinefunction(method)


# Test endpoint wrapping
def test_wrapped_endpoint_removes_self(get_mock_db):
    """Wrapped endpoints don't have 'self' in signature."""
    import inspect

    MockDB = type(get_mock_db())

    class TestRouter(AppRouter):
        db: Annotated[MockDB, Depends(get_mock_db)]

        def __init__(self):
            super().__init__(prefix="/test")

        @route(path="/items/{item_id}", methods=["GET"])
        def get_item(self, item_id: int, limit: int = 10):
            return {"item_id": item_id}

    router = TestRouter()
    deps = router._get_class_dependencies()
    method = getattr(router, "get_item")

    wrapped = router._wrap_endpoint(method, deps)
    sig = inspect.signature(wrapped)
    param_names = list(sig.parameters.keys())

    assert "self" not in param_names
    assert "item_id" in param_names
    assert "limit" in param_names
    assert "db" in param_names


def test_dependency_injection_into_self(get_mock_db):
    """Dependencies are injected into self."""
    mock_db = get_mock_db()

    class TestRouter(AppRouter):
        db: Annotated[type(mock_db), Depends(get_mock_db)]

        def __init__(self):
            super().__init__(prefix="/test")

        @route(path="/check", methods=["GET"])
        def check_db(self):
            return {"has_db": hasattr(self, "db")}

    router = TestRouter()
    deps = router._get_class_dependencies()
    method = getattr(router, "check_db")
    wrapped = router._wrap_endpoint(method, deps)

    result = wrapped(db=mock_db)
    assert result["has_db"] is True


# Integration tests
def test_full_app_integration(get_mock_db):
    """Complete integration with FastAPI app."""
    app = FastAPI()
    MockDB = type(get_mock_db())

    class TestRouter(AppRouter):
        db: Annotated[MockDB, Depends(get_mock_db)]

        def __init__(self):
            super().__init__(prefix="/api", tags=["test"])

        @route(path="/items", methods=["GET"])
        def list_items(self, skip: int = 0, limit: int = 10):
            items = self.db.query(None).offset(skip).limit(limit).all()
            return {"items": items, "skip": skip, "limit": limit}

    router = TestRouter()
    app.include_router(router.http_router)

    client = TestClient(app)
    response = client.get("/api/items?skip=0&limit=5")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["skip"] == 0
    assert data["limit"] == 5


# Edge cases
def test_no_routes_defined():
    """Router with no routes works."""

    class EmptyRouter(AppRouter):
        def __init__(self):
            super().__init__(prefix="/empty")

    router = EmptyRouter()
    assert router.http_router is not None


def test_route_with_no_parameters(get_mock_db):
    """Route methods with no parameters besides self."""
    mock_db = get_mock_db()

    class TestRouter(AppRouter):
        db: Annotated[type(mock_db), Depends(get_mock_db)]

        def __init__(self):
            super().__init__(prefix="/test")

        @route(path="/simple", methods=["GET"])
        def simple_route(self):
            return {"message": "simple"}

    router = TestRouter()
    method = getattr(router, "simple_route")
    deps = router._get_class_dependencies()

    wrapped = router._wrap_endpoint(method, deps)
    result = wrapped(db=mock_db)

    assert result["message"] == "simple"


def test_docstring_preservation(get_mock_db):
    """Method docstrings are preserved in wrapped endpoints."""
    MockDB = type(get_mock_db())

    class TestRouter(AppRouter):
        db: Annotated[MockDB, Depends(get_mock_db)]

        def __init__(self):
            super().__init__(prefix="/test")

        @route(path="/documented", methods=["GET"])
        def documented_endpoint(self):
            """This is a documented endpoint."""
            return {"documented": True}

    router = TestRouter()
    method = getattr(router, "documented_endpoint")
    deps = router._get_class_dependencies()

    wrapped = router._wrap_endpoint(method, deps)

    assert wrapped.__doc__ == "This is a documented endpoint."


def test_method_name_preservation():
    """Method names are preserved."""

    class TestRouter(AppRouter):
        def __init__(self):
            super().__init__(prefix="/test")

        @route(path="/named", methods=["GET"])
        def my_endpoint(self):
            return {"name": "my_endpoint"}

    router = TestRouter()
    method = getattr(router, "my_endpoint")
    deps = router._get_class_dependencies()

    wrapped = router._wrap_endpoint(method, deps)

    assert wrapped.__name__ == "my_endpoint"
