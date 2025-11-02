"""
Unit tests for route decorators.
"""

from typing import List

import pytest
from pydantic import BaseModel

from authentication.core import Constants
from authentication.core.routing import route, get, post, put, patch, delete, head, option, trace, RouteMetadata


# Test models
class Item(BaseModel):
    id: int
    name: str


class User(BaseModel):
    username: str
    email: str


# Test basic route decorator
def test_route_decorator_basic():
    """Route decorator attaches metadata to function."""

    @route(path="/test", methods=["GET"])
    def test_func():
        return {"test": "data"}

    assert hasattr(test_func, Constants.ROUTE_METADATA_ATTR)
    metadata = getattr(test_func, Constants.ROUTE_METADATA_ATTR)
    assert isinstance(metadata, RouteMetadata)
    assert metadata.path == "/test"
    assert metadata.methods == ["GET"]


def test_route_decorator_with_multiple_methods():
    """Route decorator supports multiple HTTP methods."""

    @route(path="/multi", methods=["GET", "POST"])
    def multi_method():
        return {}

    metadata = getattr(multi_method, Constants.ROUTE_METADATA_ATTR)
    assert set(metadata.methods) == {"GET", "POST"}


def test_route_decorator_with_response_model():
    """Route decorator accepts response_model parameter."""

    @route(path="/items", methods=["GET"], response_model=List[Item])
    def get_items():
        return []

    metadata = getattr(get_items, Constants.ROUTE_METADATA_ATTR)
    assert metadata.response_model == List[Item]


def test_route_decorator_with_status_code():
    """Route decorator accepts custom status_code."""

    @route(path="/create", methods=["POST"], status_code=201)
    def create_item():
        return {}

    metadata = getattr(create_item, Constants.ROUTE_METADATA_ATTR)
    assert metadata.status_code == 201


def test_route_decorator_with_tags():
    """Route decorator accepts tags parameter."""

    @route(path="/endpoint", methods=["GET"], tags=["items", "public"])
    def tagged_endpoint():
        return {}

    metadata = getattr(tagged_endpoint, Constants.ROUTE_METADATA_ATTR)
    assert metadata.tags == ["items", "public"]


def test_route_decorator_with_summary_and_description():
    """Route decorator accepts summary and description."""

    @route(
        path="/documented",
        methods=["GET"],
        summary="Get endpoint",
        description="This is a documented endpoint"
    )
    def documented():
        return {}

    metadata = getattr(documented, Constants.ROUTE_METADATA_ATTR)
    assert metadata.summary == "Get endpoint"
    assert metadata.description == "This is a documented endpoint"


def test_route_decorator_with_deprecated():
    """Route decorator accepts deprecated flag."""

    @route(path="/old", methods=["GET"], deprecated=True)
    def old_endpoint():
        return {}

    metadata = getattr(old_endpoint, Constants.ROUTE_METADATA_ATTR)
    assert metadata.deprecated is True


def test_route_decorator_preserves_function():
    """Route decorator preserves original function."""

    def original_func():
        """Original docstring."""
        return {"result": "data"}

    decorated = route(path="/test", methods=["GET"])(original_func)

    assert decorated.__name__ == "original_func"
    assert decorated.__doc__ == "Original docstring."
    assert decorated() == {"result": "data"}


# Test HTTP method-specific decorators
def test_get_decorator():
    """GET decorator sets method to GET."""

    @get(path="/users")
    def get_users():
        return []

    metadata = getattr(get_users, Constants.ROUTE_METADATA_ATTR)
    assert metadata.path == "/users"
    assert metadata.methods == ["GET"]


def test_post_decorator():
    """POST decorator sets method to POST."""

    @post(path="/users")
    def create_user():
        return {}

    metadata = getattr(create_user, Constants.ROUTE_METADATA_ATTR)
    assert metadata.path == "/users"
    assert metadata.methods == ["POST"]


def test_put_decorator():
    """PUT decorator sets method to PUT."""

    @put(path="/users/{user_id}")
    def update_user():
        return {}

    metadata = getattr(update_user, Constants.ROUTE_METADATA_ATTR)
    assert metadata.path == "/users/{user_id}"
    assert metadata.methods == ["PUT"]


def test_patch_decorator():
    """PATCH decorator sets method to PATCH."""

    @patch(path="/users/{user_id}")
    def partial_update():
        return {}

    metadata = getattr(partial_update, Constants.ROUTE_METADATA_ATTR)
    assert metadata.path == "/users/{user_id}"
    assert metadata.methods == ["PATCH"]


def test_delete_decorator():
    """DELETE decorator sets method to DELETE."""

    @delete(path="/users/{user_id}")
    def delete_user():
        return {}

    metadata = getattr(delete_user, Constants.ROUTE_METADATA_ATTR)
    assert metadata.path == "/users/{user_id}"
    assert metadata.methods == ["DELETE"]


def test_head_decorator():
    """HEAD decorator sets method to HEAD."""

    @head(path="/users")
    def head_users():
        return {}

    metadata = getattr(head_users, Constants.ROUTE_METADATA_ATTR)
    assert metadata.path == "/users"
    assert metadata.methods == ["HEAD"]


def test_option_decorator():
    """OPTION decorator sets method to OPTION."""

    @option(path="/users")
    def options_users():
        return {}

    metadata = getattr(options_users, Constants.ROUTE_METADATA_ATTR)
    assert metadata.path == "/users"
    assert metadata.methods == ["OPTION"]


def test_trace_decorator():
    """TRACE decorator sets method to TRACE."""

    @trace(path="/users")
    def trace_users():
        return {}

    metadata = getattr(trace_users, Constants.ROUTE_METADATA_ATTR)
    assert metadata.path == "/users"
    assert metadata.methods == ["TRACE"]


# Test decorator parameters
def test_get_with_response_model():
    """GET decorator accepts response_model."""

    @get(path="/items", response_model=List[Item])
    def get_items():
        return []

    metadata = getattr(get_items, Constants.ROUTE_METADATA_ATTR)
    assert metadata.response_model == List[Item]


def test_post_with_status_code():
    """POST decorator accepts custom status_code."""

    @post(path="/items", status_code=201)
    def create_item():
        return {}

    metadata = getattr(create_item, Constants.ROUTE_METADATA_ATTR)
    assert metadata.status_code == 201


def test_put_with_tags():
    """PUT decorator accepts tags."""

    @put(path="/items/{id}", tags=["items", "admin"])
    def update_item():
        return {}

    metadata = getattr(update_item, Constants.ROUTE_METADATA_ATTR)
    assert metadata.tags == ["items", "admin"]


def test_delete_with_deprecated():
    """DELETE decorator accepts deprecated flag."""

    @delete(path="/old-items/{id}", deprecated=True)
    def delete_old_item():
        return {}

    metadata = getattr(delete_old_item, Constants.ROUTE_METADATA_ATTR)
    assert metadata.deprecated is True


# Test response model configuration
def test_response_model_exclude():
    """Decorator accepts response_model_exclude."""

    @get(path="/users", response_model_exclude={"password", "email"})
    def get_users():
        return []

    metadata = getattr(get_users, Constants.ROUTE_METADATA_ATTR)
    assert metadata.response_model_exclude == {"password", "email"}


def test_response_model_include():
    """Decorator accepts response_model_include."""

    @get(path="/users", response_model_include={"id", "username"})
    def get_users():
        return []

    metadata = getattr(get_users, Constants.ROUTE_METADATA_ATTR)
    assert metadata.response_model_include == {"id", "username"}


def test_response_model_exclude_unset():
    """Decorator accepts response_model_exclude_unset."""

    @get(path="/items", response_model_exclude_unset=True)
    def get_items():
        return []

    metadata = getattr(get_items, Constants.ROUTE_METADATA_ATTR)
    assert metadata.response_model_exclude_unset is True


def test_response_model_exclude_none():
    """Decorator accepts response_model_exclude_none."""

    @get(path="/items", response_model_exclude_none=True)
    def get_items():
        return []

    metadata = getattr(get_items, Constants.ROUTE_METADATA_ATTR)
    assert metadata.response_model_exclude_none is True


# Test OpenAPI configuration
def test_operation_id():
    """Decorator accepts operation_id."""

    @get(path="/items", operation_id="list_all_items")
    def get_items():
        return []

    metadata = getattr(get_items, Constants.ROUTE_METADATA_ATTR)
    assert metadata.operation_id == "list_all_items"


def test_include_in_schema():
    """Decorator accepts include_in_schema."""

    @get(path="/internal", include_in_schema=False)
    def internal_endpoint():
        return {}

    metadata = getattr(internal_endpoint, Constants.ROUTE_METADATA_ATTR)
    assert metadata.include_in_schema is False


def test_openapi_extra():
    """Decorator accepts openapi_extra."""
    extra = {"x-custom": "value"}

    @get(path="/custom", openapi_extra=extra)
    def custom_endpoint():
        return {}

    metadata = getattr(custom_endpoint, Constants.ROUTE_METADATA_ATTR)
    assert metadata.openapi_extra == extra


def test_responses_parameter():
    """Decorator accepts responses parameter."""
    responses = {
        404: {"description": "Item not found"},
        400: {"description": "Bad request"}
    }

    @get(path="/items/{id}", responses=responses)
    def get_item():
        return {}

    metadata = getattr(get_item, Constants.ROUTE_METADATA_ATTR)
    assert metadata.responses == responses


def test_response_description():
    """Decorator accepts custom response_description."""

    @get(path="/items", response_description="List of items returned successfully")
    def get_items():
        return []

    metadata = getattr(get_items, Constants.ROUTE_METADATA_ATTR)
    assert metadata.response_description == "List of items returned successfully"


# Test async functions
def test_decorator_on_async_function():
    """Decorators work with async functions."""

    @get(path="/async-items")
    async def get_async_items():
        return []

    assert hasattr(get_async_items, Constants.ROUTE_METADATA_ATTR)
    metadata = getattr(get_async_items, Constants.ROUTE_METADATA_ATTR)
    assert metadata.path == "/async-items"


# Test path parameters
def test_path_with_parameters():
    """Decorator handles path parameters."""

    @get(path="/users/{user_id}/items/{item_id}")
    def get_user_item():
        return {}

    metadata = getattr(get_user_item, Constants.ROUTE_METADATA_ATTR)
    assert metadata.path == "/users/{user_id}/items/{item_id}"


# Test multiple decorators on same function
def test_multiple_decorators():
    """Last decorator wins when multiple decorators applied."""

    @post(path="/second")
    @get(path="/first")
    def multi_decorated():
        return {}

    # Last decorator (post) should be the active one
    metadata = getattr(multi_decorated, Constants.ROUTE_METADATA_ATTR)
    assert metadata.path == "/second"
    assert metadata.methods == ["POST"]


# Test name parameter
def test_name_parameter():
    """Decorator accepts name parameter."""

    @get(path="/items", name="list_items")
    def get_items():
        return []

    metadata = getattr(get_items, Constants.ROUTE_METADATA_ATTR)
    assert metadata.name == "list_items"


# Test all HTTP methods have consistent behavior
@pytest.mark.parametrize("decorator,method", [
    (get, "GET"),
    (post, "POST"),
    (put, "PUT"),
    (patch, "PATCH"),
    (delete, "DELETE"),
    (head, "HEAD"),
    (option, "OPTION"),
    (trace, "TRACE"),
])
def test_all_http_methods(decorator, method):
    """All HTTP method decorators set correct method."""

    @decorator(path="/test")
    def test_func():
        return {}

    metadata = getattr(test_func, Constants.ROUTE_METADATA_ATTR)
    assert metadata.methods == [method]


# Test route_class_override parameter
def test_route_decorator_route_class_override():
    """Route decorator accepts route_class_override in kwargs."""
    from fastapi.routing import APIRoute

    class CustomRoute(APIRoute):
        pass

    @route(path="/test", methods=["GET"], route_class_override=CustomRoute)
    def test_func():
        return {}

    metadata = getattr(test_func, Constants.ROUTE_METADATA_ATTR)
    assert metadata.route_class_override == CustomRoute


# Test edge cases
def test_empty_tags_list():
    """Decorator accepts empty tags list."""

    @get(path="/test", tags=[])
    def test_func():
        return {}

    metadata = getattr(test_func, Constants.ROUTE_METADATA_ATTR)
    assert metadata.tags == []


def test_none_parameters():
    """Decorator handles None parameters correctly."""

    @get(
        path="/test",
        response_model=None,
        status_code=None,
        tags=None
    )
    def test_func():
        return {}

    metadata = getattr(test_func, Constants.ROUTE_METADATA_ATTR)
    assert metadata.response_model is None
    assert metadata.status_code is None
    assert metadata.tags is None


def test_decorator_with_class_method():
    """Decorator works with class methods."""

    class TestClass:
        @get(path="/method")
        def test_method(self):
            return {}

    instance = TestClass()
    assert hasattr(instance.test_method, Constants.ROUTE_METADATA_ATTR)


def test_decorator_with_static_method():
    """Decorator works with static methods."""

    class TestClass:
        @staticmethod
        @get(path="/static")
        def test_static():
            return {}

    assert hasattr(TestClass.test_static, Constants.ROUTE_METADATA_ATTR)
