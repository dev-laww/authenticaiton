import importlib
import inspect
import sys
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter
from fastapi.routing import APIRoute

from .dto import RouterMetadata
from .extractor import Extractor, DefaultExtractor


def _resolve_base_path(base_path: str, relative_to: Optional[str] = None) -> Path:
    """
    Resolve the base path, handling relative paths intelligently.

    Args:
        base_path: The path to resolve (can be relative or absolute)
        relative_to: Optional file path to resolve relative paths against.
                    If None, attempts to detect the caller's file location.

    Returns:
        Resolved absolute Path object
    """
    path = Path(base_path)

    if path.is_absolute():
        return path.resolve()

    if relative_to:
        base = Path(relative_to).parent.resolve()
        return (base / path).resolve()

    try:
        frame = inspect.currentframe()
        if frame:
            # Skip frames within this module
            while frame:
                frame_info = inspect.getframeinfo(frame)
                frame_file = frame_info.filename

                # Skip this file and any __init__.py files in the routing module
                if not frame_file.endswith(('file_router.py', 'routing/__init__.py')):
                    caller_path = Path(frame_file).parent.resolve()
                    resolved = (caller_path / path).resolve()
                    return resolved

                frame = frame.f_back
    except Exception as e:
        raise e

    resolved = path.resolve()

    return resolved


class FileRouter(APIRouter):
    """
    A universal router that automatically discovers and registers routes from Python modules.

    This router extends APIRouter and scans a directory for Python files, automatically
    importing and registering any APIRouter instances it finds. It's completely
    structure-agnostic and uses an Extractor to define how routers are discovered.

    Usage:
        app.include_router(FileRouter("./routes"))
    """

    def __init__(
        self,
        base_path: str,
        prefix: str = "",
        tags: Optional[list[str]] = None,
        include_patterns: Optional[list[str]] = None,
        exclude_patterns: Optional[list[str]] = None,
        recursive: bool = True,
        extractor: Optional[Extractor] = None,
        relative_to: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """
        Initialize the FileRouter.

        Args:
            base_path: Base directory path to search for route modules.
                Can be absolute or relative. Relative paths are resolved:
                - Relative to the calling file's directory (auto-detected)
                - Or relative to 'relative_to' parameter if provided
            prefix: URL prefix to add to all discovered routes
            tags: Tags to add to all discovered routes
            include_patterns: List of glob patterns for files to include
            exclude_patterns: List of glob patterns for files to exclude
            recursive: Whether to search subdirectories recursively
            extractor: Custom Extractor instance for discovering routers in modules.
                If None, uses DefaultExtractor which looks for 'router' variable.
            relative_to: Optional file path (__file__) to resolve relative base_path against.
                If None, will attempt to auto-detect the caller's file location.
            **kwargs: Additional arguments passed to APIRouter
        """
        super().__init__(prefix=prefix, tags=tags or [], **kwargs)

        self.base_path = _resolve_base_path(base_path, relative_to)
        self.include_patterns = include_patterns or ["*.py"]
        self.exclude_patterns = exclude_patterns or ["__pycache__", "*.pyc", "__init__.py"]
        self.recursive = recursive
        self.extractor = extractor or DefaultExtractor()
        self.registered_routes = set()
        self._discovery_stats = {}

        # Automatically discover and register routes on initialization
        self._discover_and_register_routes()

    def _discover_and_register_routes(self) -> None:
        """
        Discover and register all routes from the specified directory.
        """
        self._discovery_stats = {
            "modules_found": 0,
            "routers_registered": 0,
            "errors": []
        }

        if not self.base_path.exists():
            error_msg = f"Base path does not exist: {self.base_path}"
            self._discovery_stats["errors"].append(error_msg)
            return

        python_files = self._find_python_files()
        self._discovery_stats["modules_found"] = len(python_files)

        for file_path in python_files:
            try:
                module_stats = self._process_module(file_path)
                self._discovery_stats["routers_registered"] += module_stats["routers_registered"]
                if module_stats["errors"]:
                    self._discovery_stats["errors"].extend(module_stats["errors"])
            except (ImportError, AttributeError, SyntaxError) as e:
                error_msg = f"Error processing {file_path}: {str(e)}"
                self._discovery_stats["errors"].append(error_msg)

    def _find_python_files(self) -> list[Path]:
        """Find all Python files matching the criteria."""
        python_files: list[Path] = []

        if self.recursive:
            for pattern in self.include_patterns:
                python_files.extend(self.base_path.rglob(pattern))
        else:
            for pattern in self.include_patterns:
                python_files.extend(self.base_path.glob(pattern))

        filtered_files: list[Path] = []
        for file_path in python_files:
            if self._should_include_file(file_path):
                filtered_files.append(file_path)

        return filtered_files

    def _should_include_file(self, file_path: Path) -> bool:
        """Check if a file should be included based on exclude patterns."""
        file_str = str(file_path)

        for exclude_pattern in self.exclude_patterns:
            if exclude_pattern in file_str or file_path.name == exclude_pattern:
                return False

        return True

    def _process_module(self, file_path: Path) -> dict[str, Any]:
        """Process a single Python module and register any routers found."""
        module_stats: dict[str, Any] = {
            "routers_registered": 0,
            "errors": []
        }

        try:
            module_name = file_path.stem

            if module_name in self.registered_routes:
                return module_stats

            project_root = self._find_project_root(file_path)
            if project_root and str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))

            try:
                full_module_name = self._get_full_module_name(file_path, project_root)
                module = importlib.import_module(full_module_name)

                # Use the extractor to discover routers
                try:
                    extracted_routers = self.extractor.extract(module)

                    for router_metadata in extracted_routers:
                        if isinstance(router_metadata.router, APIRouter):
                            self._register_router(router_metadata)
                            module_stats["routers_registered"] += 1
                        else:
                            error_msg = (
                                f"Extractor returned non-APIRouter instance "
                                f"from {full_module_name}: {type(router_metadata.router)}"
                            )
                            module_stats["errors"].append(error_msg)

                except Exception as e:
                    error_msg = f"Extractor failed for {full_module_name}: {str(e)}"
                    module_stats["errors"].append(error_msg)

                self.registered_routes.add(full_module_name)

            finally:
                if project_root and str(project_root) in sys.path:
                    sys.path.remove(str(project_root))

        except (ImportError, AttributeError, SyntaxError) as e:
            error_msg = f"Error processing module {file_path}: {str(e)}"
            module_stats["errors"].append(error_msg)

        return module_stats

    def _find_project_root(self, file_path: Path) -> Optional[Path]:
        """Find the project root by looking for common indicators."""
        current_path = file_path.parent
        indicators = ["pyproject.toml", "setup.py", "requirements.txt", "Pipfile", "poetry.lock"]

        while current_path != current_path.parent:
            for indicator in indicators:
                if (current_path / indicator).exists():
                    return current_path
            current_path = current_path.parent
        return self.base_path.parent

    @staticmethod
    def _get_full_module_name(file_path: Path, project_root: Optional[Path]) -> str:
        """Get the full module name for importing."""
        if project_root:
            relative_path = file_path.relative_to(project_root)
            module_name = str(relative_path).replace("/", ".").replace("\\", ".").replace(".py", "")
            return module_name
        else:
            return file_path.stem

    def _register_router(self, router_metadata: RouterMetadata) -> None:
        """
        Register a discovered router by including its routes.

        Args:
            router_metadata: RouterMetadata containing the router and its metadata
        """
        router = router_metadata.router

        # Include all routes from the discovered router into this FileRouter
        for route in router.routes:
            if isinstance(route, APIRoute):
                # Merge tags if both routers have them
                route_tags = list(route.tags) if route.tags else []
                if router.tags:
                    route_tags = list(set(route_tags + list(router.tags)))

                # Add the route to this FileRouter
                self.add_api_route(
                    path=route.path,
                    endpoint=route.endpoint,
                    methods=route.methods,
                    tags=route_tags or None,
                    summary=route.summary,
                    description=route.description,
                    response_model=route.response_model,
                    status_code=route.status_code,
                    responses=route.responses,
                    deprecated=route.deprecated,
                    operation_id=route.operation_id,
                    response_model_include=route.response_model_include,
                    response_model_exclude=route.response_model_exclude,
                    response_model_by_alias=route.response_model_by_alias,
                    response_model_exclude_unset=route.response_model_exclude_unset,
                    response_model_exclude_defaults=route.response_model_exclude_defaults,
                    response_model_exclude_none=route.response_model_exclude_none,
                    include_in_schema=route.include_in_schema,
                )

    @property
    def stats(self) -> dict[str, Any]:
        """Get discovery statistics."""
        return self._discovery_stats.copy()