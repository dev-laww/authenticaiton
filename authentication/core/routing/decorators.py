import re
from enum import Enum
from typing import Optional, Type, Any, Sequence, Union, List, Dict, Callable, Set

from fastapi import params
from fastapi.datastructures import Default
from fastapi.routing import APIRoute
from h11 import Response
from semver import Version
from starlette.responses import JSONResponse
from starlette.routing import BaseRoute

from .dto import RouteMetadata, SetIntStr, DictIntStrAny, AnyCallable, VersionMetadata
from ..constants import Constants


# TODO: add websocket route support

def _parse_version(version: str) -> Version:
    semver_regex = re.compile(Constants.SEMVER_REGEX, re.VERBOSE)

    match = semver_regex.match(version)
    if not match:
        raise ValueError(f"Invalid version string: {version}")

    major = match.group("major")
    minor = match.group("minor") or "0"
    patch = match.group("patch") or "0"
    prerelease = match.group("prerelease")
    build = match.group("build")

    normalized = f"{major}.{minor}.{patch}"
    if prerelease:
        normalized += f"-{prerelease}"
    if build:
        normalized += f"+{build}"

    return Version.parse(normalized)


def route(
    path: str,
    *,
    response_model: Optional[Type[Any]] = None,
    status_code: Optional[int] = None,
    tags: Optional[List[Union[str, Enum]]] = None,
    dependencies: Optional[Sequence[params.Depends]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    response_description: str = "Successful Response",
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
    deprecated: Optional[bool] = None,
    methods: Optional[Union[Set[str], List[str]]] = None,
    operation_id: Optional[str] = None,
    response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: Type[Response] = Default(JSONResponse),
    name: Optional[str] = None,
    route_class_override: Optional[Type[APIRoute]] = None,
    callbacks: Optional[List[BaseRoute]] = None,
    openapi_extra: Optional[Dict[str, Any]] = None,
    version: Optional[str] = None,
    deprecated_in: Optional[str] = None,
    removed_in: Optional[str] = None,
    **kwargs: Any
):
    def decorator(method: AnyCallable):
        parsed_version = _parse_version(version) if version else Version.parse("1.0.0")
        parsed_deprecated_in = _parse_version(deprecated_in) if deprecated_in else None
        parsed_removed_in = _parse_version(removed_in) if removed_in else None

        version_metadata = VersionMetadata(
            path=path,
            method=methods[0] if methods else 'GET',
            version=parsed_version,
            deprecated_in=parsed_deprecated_in,
            removed_in=parsed_removed_in
        )

        route_metadata = RouteMetadata(
            path=path,
            response_model=response_model,
            status_code=status_code,
            tags=tags,
            dependencies=dependencies,
            summary=summary,
            description=description,
            response_description=response_description,
            responses=responses,
            deprecated=deprecated,
            methods=methods,
            operation_id=operation_id,
            response_model_include=response_model_include,
            response_model_exclude=response_model_exclude,
            response_model_by_alias=response_model_by_alias,
            response_model_exclude_unset=response_model_exclude_unset,
            response_model_exclude_defaults=response_model_exclude_defaults,
            response_model_exclude_none=response_model_exclude_none,
            include_in_schema=include_in_schema,
            response_class=response_class,
            name=name,
            route_class_override=route_class_override,
            callbacks=callbacks,
            openapi_extra=openapi_extra,
            **kwargs  # noqa
        )

        setattr(method, Constants.VERSION_METADATA_ATTR, version_metadata)
        setattr(method, Constants.ROUTE_METADATA_ATTR, route_metadata)
        return method

    return decorator


def get(
    path: str,
    *,
    response_model: Optional[Type[Any]] = None,
    status_code: Optional[int] = None,
    tags: Optional[List[Union[str, Enum]]] = None,
    dependencies: Optional[Sequence[params.Depends]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    response_description: str = "Successful Response",
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
    deprecated: Optional[bool] = None,
    operation_id: Optional[str] = None,
    response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: Type[Response] = Default(JSONResponse),
    name: Optional[str] = None,
    callbacks: Optional[List[BaseRoute]] = None,
    openapi_extra: Optional[Dict[str, Any]] = None,
    version: Optional[str] = None,
    deprecated_in: Optional[str] = None,
    removed_in: Optional[str] = None,
    **kwargs: Any
) -> Callable[[AnyCallable], AnyCallable]:
    return route(
        path,
        methods=['GET'],
        response_model=response_model,
        status_code=status_code,
        tags=tags,
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=responses,
        deprecated=deprecated,
        operation_id=operation_id,
        response_model_include=response_model_include,
        response_model_exclude=response_model_exclude,
        response_model_by_alias=response_model_by_alias,
        response_model_exclude_unset=response_model_exclude_unset,
        response_model_exclude_defaults=response_model_exclude_defaults,
        response_model_exclude_none=response_model_exclude_none,
        include_in_schema=include_in_schema,
        response_class=response_class,
        name=name,
        callbacks=callbacks,
        openapi_extra=openapi_extra,
        version=version,
        deprecated_in=deprecated_in,
        removed_in=removed_in,
        **kwargs
    )


def post(
    path: str,
    *,
    response_model: Optional[Type[Any]] = None,
    status_code: Optional[int] = None,
    tags: Optional[List[Union[str, Enum]]] = None,
    dependencies: Optional[Sequence[params.Depends]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    response_description: str = "Successful Response",
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
    deprecated: Optional[bool] = None,
    operation_id: Optional[str] = None,
    response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: Type[Response] = Default(JSONResponse),
    name: Optional[str] = None,
    callbacks: Optional[List[BaseRoute]] = None,
    openapi_extra: Optional[Dict[str, Any]] = None,
    version: Optional[str] = None,
    deprecated_in: Optional[str] = None,
    removed_in: Optional[str] = None,
    **kwargs: Any
) -> Callable[[AnyCallable], AnyCallable]:
    return route(
        path,
        methods=['POST'],
        response_model=response_model,
        status_code=status_code,
        tags=tags,
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=responses,
        deprecated=deprecated,
        operation_id=operation_id,
        response_model_include=response_model_include,
        response_model_exclude=response_model_exclude,
        response_model_by_alias=response_model_by_alias,
        response_model_exclude_unset=response_model_exclude_unset,
        response_model_exclude_defaults=response_model_exclude_defaults,
        response_model_exclude_none=response_model_exclude_none,
        include_in_schema=include_in_schema,
        response_class=response_class,
        name=name,
        callbacks=callbacks,
        openapi_extra=openapi_extra,
        version=version,
        deprecated_in=deprecated_in,
        removed_in=removed_in,
        **kwargs
    )


def put(
    path: str,
    *,
    response_model: Optional[Type[Any]] = None,
    status_code: Optional[int] = None,
    tags: Optional[List[Union[str, Enum]]] = None,
    dependencies: Optional[Sequence[params.Depends]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    response_description: str = "Successful Response",
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
    deprecated: Optional[bool] = None,
    operation_id: Optional[str] = None,
    response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: Type[Response] = Default(JSONResponse),
    name: Optional[str] = None,
    callbacks: Optional[List[BaseRoute]] = None,
    openapi_extra: Optional[Dict[str, Any]] = None,
    version: Optional[str] = None,
    deprecated_in: Optional[str] = None,
    removed_in: Optional[str] = None,
    **kwargs: Any
) -> Callable[[AnyCallable], AnyCallable]:
    return route(
        path,
        methods=['PUT'],
        response_model=response_model,
        status_code=status_code,
        tags=tags,
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=responses,
        deprecated=deprecated,
        operation_id=operation_id,
        response_model_include=response_model_include,
        response_model_exclude=response_model_exclude,
        response_model_by_alias=response_model_by_alias,
        response_model_exclude_unset=response_model_exclude_unset,
        response_model_exclude_defaults=response_model_exclude_defaults,
        response_model_exclude_none=response_model_exclude_none,
        include_in_schema=include_in_schema,
        response_class=response_class,
        name=name,
        callbacks=callbacks,
        openapi_extra=openapi_extra,
        version=version,
        deprecated_in=deprecated_in,
        removed_in=removed_in,
        **kwargs
    )


def patch(
    path: str,
    *,
    response_model: Optional[Type[Any]] = None,
    status_code: Optional[int] = None,
    tags: Optional[List[Union[str, Enum]]] = None,
    dependencies: Optional[Sequence[params.Depends]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    response_description: str = "Successful Response",
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
    deprecated: Optional[bool] = None,
    operation_id: Optional[str] = None,
    response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: Type[Response] = Default(JSONResponse),
    name: Optional[str] = None,
    callbacks: Optional[List[BaseRoute]] = None,
    openapi_extra: Optional[Dict[str, Any]] = None,
    version: Optional[str] = None,
    deprecated_in: Optional[str] = None,
    removed_in: Optional[str] = None,
    **kwargs: Any
) -> Callable[[AnyCallable], AnyCallable]:
    return route(
        path,
        methods=['PATCH'],
        response_model=response_model,
        status_code=status_code,
        tags=tags,
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=responses,
        deprecated=deprecated,
        operation_id=operation_id,
        response_model_include=response_model_include,
        response_model_exclude=response_model_exclude,
        response_model_by_alias=response_model_by_alias,
        response_model_exclude_unset=response_model_exclude_unset,
        response_model_exclude_defaults=response_model_exclude_defaults,
        response_model_exclude_none=response_model_exclude_none,
        include_in_schema=include_in_schema,
        response_class=response_class,
        name=name,
        callbacks=callbacks,
        openapi_extra=openapi_extra,
        version=version,
        deprecated_in=deprecated_in,
        removed_in=removed_in,
        **kwargs
    )


def delete(
    path: str,
    *,
    response_model: Optional[Type[Any]] = None,
    status_code: Optional[int] = None,
    tags: Optional[List[Union[str, Enum]]] = None,
    dependencies: Optional[Sequence[params.Depends]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    response_description: str = "Successful Response",
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
    deprecated: Optional[bool] = None,
    operation_id: Optional[str] = None,
    response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: Type[Response] = Default(JSONResponse),
    name: Optional[str] = None,
    callbacks: Optional[List[BaseRoute]] = None,
    openapi_extra: Optional[Dict[str, Any]] = None,
    version: Optional[str] = None,
    deprecated_in: Optional[str] = None,
    removed_in: Optional[str] = None,
    **kwargs: Any
) -> Callable[[AnyCallable], AnyCallable]:
    return route(
        path,
        methods=['DELETE'],
        response_model=response_model,
        status_code=status_code,
        tags=tags,
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=responses,
        deprecated=deprecated,
        operation_id=operation_id,
        response_model_include=response_model_include,
        response_model_exclude=response_model_exclude,
        response_model_by_alias=response_model_by_alias,
        response_model_exclude_unset=response_model_exclude_unset,
        response_model_exclude_defaults=response_model_exclude_defaults,
        response_model_exclude_none=response_model_exclude_none,
        include_in_schema=include_in_schema,
        response_class=response_class,
        name=name,
        callbacks=callbacks,
        openapi_extra=openapi_extra,
        version=version,
        deprecated_in=deprecated_in,
        removed_in=removed_in,
        **kwargs
    )


def head(
    path: str,
    *,
    response_model: Optional[Type[Any]] = None,
    status_code: Optional[int] = None,
    tags: Optional[List[Union[str, Enum]]] = None,
    dependencies: Optional[Sequence[params.Depends]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    response_description: str = "Successful Response",
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
    deprecated: Optional[bool] = None,
    operation_id: Optional[str] = None,
    response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: Type[Response] = Default(JSONResponse),
    name: Optional[str] = None,
    callbacks: Optional[List[BaseRoute]] = None,
    openapi_extra: Optional[Dict[str, Any]] = None,
    version: Optional[str] = None,
    deprecated_in: Optional[str] = None,
    removed_in: Optional[str] = None,
    **kwargs: Any
) -> Callable[[AnyCallable], AnyCallable]:
    return route(
        path,
        methods=['HEAD'],
        response_model=response_model,
        status_code=status_code,
        tags=tags,
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=responses,
        deprecated=deprecated,
        operation_id=operation_id,
        response_model_include=response_model_include,
        response_model_exclude=response_model_exclude,
        response_model_by_alias=response_model_by_alias,
        response_model_exclude_unset=response_model_exclude_unset,
        response_model_exclude_defaults=response_model_exclude_defaults,
        response_model_exclude_none=response_model_exclude_none,
        include_in_schema=include_in_schema,
        response_class=response_class,
        name=name,
        callbacks=callbacks,
        openapi_extra=openapi_extra,
        version=version,
        deprecated_in=deprecated_in,
        removed_in=removed_in,
        **kwargs
    )


def option(
    path: str,
    *,
    response_model: Optional[Type[Any]] = None,
    status_code: Optional[int] = None,
    tags: Optional[List[Union[str, Enum]]] = None,
    dependencies: Optional[Sequence[params.Depends]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    response_description: str = "Successful Response",
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
    deprecated: Optional[bool] = None,
    operation_id: Optional[str] = None,
    response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: Type[Response] = Default(JSONResponse),
    name: Optional[str] = None,
    callbacks: Optional[List[BaseRoute]] = None,
    openapi_extra: Optional[Dict[str, Any]] = None,
    version: Optional[str] = None,
    deprecated_in: Optional[str] = None,
    removed_in: Optional[str] = None,
    **kwargs: Any
) -> Callable[[AnyCallable], AnyCallable]:
    return route(
        path,
        methods=['OPTION'],
        response_model=response_model,
        status_code=status_code,
        tags=tags,
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=responses,
        deprecated=deprecated,
        operation_id=operation_id,
        response_model_include=response_model_include,
        response_model_exclude=response_model_exclude,
        response_model_by_alias=response_model_by_alias,
        response_model_exclude_unset=response_model_exclude_unset,
        response_model_exclude_defaults=response_model_exclude_defaults,
        response_model_exclude_none=response_model_exclude_none,
        include_in_schema=include_in_schema,
        response_class=response_class,
        name=name,
        callbacks=callbacks,
        openapi_extra=openapi_extra,
        version=version,
        deprecated_in=deprecated_in,
        removed_in=removed_in,
        **kwargs
    )


def trace(
    path: str,
    *,
    response_model: Optional[Type[Any]] = None,
    status_code: Optional[int] = None,
    tags: Optional[List[Union[str, Enum]]] = None,
    dependencies: Optional[Sequence[params.Depends]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    response_description: str = "Successful Response",
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
    deprecated: Optional[bool] = None,
    operation_id: Optional[str] = None,
    response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: Type[Response] = Default(JSONResponse),
    name: Optional[str] = None,
    callbacks: Optional[List[BaseRoute]] = None,
    openapi_extra: Optional[Dict[str, Any]] = None,
    version: Optional[str] = None,
    deprecated_in: Optional[str] = None,
    removed_in: Optional[str] = None,
    **kwargs: Any
) -> Callable[[AnyCallable], AnyCallable]:
    return route(
        path,
        methods=['TRACE'],
        response_model=response_model,
        status_code=status_code,
        tags=tags,
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=responses,
        deprecated=deprecated,
        operation_id=operation_id,
        response_model_include=response_model_include,
        response_model_exclude=response_model_exclude,
        response_model_by_alias=response_model_by_alias,
        response_model_exclude_unset=response_model_exclude_unset,
        response_model_exclude_defaults=response_model_exclude_defaults,
        response_model_exclude_none=response_model_exclude_none,
        include_in_schema=include_in_schema,
        response_class=response_class,
        name=name,
        callbacks=callbacks,
        openapi_extra=openapi_extra,
        version=version,
        deprecated_in=deprecated_in,
        removed_in=removed_in,
        **kwargs
    )
