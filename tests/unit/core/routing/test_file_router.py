# test_file_router_full.py

import sys
import types

from fastapi import APIRouter
from fastapi.routing import APIRoute

from authentication.core.routing.dto import RouterMetadata
from authentication.core.routing.extractor import Extractor
from authentication.core.routing.file_router import FileRouter, _resolve_base_path # noqa


# --- Dummy Extractors ---

class DummyExtractor(Extractor):
    """Returns a single simple router for testing."""

    def extract(self, module):
        router = APIRouter()

        @router.get("/test")
        def _(): return {"ok": True}

        return [RouterMetadata(router=router)]


# --- Base path tests ---

def test_resolve_base_path_absolute(tmp_path):
    path = _resolve_base_path(str(tmp_path))
    assert path == tmp_path.resolve()


def test_resolve_base_path_relative(tmp_path):
    rel = "subdir"
    base = tmp_path / rel
    base.mkdir()
    resolved = _resolve_base_path(rel, relative_to=str(tmp_path / "main.py"))
    assert resolved == base.resolve()


# --- File inclusion / exclusion ---

def test_should_include_file_filters(tmp_path):
    file = tmp_path / "__init__.py"
    fr = FileRouter(str(tmp_path), extractor=DummyExtractor())
    assert not fr._should_include_file(file)

    ok_file = tmp_path / "user_routes.py"
    ok_file.write_text("# test")
    assert fr._should_include_file(ok_file)


def test_find_python_files(tmp_path):
    (tmp_path / "ok.py").write_text("# ok")
    (tmp_path / "__init__.py").write_text("# skip")

    fr = FileRouter(str(tmp_path), recursive=False, extractor=DummyExtractor())
    files = fr._find_python_files()
    assert all(f.name != "__init__.py" for f in files)
    assert any(f.name == "ok.py" for f in files)


# --- Module processing / router registration ---

def test_process_module_registers_router(tmp_path, monkeypatch):
    # Dummy module file
    mod_dir = tmp_path / "routes"
    mod_dir.mkdir()
    mod_file = mod_dir / "user_routes.py"
    mod_file.write_text("x = 1")

    dummy_router = APIRouter()

    @dummy_router.get("/ping")
    def ping(): return {"pong": True}

    dummy_module = types.ModuleType("user_routes")
    monkeypatch.setitem(sys.modules, "user_routes", dummy_module)

    class FakeExtractor(Extractor):
        def extract(self, module):
            return [RouterMetadata(router=dummy_router)]

    fr = FileRouter(str(mod_dir), extractor=FakeExtractor())
    # After registration, the router should have 1 route
    routes = [r for r in fr.routes if "/ping" in r.path]
    assert len(routes) == 1
    assert routes[0].path == "/ping"


def test_file_router_stats_and_errors(tmp_path):
    bad_dir = tmp_path / "not_exist"
    fr = FileRouter(str(bad_dir))
    stats = fr.stats
    assert stats["errors"]
    assert stats["modules_found"] == 0

def test_register_router_merges_tags(tmp_path):
    fr = FileRouter(str(tmp_path), extractor=DummyExtractor())

    router = APIRouter()

    @router.get("/a", tags=["tag1"])
    def a(): return {"ok": True}

    @router.get("/b")  # no tags
    def b(): return {"ok": True}

    fr._register_router(RouterMetadata(router=router))

    paths = [r.path for r in fr.routes]
    assert "/a" in paths and "/b" in paths
    for r in fr.routes:
        assert isinstance(r, APIRoute)


def test_find_project_root_with_indicator(tmp_path):
    (tmp_path / "setup.py").write_text("# dummy")
    fr = FileRouter(str(tmp_path))
    project_root = fr._find_project_root(tmp_path / "file.py")
    assert project_root == tmp_path


def test_find_project_root_fallback(tmp_path):
    fr = FileRouter(str(tmp_path))
    project_root = fr._find_project_root(tmp_path / "file.py")
    assert project_root == tmp_path.parent


def test_extractor_raises_exception(tmp_path):
    mod_file = tmp_path / "mod.py"
    mod_file.write_text("x=1")

    class BadExtractor(Extractor):
        def extract(self, module):
            raise RuntimeError("boom")

    fr = FileRouter(str(tmp_path), extractor=BadExtractor())
    stats = fr.stats
    assert any("boom" in e for e in stats["errors"])


def test_extractor_returns_invalid_router(tmp_path):
    mod_file = tmp_path / "mod.py"
    mod_file.write_text("x=1")

    class InvalidExtractor(Extractor):
        def extract(self, module):
            return [RouterMetadata(router="not a router")] # noqa

    fr = FileRouter(str(tmp_path), extractor=InvalidExtractor())
    stats = fr.stats
    assert any("non-APIRouter" in e for e in stats["errors"])


def test_recursive_discovery(tmp_path):
    subdir = tmp_path / "sub"
    subdir.mkdir()
    (subdir / "r.py").write_text("x=1")

    fr = FileRouter(str(tmp_path), recursive=True, extractor=DummyExtractor())
    found_files = fr._find_python_files()
    assert any("r.py" in str(f) for f in found_files)
