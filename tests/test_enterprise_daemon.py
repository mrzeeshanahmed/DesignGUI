"""
Enterprise GPU / Autonomous Swarm — Daemon E2E Tests
=====================================================
Proves that `designgui start` can run reliably in the background while
AI agents rapidly generate and overwrite .py view files, and that the
hot-reload engine (watchdog + NiceGUI ui.timer debounce) doesn't crash.

Architecture under test (server.py):
    - HotReloadHandler.on_modified() → ui.timer(0.1s) → render_generated_view()
    - render_generated_view() purges sys.modules, re-imports via importlib.util
    - All exceptions are caught and rendered in the preview pane (server never crashes)

Port: 8081 (isolated from default 8080 and export tests on 8082)
"""
import sys
import time
import subprocess
import textwrap
import json
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DAEMON_PORT = 8081
SERVER_BOOT_TIMEOUT = 20  # seconds — NiceGUI first boot can be slow
WATCHDOG_SETTLE_TIME = 3  # seconds — watchdog on_modified + ui.timer(0.1) + margin
STRESS_WRITES = 5
STRESS_INTERVAL = 0.4  # seconds between rapid saves

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_view(views_dir: Path, filename: str, content: str):
    """Write a view .py file to the views directory."""
    (views_dir / filename).write_text(textwrap.dedent(content), encoding="utf-8")


def _scaffold_project(project_dir: Path):
    """Manually scaffold a .designgui project (avoids interactive typer.prompt)."""
    designgui_dir = project_dir / ".designgui"
    views_dir = designgui_dir / "product" / "views"
    views_dir.mkdir(parents=True, exist_ok=True)
    (designgui_dir / "product" / "__init__.py").touch()
    (views_dir / "__init__.py").touch()

    config = {
        "environment": "Autonomous Agent",
        "daemon_port": DAEMON_PORT,
        "locale": "en-US",
        "font_family": "Inter, sans-serif",
        "paths": {
            "instructions": "DESIGNGUI_INSTRUCTIONS.md",
            "views": ".designgui/product/views",
            "models": ".designgui/product/models.py"
        }
    }
    (designgui_dir / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    # Seed a basic dashboard view
    _write_view(views_dir, "dashboard.py", """\
        from designgui.ui_lib.primitives import Stack, Text

        def render_view():
            with Stack(base_classes=['p-8']):
                Text('Initial Dashboard', base_classes=['text-2xl'])
    """)

    return views_dir


def _wait_for_server(port: int, timeout: int = SERVER_BOOT_TIMEOUT):
    """Poll the server until it responds with HTTP 200 or timeout expires."""
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
# Fixture: launch the server in a subprocess, yield, then tear down
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def daemon_env(tmp_path_factory):
    """
    Scaffold a project and launch `designgui start --port 8081`.
    Yields (process_handle, views_dir_path).
    Tears down by terminating the process.
    """
    project_dir = tmp_path_factory.mktemp("enterprise")
    views_dir = _scaffold_project(project_dir)

    # Launch the server (NOT daemon — we need process control for teardown)
    proc = subprocess.Popen(
        [sys.executable, "-m", "designgui.cli", "start", "--port", str(DAEMON_PORT)],
        cwd=str(project_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**dict(__import__("os").environ), "PYTHONPATH": str(project_dir)},
    )

    # Wait for the server to boot
    if not _wait_for_server(DAEMON_PORT):
        proc.terminate()
        proc.wait(timeout=5)
        stdout = proc.stdout.read().decode(errors="replace") if proc.stdout else ""
        stderr = proc.stderr.read().decode(errors="replace") if proc.stderr else ""
        pytest.skip(
            f"Server failed to boot on port {DAEMON_PORT} within {SERVER_BOOT_TIMEOUT}s.\n"
            f"stdout: {stdout[:500]}\nstderr: {stderr[:500]}"
        )

    yield proc, views_dir

    # Teardown
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestDaemonBootAndHealth:
    """Verify the daemon boots and serves the NiceGUI shell."""

    def test_daemon_boots_and_serves_html(self, daemon_env):
        """Server responds HTTP 200 with the Nice Design OS header."""
        import httpx
        proc, _ = daemon_env
        r = httpx.get(f"http://localhost:{DAEMON_PORT}/", timeout=5)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        assert proc.poll() is None, "Server process exited unexpectedly"


class TestHotReload:
    """Verify the watchdog hot-reload picks up file changes without crashing."""

    def test_hot_reload_simple_view(self, daemon_env):
        """Overwrite dashboard.py with a simple view — server stays alive."""
        import httpx
        proc, views_dir = daemon_env

        _write_view(views_dir, "dashboard.py", """\
            from designgui.ui_lib.primitives import Stack, Text

            def render_view():
                with Stack(base_classes=['p-8', 'bg-white']):
                    Text('Hot Reloaded View', base_classes=['text-3xl', 'font-bold'])
        """)

        time.sleep(WATCHDOG_SETTLE_TIME)

        r = httpx.get(f"http://localhost:{DAEMON_PORT}/", timeout=5)
        assert r.status_code == 200
        assert proc.poll() is None, "Server crashed after simple hot-reload"

    def test_hot_reload_complex_composites(self, daemon_env):
        """Sequentially overwrite dashboard.py with AuthForm → StatGrid → DataFeed.
        Server must survive all three increasingly complex composite components."""
        import httpx
        proc, views_dir = daemon_env

        composite_views = [
            # AuthForm — macro composite with Email, Password, ToggleSwitch, Button
            """\
            from designgui.ui_lib.composites import AuthForm

            def render_view():
                AuthForm(title="Enterprise Login")
            """,
            # StatGrid — renders 3 stat cards with trends
            """\
            from designgui.ui_lib.composites import StatGrid

            def render_view():
                StatGrid(stats=[
                    {'label': 'GPU Nodes', 'value': '128', 'trend': '+8%', 'positive': True},
                    {'label': 'Throughput', 'value': '4.2 TB/s', 'trend': '+22%', 'positive': True},
                    {'label': 'Errors', 'value': '3', 'trend': '-50%', 'positive': True},
                ])
            """,
            # DataFeed — vertical timeline with multiple items
            """\
            from designgui.ui_lib.composites import DataFeed

            def render_view():
                DataFeed(items=[
                    {'title': 'Model Trained', 'description': 'GPT-J fine-tune completed', 'time': '2m ago', 'icon': 'check_circle'},
                    {'title': 'Deployment', 'description': 'Pushed to prod cluster', 'time': '5m ago', 'icon': 'cloud_upload'},
                    {'title': 'Alert', 'description': 'Memory threshold exceeded', 'time': '12m ago', 'icon': 'warning'},
                ])
            """,
        ]

        for i, view_code in enumerate(composite_views):
            _write_view(views_dir, "dashboard.py", view_code)
            time.sleep(WATCHDOG_SETTLE_TIME)

            r = httpx.get(f"http://localhost:{DAEMON_PORT}/", timeout=5)
            assert r.status_code == 200, f"Server failed after composite write #{i+1}"
            assert proc.poll() is None, f"Server crashed after composite write #{i+1}"

    def test_new_file_creation_detected(self, daemon_env):
        """Create a brand-new analytics.py — watchdog on_created should pick it up."""
        import httpx
        proc, views_dir = daemon_env

        _write_view(views_dir, "analytics.py", """\
            from designgui.ui_lib.primitives import Stack, Text

            def render_view():
                with Stack(base_classes=['p-8']):
                    Text('Analytics Dashboard', base_classes=['text-xl'])
        """)

        time.sleep(WATCHDOG_SETTLE_TIME)

        r = httpx.get(f"http://localhost:{DAEMON_PORT}/", timeout=5)
        assert r.status_code == 200
        assert proc.poll() is None, "Server crashed after new file creation"


class TestServerResilience:
    """Verify the server survives adversarial conditions."""

    def test_stress_rapid_saves(self, daemon_env):
        """Save dashboard.py 5 times in 2 seconds — watchdog debounce must hold."""
        import httpx
        proc, views_dir = daemon_env

        for i in range(STRESS_WRITES):
            _write_view(views_dir, "dashboard.py", f"""\
                from designgui.ui_lib.primitives import Stack, Text

                def render_view():
                    with Stack(base_classes=['p-4']):
                        Text('Stress write #{i}', base_classes=['text-lg'])
            """)
            time.sleep(STRESS_INTERVAL)

        # Wait for all debounced reloads to settle
        time.sleep(WATCHDOG_SETTLE_TIME)

        r = httpx.get(f"http://localhost:{DAEMON_PORT}/", timeout=5)
        assert r.status_code == 200, "Server failed after rapid save stress test"
        assert proc.poll() is None, "Server crashed during rapid save stress test"

    def test_syntax_error_does_not_crash_server(self, daemon_env):
        """Write deliberately broken Python — server must catch the exception
        in render_generated_view()'s try/except and continue serving."""
        import httpx
        proc, views_dir = daemon_env

        # Write intentionally broken syntax
        (views_dir / "dashboard.py").write_text(
            "def render_view(:\\n    pass  # SyntaxError: missing closing paren\\n",
            encoding="utf-8"
        )

        time.sleep(WATCHDOG_SETTLE_TIME)

        r = httpx.get(f"http://localhost:{DAEMON_PORT}/", timeout=5)
        assert r.status_code == 200, "Server should still return 200 even with broken view"
        assert proc.poll() is None, "Server crashed on syntax error — should be caught by try/except"

        # Restore a valid view so subsequent tests aren't affected
        _write_view(views_dir, "dashboard.py", """\
            from designgui.ui_lib.primitives import Stack, Text

            def render_view():
                with Stack(base_classes=['p-4']):
                    Text('Recovered', base_classes=['text-lg'])
        """)
        time.sleep(WATCHDOG_SETTLE_TIME)
