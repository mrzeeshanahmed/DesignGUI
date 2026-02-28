"""
Live Preview Engine
"""
import importlib.util
import sys
from pathlib import Path
from nicegui import ui

def preview_environment():
    ui.add_head_html('<script src="https://cdn.tailwindcss.com"></script>')
    ui.query('body').classes('p-0 m-0 bg-gray-50')
    
    with ui.column().classes('w-full h-screen p-0 m-0'):
        # Header / Controls
        with ui.row().classes('w-full bg-white border-b border-gray-200 p-4 flex justify-between items-center shadow-sm z-10'):
            ui.label('Nice Design OS - Live Preview').classes('text-lg font-bold text-gray-800')
            
            with ui.row().classes('gap-2 items-center'):
                ui.label('View Source:').classes('text-sm text-gray-500 font-medium')
                
                # The dropdown auto re-renders on change
                view_select = ui.select(options=[], value=None, on_change=lambda e: render_generated_view(e.value)).classes('w-48')
                
                def trigger_reload():
                    if view_select.value:
                        render_generated_view(view_select.value)
                ui.button('Refresh', on_click=trigger_reload).props('outline color=primary size=sm')

        # Empty container waiting for AI code
        preview_pane = ui.column().classes('w-full h-full p-8 overflow-y-auto')
        
        def update_file_list():
            views_dir = Path.cwd() / "product" / "views"
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
            
            module_path = Path.cwd() / "product" / "views" / filename
            if not module_path.exists():
                ui.notify(f"View file {filename} not found.")
                return
                
            preview_pane.clear() # Clear old UI
            
            try:
                # Dynamically load the python file
                module_name = f"dynamic_view_{filename[:-3]}"
                
                # Make sure product/views is in sys.path for relative imports within the views
                views_dir_str = str(Path.cwd() / "product" / "views")
                if views_dir_str not in sys.path:
                    sys.path.insert(0, views_dir_str)
                    
                spec = importlib.util.spec_from_file_location(module_name, str(module_path))
                module = importlib.util.module_from_spec(spec)
                # Overwrite module in sys.modules to ensure reload
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                
                # Execute the default function or the view function
                target_func = None
                if hasattr(module, 'render_view'):
                    target_func = getattr(module, 'render_view')
                else:
                    import inspect
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
                import traceback
                error_trace = traceback.format_exc()
                with preview_pane:
                    ui.label("Error Rendering View:").classes('text-red-600 font-bold text-lg')
                    ui.code(error_trace).classes('w-full mt-2 whitespace-pre-wrap')
                ui.notify(f"Error loading {filename}: {str(e)}", type="negative")

        # Initial population
        update_file_list()

def run_server():
    @ui.page('/')
    def index():
        preview_environment()
        
    ui.run(title='Nice Design OS - Live Preview', port=8080, reload=False)
