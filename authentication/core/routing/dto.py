from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Type, List, Sequence, Dict, Union, Set, TypeVar

from fastapi import APIRouter
from fastapi import params
from fastapi.datastructures import DefaultPlaceholder, Default
from fastapi.routing import APIRoute
from h11 import Response
from starlette.responses import JSONResponse
from starlette.routing import Route

SetIntStr = Set[Union[int, str]]
DictIntStrAny = Dict[Union[int, str], Any]
AnyCallable = TypeVar('AnyCallable', bound=Callable[..., Any])


@dataclass
class RouterMetadata:
    """
    Container for a discovered router and its associated metadata.

    Attributes:
        router: The APIRouter instance
        metadata: Additional metadata about the router (e.g., tags, descriptions, flags)
    """
    router: APIRouter
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RouteMetadata:
    """The arguments APIRouter.add_api_route takes.

    Just a convenience for type safety, and so we can pass all the args needed by the underlying FastAPI route args via
    `**dataclasses.asdict(some_args)`.
    """
    path: str
    response_model: Optional[Type[Any]] = None
    status_code: Optional[int] = None
    tags: Optional[List[str]] = None
    dependencies: Optional[Sequence[params.Depends]] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    response_description: str = "Successful Response"
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None
    deprecated: Optional[bool] = None
    methods: Optional[Union[Set[str], List[str]]] = None
    operation_id: Optional[str] = None
    response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None
    response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None
    response_model_by_alias: bool = True
    response_model_exclude_unset: bool = False
    response_model_exclude_defaults: bool = False
    response_model_exclude_none: bool = False
    include_in_schema: bool = True
    response_class: Union[Type[Response], DefaultPlaceholder] = field(default_factory=lambda: Default(JSONResponse))
    name: Optional[str] = None
    route_class_override: Optional[Type[APIRoute]] = None
    callbacks: Optional[List[Route]] = None
    openapi_extra: Optional[Dict[str, Any]] = None

    class Config:
        arbitrary_types_allowed = True