from typing import Optional, List, Tuple

from fastapi import FastAPI
from fastapi.routing import APIRoute
from semver import Version
from starlette.routing import BaseRoute, WebSocketRoute

from .dto import VersionMetadata
from .. import Constants
from ..base import AppObject
from ..logging import get_logger

logger = get_logger(__name__)


class VersionManager(AppObject):
    _app: Optional[FastAPI]
    _original_routes: Optional[List[BaseRoute]]

    def __init__(
        self,
        default_version: str = "1.0.0",
        latest_prefix: Optional[str] = None,
        include_main_docs: bool = True,
        include_main_openapi_route: bool = True,
        include_version_docs: bool = True,
        include_version_openapi_route: bool = True,
        include_versions_route: bool = False,
    ):
        self._default_version = default_version
        self._latest_prefix = latest_prefix
        self._include_main_docs = include_main_docs
        self._include_main_openapi_route = include_main_openapi_route
        self._include_version_docs = include_version_docs
        self._include_version_openapi_route = include_version_openapi_route
        self._include_versions_route = include_versions_route

    def apply(self, app: FastAPI):
        self._app = app
        self._original_routes = app.routes.copy()

        self._strip_routes()

        routes, deprecated_routes, removed_routes = self._get_routes_by_version()
        versions = list(set(route.version for route in routes))

        logger.info(f"Total versions discovered: {len(versions)}")
        logger.info(f"Discovered API versions: {[str(v) for v in versions]}")

        return versions

    def _get_routes_by_version(self) -> Tuple[List[VersionMetadata], List[VersionMetadata], List[VersionMetadata]]:
        all_routes: List[VersionMetadata] = []
        deprecated_routes: List[VersionMetadata] = []
        removed_routes: List[VersionMetadata] = []

        for route in self._original_routes:
            endpoint = getattr(route, 'endpoint', None)
            valid_route_types = (APIRoute, WebSocketRoute)
            endpoint_has_version_metadata = endpoint and hasattr(endpoint, Constants.VERSION_METADATA_ATTR)

            if not isinstance(route, valid_route_types) or not endpoint_has_version_metadata:
                continue

            version_metadata: VersionMetadata = getattr(route.endpoint, Constants.VERSION_METADATA_ATTR)

            all_routes.append(version_metadata)

        all_routes.sort(key=lambda x: x.version, reverse=True)

        latest_version = all_routes[0].version if all_routes else Version.parse(self._default_version)

        for version_info in all_routes:
            if version_info.removed_in and latest_version >= version_info.removed_in:
                removed_routes.append(version_info)

            if version_info.deprecated_in and latest_version >= version_info.deprecated_in:
                deprecated_routes.append(version_info)

        return all_routes, deprecated_routes, removed_routes

    def _strip_routes(self):
        paths_to_keep = []

        if self._include_main_docs:
            paths_to_keep.extend([
                self._app.docs_url,  # noqa
                self._app.redoc_url,  # noqa
                self._app.swagger_ui_oauth2_redirect_url  # noqa
            ])

        if self._include_main_openapi_route:
            paths_to_keep.append(self._app.openapi_url)  # noqa

        self._app.router.routes = [  # noqa
            route for route in self._app.routes if
            getattr(route, 'path') in paths_to_keep
        ]
