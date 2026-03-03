"""
Live Preview Engine
"""
import importlib.util
import sys
import inspect
import traceback
import json
from pathlib import Path
from nicegui import ui
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import time
import secrets as _secrets
from nicegui import app

# Global singleton to prevent thread explosion per page load
_observer_instance = None

def get_or_create_observer(views_dir_path):
    global _observer_instance
    if _observer_instance is None and Path(views_dir_path).exists():
        
        class GlobalHotReloadHandler(FileSystemEventHandler):
            def on_modified(self, event):
                if event.is_directory or not event.src_path.endswith('.py'):
                    return
                # Tell all connected clients via app storage that a refresh occurred
                app.storage.general['last_modified'] = time.time()
                
            def on_created(self, event):
                self.on_modified(event)

            def on_deleted(self, event):
                self.on_modified(event)

        _observer_instance = Observer()
        # Schedule the singleton handler
        _observer_instance.schedule(GlobalHotReloadHandler(), views_dir_path, recursive=False)
        _observer_instance.start()
        
    return _observer_instance


def _get_storage_secret() -> str:
    """Return a persistent storage secret from config.json, generating one if absent."""
    config_path = Path(".designgui/config.json")
    try:
        config = json.loads(config_path.read_text())
        if "storage_secret" in config:
            return config["storage_secret"]
        # Generate, persist, and return a new random secret
        new_secret = _secrets.token_hex(32)
        config["storage_secret"] = new_secret
        config_path.write_text(json.dumps(config, indent=2))
        return new_secret
    except Exception:
        # Fallback: ephemeral secret if config is unreadable (non-persistent)
        return _secrets.token_hex(32)


def preview_environment(views_path: str = ".designgui/product/views"):
    try:
        config = json.loads(Path(".designgui/config.json").read_text())
        locale = config.get("locale", "en-US")
        font_family = config.get("font_family", "Inter, sans-serif")
    except Exception:
        locale = "en-US"
        font_family = "Inter, sans-serif"
        
    # Global CSS injection for CJK and standard typographies
    ui.add_head_html(f'<style>body {{ font-family: {font_family}; }}</style>')
    ui.add_head_html('<script src="https://cdn.tailwindcss.com"></script>')
    
    # RTL Parsing natively skipping Hebrew explicitly as requested
    rtl_locales = ["ar", "fa", "ur"]
    if any(locale.startswith(r) for r in rtl_locales):
        ui.query('html').props('dir="rtl"')
        ui.query('body').classes('p-0 m-0 bg-gray-50 text-right')
    else:
        ui.query('html').props('dir="ltr"')
        ui.query('body').classes('p-0 m-0 bg-gray-50 text-left')
    
    with ui.column().classes('w-full h-screen p-0 m-0'):
        # Header / Controls
        with ui.row().classes('w-full bg-white border-b border-gray-200 p-4 flex justify-between items-center shadow-sm z-10'):
            ui.label('Nice Design OS - Live Preview').classes('text-lg font-bold text-gray-800')
            
            with ui.row().classes('gap-2 items-center'):
                ui.label('View Source:').classes('text-sm text-gray-500 font-medium')
                
                # The dropdown auto re-renders on change
                view_select = ui.select(options=[], value=None, on_change=lambda e: render_generated_view(e.value)).classes('w-48')
                
                # Watchdog replaces manual Refresh buttons
                ui.label('(Auto-Saving via Watchdog)').classes('text-xs text-green-600 font-bold ml-2')

        # Empty container waiting for AI code
        preview_pane = ui.column().classes('w-full h-full p-8 overflow-y-auto')
        
        def update_file_list():
            views_dir = Path.cwd() / Path(views_path)
            if views_dir.exists():
                py_files = [f.name for f in views_dir.glob("*.py") if f.name != "__init__.py"]
                view_select.options = py_files
                view_select.update()
                if py_files and view_select.value not in py_files:
                    view_select.set_value(py_files[0])
                    # set_value triggers on_change, which calls render_generated_view
                    
        def render_generated_view(filename):
            if not filename:
                return
            
            module_path = Path.cwd() / Path(views_path) / filename
            if not module_path.exists():
                ui.notify(f"View file {filename} not found.")
                return
                
            preview_pane.clear() # Clear old UI
            
            try:
                # Dynamically load the python file
                module_name = f"dynamic_view_{filename[:-3]}"
                
                # Force strictly pure reload by purging stale references
                if module_name in sys.modules:
                    del sys.modules[module_name]
                
                # Make sure views_path is in sys.path for relative imports within the views
                views_dir_str = str(Path.cwd() / Path(views_path))
                if views_dir_str not in sys.path:
                    sys.path.insert(0, views_dir_str)
                    
                spec = importlib.util.spec_from_file_location(module_name, str(module_path))
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                
                # Execute the default function or the view function
                target_func = None
                if hasattr(module, 'render_view'):
                    target_func = getattr(module, 'render_view')
                else:
                    for name, obj in inspect.getmembers(module, inspect.isfunction):
                        if obj.__module__ == module_name:
                            target_func = obj
                            break
                
                if target_func:
                    with preview_pane:
                        target_func()
                    ui.notify(f"Reloaded {filename} successfully.", type="positive")
                else:
                    with preview_pane:
                        ui.label(f"Could not find a render function in {filename}. Please define 'render_view()'.").classes('text-red-500 font-bold p-4 bg-red-50 rounded border border-red-200 w-full')

            except Exception as e:
                error_trace = traceback.format_exc()
                with preview_pane:
                    ui.label("Error Rendering View:").classes('text-red-600 font-bold text-lg')
                    ui.code(error_trace).classes('w-full mt-2 whitespace-pre-wrap')
                ui.notify(f"Error loading {filename}: {str(e)}", type="negative")

        # Initial population
        update_file_list()
        
        # Track the last known modification timestamp locally per-client connection
        # Initialize storage if it doesn't exist
        if 'last_modified' not in app.storage.general:
            app.storage.general['last_modified'] = 0.0
            
        client_last_seen = app.storage.general['last_modified']
        
        def check_for_updates():
            nonlocal client_last_seen
            current_mod = app.storage.general.get('last_modified', 0.0)
            if current_mod > client_last_seen:
                client_last_seen = current_mod
                update_file_list()
                if view_select.value:
                    render_generated_view(view_select.value)
                    
        # Check every 500ms for updates within the correct client context boundary
        ui.timer(0.5, check_for_updates)

def run_server(port: int = 8080, views_path: str = ".designgui/product/views"):
    
    # Initialize Watchdog Singleton Thread once ahead of clients
    views_dir_path = str(Path.cwd() / Path(views_path))
    get_or_create_observer(views_dir_path)
    
    @ui.page('/')
    def index():
        preview_environment(views_path=views_path)
        
    ui.run(title='Nice Design OS - Live Preview', port=port, reload=False, storage_secret=_get_storage_secret())
