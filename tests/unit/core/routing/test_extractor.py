"""
Unit tests for router extractor classes.
"""

from types import ModuleType

import pytest
from fastapi import APIRouter

from authentication.core.routing.dto import RouterMetadata
from authentication.core.routing.extractor import Extractor, DefaultExtractor, MultiRouterExtractor


# Fixtures for mock modules
@pytest.fixture
def module_with_router():
    """Module with a single 'router' variable."""
    module = ModuleType("test_module")
    module.router = APIRouter(prefix="/test", tags=["test"])
    return module


@pytest.fixture
def module_with_custom_router():
    """Module with a custom-named router variable."""
    module = ModuleType("test_module")
    module.api_router = APIRouter(prefix="/api", tags=["api"])
    return module


@pytest.fixture
def module_with_multiple_routers():
    """Module with multiple router instances."""
    module = ModuleType("test_module")
    module.user_router = APIRouter(prefix="/users", tags=["users"])
    module.item_router = APIRouter(prefix="/items", tags=["items"])
    module.admin_router = APIRouter(prefix="/admin", tags=["admin"])
    return module


@pytest.fixture
def module_with_private_router():
    """Module with both public and private routers."""
    module = ModuleType("test_module")
    module.public_router = APIRouter(prefix="/public")
    module._private_router = APIRouter(prefix="/private")
    return module


@pytest.fixture
def module_without_router():
    """Module without any router."""
    module = ModuleType("test_module")
    module.some_function = lambda: "test"
    module.some_value = 42
    return module


@pytest.fixture
def module_with_non_router():
    """Module with a 'router' variable that's not an APIRouter."""
    module = ModuleType("test_module")
    module.router = {"not": "a router"}
    return module


# Test Abstract Base Class
def test_extractor_is_abstract():
    """Extractor cannot be instantiated directly."""
    with pytest.raises(TypeError):
        Extractor()  # noqa


def test_extractor_requires_extract_method():
    """Subclass must implement extract method."""

    class IncompleteExtractor(Extractor):  # noqa
        pass

    with pytest.raises(TypeError):
        IncompleteExtractor()  # noqa


def test_custom_extractor_implementation():
    """Custom extractor can be implemented."""

    class CustomExtractor(Extractor):
        def extract(self, module):
            return []

    extractor = CustomExtractor()
    assert extractor.extract(ModuleType("test")) == []


# Test DefaultExtractor
def test_default_extractor_initialization():
    """DefaultExtractor initializes with default router name."""

    extractor = DefaultExtractor()
    assert extractor.router_var_name == "router"


def test_default_extractor_custom_name():
    """DefaultExtractor can use custom router variable name."""

    extractor = DefaultExtractor(router_var_name="api_router")
    assert extractor.router_var_name == "api_router"


def test_default_extractor_finds_router(module_with_router):
    """DefaultExtractor finds standard router variable."""

    extractor = DefaultExtractor()
    routers = extractor.extract(module_with_router)

    assert len(routers) == 1
    assert isinstance(routers[0], RouterMetadata)
    assert isinstance(routers[0].router, APIRouter)
    assert routers[0].router.prefix == "/test"


def test_default_extractor_custom_name_finds_router(module_with_custom_router):
    """DefaultExtractor finds router with custom name."""

    extractor = DefaultExtractor(router_var_name="api_router")
    routers = extractor.extract(module_with_custom_router)

    assert len(routers) == 1
    assert routers[0].router.prefix == "/api"


def test_default_extractor_missing_router(module_without_router):
    """DefaultExtractor returns empty list when router not found."""

    extractor = DefaultExtractor()
    routers = extractor.extract(module_without_router)

    assert routers == []


def test_default_extractor_wrong_type(module_with_non_router):
    """DefaultExtractor ignores non-APIRouter variables."""

    extractor = DefaultExtractor()
    routers = extractor.extract(module_with_non_router)

    assert routers == []


def test_default_extractor_multiple_routers_only_finds_one(module_with_multiple_routers):
    """DefaultExtractor only finds the specified router variable."""

    extractor = DefaultExtractor(router_var_name="user_router")
    routers = extractor.extract(module_with_multiple_routers)

    assert len(routers) == 1
    assert routers[0].router.prefix == "/users"


# Test MultiRouterExtractor
def test_multi_extractor_initialization():
    """MultiRouterExtractor initializes with default exclude_private."""

    extractor = MultiRouterExtractor()
    assert extractor.exclude_private is True


def test_multi_extractor_custom_exclude_private():
    """MultiRouterExtractor can be configured to include private."""

    extractor = MultiRouterExtractor(exclude_private=False)
    assert extractor.exclude_private is False


def test_multi_extractor_finds_single_router(module_with_router):
    """MultiRouterExtractor finds single router."""

    extractor = MultiRouterExtractor()
    routers = extractor.extract(module_with_router)

    assert len(routers) == 1
    assert isinstance(routers[0].router, APIRouter)


def test_multi_extractor_finds_all_routers(module_with_multiple_routers):
    """MultiRouterExtractor finds all routers in module."""

    extractor = MultiRouterExtractor()
    routers = extractor.extract(module_with_multiple_routers)

    assert len(routers) == 3

    prefixes = {r.router.prefix for r in routers}
    assert prefixes == {"/users", "/items", "/admin"}


def test_multi_extractor_excludes_private_by_default(module_with_private_router):
    """MultiRouterExtractor excludes private routers by default."""

    extractor = MultiRouterExtractor()
    routers = extractor.extract(module_with_private_router)

    assert len(routers) == 1
    assert routers[0].router.prefix == "/public"


def test_multi_extractor_includes_private_when_configured(module_with_private_router):
    """MultiRouterExtractor includes private routers when configured."""

    extractor = MultiRouterExtractor(exclude_private=False)
    routers = extractor.extract(module_with_private_router)

    assert len(routers) == 2
    prefixes = {r.router.prefix for r in routers}
    assert prefixes == {"/public", "/private"}


def test_multi_extractor_empty_module(module_without_router):
    """MultiRouterExtractor returns empty list for module without routers."""

    extractor = MultiRouterExtractor()
    routers = extractor.extract(module_without_router)

    assert routers == []


def test_multi_extractor_ignores_non_routers(module_with_non_router):
    """MultiRouterExtractor ignores non-APIRouter attributes."""

    extractor = MultiRouterExtractor()
    routers = extractor.extract(module_with_non_router)

    assert routers == []


def test_multi_extractor_metadata_includes_variable_name(module_with_multiple_routers):
    """MultiRouterExtractor includes variable name in metadata."""

    extractor = MultiRouterExtractor()
    routers = extractor.extract(module_with_multiple_routers)

    variable_names = {r.metadata.get('variable_name') for r in routers}
    assert variable_names == {"user_router", "item_router", "admin_router"}


def test_multi_extractor_handles_attribute_error():
    """MultiRouterExtractor handles AttributeError gracefully."""

    module = ModuleType("test_module")

    # Add a property that raises AttributeError
    class ProblematicProperty:
        @property
        def bad_attr(self):
            raise AttributeError("Cannot access")

    module.problematic = ProblematicProperty()

    extractor = MultiRouterExtractor()
    routers = extractor.extract(module)

    # Should not raise, just return empty list
    assert routers == []


# Test edge cases
def test_default_extractor_with_none_module():
    """DefaultExtractor handles None module gracefully."""

    extractor = DefaultExtractor()
    routers = extractor.extract(None)

    assert routers == []


def test_multi_extractor_with_empty_dir():
    """MultiRouterExtractor handles modules with no attributes."""

    module = ModuleType("empty_module")

    extractor = MultiRouterExtractor()
    routers = extractor.extract(module)

    assert routers == []


def test_extractors_return_router_metadata_type(module_with_router):
    """Both extractors return RouterMetadata instances."""

    default_extractor = DefaultExtractor()
    multi_extractor = MultiRouterExtractor()

    default_result = default_extractor.extract(module_with_router)
    multi_result = multi_extractor.extract(module_with_router)

    assert all(isinstance(r, RouterMetadata) for r in default_result)
    assert all(isinstance(r, RouterMetadata) for r in multi_result)


def test_router_metadata_contains_valid_router(module_with_router):
    """RouterMetadata contains a valid APIRouter instance."""

    extractor = DefaultExtractor()
    routers = extractor.extract(module_with_router)

    router_metadata = routers[0]
    assert hasattr(router_metadata, 'router')
    assert isinstance(router_metadata.router, APIRouter)
    assert hasattr(router_metadata.router, 'routes')


# Test real-world scenarios
def test_mixed_module_content():
    """Extractor works with module containing mixed content."""

    module = ModuleType("mixed_module")
    module.router = APIRouter(prefix="/api")
    module.CONFIG = {"key": "value"}
    module.helper_function = lambda x: x * 2
    module.SomeClass = type("SomeClass", (), {})
    module.CONSTANT = 42

    extractor = MultiRouterExtractor()
    routers = extractor.extract(module)

    assert len(routers) == 1
    assert routers[0].router.prefix == "/api"


def test_module_with_router_subclass():
    """Extractor detects APIRouter subclasses."""

    class CustomRouter(APIRouter):
        pass

    module = ModuleType("custom_module")
    module.router = CustomRouter(prefix="/custom")

    extractor = DefaultExtractor()
    routers = extractor.extract(module)

    assert len(routers) == 1
    assert isinstance(routers[0].router, APIRouter)
    assert routers[0].router.prefix == "/custom"


def test_comparison_default_vs_multi_extractor(module_with_multiple_routers):
    """Compare DefaultExtractor vs MultiRouterExtractor behavior."""

    default_extractor = DefaultExtractor()
    multi_extractor = MultiRouterExtractor()

    default_result = default_extractor.extract(module_with_multiple_routers)
    multi_result = multi_extractor.extract(module_with_multiple_routers)

    assert len(default_result) == 0
    assert len(multi_result) == 3
