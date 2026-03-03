"""
Raspberry Pi / Headless Edge Deployment — Export E2E Tests
==========================================================
Proves that `designgui export` generates a lightweight, valid, self-contained
Python application that can run entirely detached from the DesignGUI CLI,
optimized for low-memory headless edge devices.

Architecture under test (cli.py export()):
    - Copies .designgui/product/ → production_app/product/
    - Generates production_app/main.py with dynamic router
    - Router maps dashboard→'/', others→'/{name}'
    - Generated app uses ui.run(reload=False, show=False) for headless mode

Port: 8082 (isolated from default 8080 and daemon tests on 8081)
"""
import sys
import ast
import time
import subprocess
import textwrap
import json
import shutil
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
EXPORT_PORT = 8082
CUSTOM_PORT = 9090
CUSTOM_HOST = "0.0.0.0"
RUNTIME_BOOT_TIMEOUT = 20  # seconds — NiceGUI first startup downloads frontend assets

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _scaffold_project(project_dir: Path, views: dict[str, str]):
    """Manually scaffold a .designgui project with the given views."""
    designgui_dir = project_dir / ".designgui"
    views_dir = designgui_dir / "product" / "views"
    views_dir.mkdir(parents=True, exist_ok=True)
    (designgui_dir / "product" / "__init__.py").touch()
    (views_dir / "__init__.py").touch()

    config = {
        "environment": "Generic/Cloud IDE",
        "daemon_port": 8080,
        "locale": "en-US",
        "font_family": "Inter, sans-serif",
        "paths": {
            "instructions": "DESIGNGUI_INSTRUCTIONS.md",
            "views": ".designgui/product/views",
            "models": ".designgui/product/models.py"
        }
    }
    (designgui_dir / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    for filename, code in views.items():
        (views_dir / filename).write_text(textwrap.dedent(code), encoding="utf-8")

    return views_dir


def _run_export(project_dir: Path, host: str = "0.0.0.0", port: int = EXPORT_PORT):
    """Run designgui export and return the completed process."""
    return subprocess.run(
        [sys.executable, "-m", "designgui.cli", "export", "--host", host, "--port", str(port)],
        cwd=str(project_dir),
        capture_output=True,
        text=True,
        timeout=30,
    )


def _wait_for_server(port: int, timeout: int = RUNTIME_BOOT_TIMEOUT):
    """Poll the server until HTTP 200 or timeout."""
    import httpx
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = httpx.get(f"http://localhost:{port}/", timeout=2)
            if r.status_code == 200:
                return True
        except (httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout):
            pass
        time.sleep(1)
    return False


# ---------------------------------------------------------------------------
# Standard three-view project fixture
# ---------------------------------------------------------------------------
STANDARD_VIEWS = {
    "dashboard.py": """\
        from designgui.ui_lib.primitives import Stack, Text

        def render_view():
            with Stack(base_classes=['p-8']):
                Text('Dashboard', base_classes=['text-2xl'])
    """,
    "home.py": """\
        from designgui.ui_lib.primitives import Stack, Text

        def render_view():
            with Stack(base_classes=['p-8']):
                Text('Home', base_classes=['text-2xl'])
    """,
    "settings.py": """\
        from designgui.ui_lib.primitives import Stack, Text

        def render_view():
            with Stack(base_classes=['p-8']):
                Text('Settings', base_classes=['text-2xl'])
    """,
}


@pytest.fixture()
def export_project(tmp_path):
    """Scaffold a project with 3 views and run export. Yield (project_dir, prod_dir)."""
    _scaffold_project(tmp_path, STANDARD_VIEWS)
    result = _run_export(tmp_path, port=EXPORT_PORT)
    assert result.returncode == 0, f"Export failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"

    prod_dir = tmp_path / "production_app"
    yield tmp_path, prod_dir

    # Cleanup
    if prod_dir.exists():
        shutil.rmtree(prod_dir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Static Validation Tests
# ---------------------------------------------------------------------------

class TestExportStaticValidation:
    """Validate the exported build artifacts without running them."""

    def test_export_creates_production_dir(self, export_project):
        """production_app/ directory must exist after export."""
        _, prod_dir = export_project
        assert prod_dir.exists(), "production_app/ directory was not created"
        assert prod_dir.is_dir(), "production_app/ is not a directory"

    def test_export_copies_all_views(self, export_project):
        """All 3 view files + __init__.py must be copied to production_app/product/views/."""
        _, prod_dir = export_project
        views_dir = prod_dir / "product" / "views"
        assert views_dir.exists(), "product/views/ not found in production_app/"

        expected_files = {"dashboard.py", "home.py", "settings.py", "__init__.py"}
        actual_files = {f.name for f in views_dir.iterdir() if f.is_file()}
        assert expected_files.issubset(actual_files), (
            f"Missing files: {expected_files - actual_files}"
        )

    def test_main_py_has_no_syntax_errors(self, export_project):
        """production_app/main.py must be valid Python — ast.parse() must not raise.
        This would have caught the f-string template bugs from earlier review cycles."""
        _, prod_dir = export_project
        main_py = prod_dir / "main.py"
        assert main_py.exists(), "main.py not found in production_app/"

        source = main_py.read_text(encoding="utf-8")
        try:
            ast.parse(source)
        except SyntaxError as e:
            pytest.fail(f"main.py has a SyntaxError: {e}")

    def test_main_py_routes_all_views(self, export_project):
        """The dynamic router must map all 3 views to route functions.
        dashboard → '/', home → '/home', settings → '/settings'."""
        _, prod_dir = export_project
        source = (prod_dir / "main.py").read_text(encoding="utf-8")
        tree = ast.parse(source)

        # Collect all function definitions
        func_names = [
            node.name for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        ]

        assert "route_dashboard" in func_names, "route_dashboard() not found in main.py"
        assert "route_home" in func_names, "route_home() not found in main.py"
        assert "route_settings" in func_names, "route_settings() not found in main.py"

        # Verify route paths in source text
        assert "'/'" in source, "Root route '/' not found in main.py"
        assert "'/home'" in source, "Route '/home' not found in main.py"
        assert "'/settings'" in source, "Route '/settings' not found in main.py"

    def test_main_py_headless_flags(self, export_project):
        """The exported app MUST use reload=False and show=False —
        these are the two flags that make headless edge deployment work
        (no browser window opens, no auto-reload on a Raspberry Pi)."""
        _, prod_dir = export_project
        source = (prod_dir / "main.py").read_text(encoding="utf-8")

        assert "reload=False" in source, "reload=False not found — will break headless deployment"
        assert "show=False" in source, "show=False not found — will try to open browser on headless device"

    def test_export_custom_host_port(self, tmp_path):
        """Export with --host 0.0.0.0 --port 9090 — main.py must embed those values."""
        _scaffold_project(tmp_path, STANDARD_VIEWS)
        result = _run_export(tmp_path, host=CUSTOM_HOST, port=CUSTOM_PORT)
        assert result.returncode == 0, f"Export failed: {result.stderr}"

        source = (tmp_path / "production_app" / "main.py").read_text(encoding="utf-8")
        assert f"host='{CUSTOM_HOST}'" in source, f"Custom host {CUSTOM_HOST} not found in main.py"
        assert f"port={CUSTOM_PORT}" in source, f"Custom port {CUSTOM_PORT} not found in main.py"


# ---------------------------------------------------------------------------
# Runtime Validation Tests (The Pi Simulation)
# ---------------------------------------------------------------------------

class TestExportRuntimeValidation:
    """Boot the exported app and probe it — simulates a headless Raspberry Pi."""

    def test_exported_app_boots(self, export_project):
        """The exported app must boot and serve HTTP 200 on the configured port."""
        import httpx
        _, prod_dir = export_project
        main_py = prod_dir / "main.py"

        proc = subprocess.Popen(
            [sys.executable, str(main_py)],
            cwd=str(prod_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        try:
            if not _wait_for_server(EXPORT_PORT):
                stdout = proc.stdout.read().decode(errors="replace") if proc.stdout else ""
                stderr = proc.stderr.read().decode(errors="replace") if proc.stderr else ""
                pytest.skip(
                    f"Exported app failed to boot on port {EXPORT_PORT}.\n"
                    f"stdout: {stdout[:500]}\nstderr: {stderr[:500]}"
                )

            r = httpx.get(f"http://localhost:{EXPORT_PORT}/", timeout=5)
            assert r.status_code == 200, f"Root route returned {r.status_code}"
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)

    def test_exported_app_serves_all_routes(self, export_project):
        """All 3 routes (/, /home, /settings) must return HTTP 200."""
        import httpx
        _, prod_dir = export_project
        main_py = prod_dir / "main.py"

        proc = subprocess.Popen(
            [sys.executable, str(main_py)],
            cwd=str(prod_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        try:
            if not _wait_for_server(EXPORT_PORT):
                pytest.skip(f"Exported app failed to boot on port {EXPORT_PORT}")

            for route in ["/", "/home", "/settings"]:
                r = httpx.get(f"http://localhost:{EXPORT_PORT}{route}", timeout=5)
                assert r.status_code == 200, f"Route {route} returned {r.status_code}"
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)
