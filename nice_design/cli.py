import os
import typer
from pathlib import Path

app = typer.Typer(help="Nice Design OS CLI")

@app.command()
def init():
    """Initialize a new Nice Design OS project and inject AI Agent rules."""
    cwd = Path.cwd()
    typer.echo("Initializing Nice Design OS project...")
    
    # 1. Create hidden dir
    commands_dir = cwd / ".designgui" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Create product views dir
    views_dir = cwd / "product" / "views"
    views_dir.mkdir(parents=True, exist_ok=True)
    
    # Create empty __init__.py so it's a module
    (cwd / "product" / "__init__.py").touch(exist_ok=True)
    (views_dir / "__init__.py").touch(exist_ok=True)
    
    # 3. Generate .cursorrules
    cursorrules_content = """# Nice Design OS - Agent Rules
You are an expert Python UI developer. You will build apps using the `nice_design.ui_lib` framework.

## Command Interception
When the user types a slash command, you MUST read the corresponding instruction file BEFORE answering:
- `/product-vision`: Read `.designgui/commands/vision.md`
- `/design-shell`: Read `.designgui/commands/shell.md`
- `/shape-section`: Read `.designgui/commands/section.md`
- `/design-screen`: Read `.designgui/commands/screen.md`

## Strict Guidelines
1. Only output Python code using `import nice_design.ui_lib as ui`.
2. Do not use React, HTML, or standard NiceGUI elements like `ui.button`, `ui.input`, `ui.label`, etc.
3. Save generated UI views in `product/views/`.
"""
    (cwd / ".cursorrules").write_text(cursorrules_content)
    
    # 4. Write placeholder markdown instruction
    section_md_content = """# Component API Cheat Sheet

Use these exact components from `nice_design.ui_lib.primitives` and `nice_design.ui_lib.inputs`.

- `Text(text: str, base_classes: list[str] = None)`: A span wrapper for text.
- `Box(base_classes: list[str] = None)`: A div container.
- `Flex(base_classes: list[str] = None)`: A flex row container.
- `Stack(base_classes: list[str] = None)`: A flex column container.
- `Container(base_classes: list[str] = None)`: A centered max-width container.
- `Button(text: str, on_click: Callable = None, variant: str = 'primary', base_classes: list[str] = None)`: A button. Variants: 'primary', 'ghost', 'outline'.
- `Input(placeholder: str = '', value: str = '', on_change: Callable = None, base_classes: list[str] = None)`: A text input field. Use `.bind_value_to(obj, 'prop_name')` to bind.
- `Divider(base_classes: list[str] = None)`: A horizontal line.

## Tailwind Classes
Inject standard Tailwind classes using the `base_classes` parameter, e.g. `Button('Save', base_classes=['mt-4', 'w-full'])`.
"""
    (commands_dir / "section.md").write_text(section_md_content)
    
    # Create a placeholder view so the server has something to render
    placeholder_view_content = """from nice_design.ui_lib.primitives import Stack, Text
from nice_design.ui_lib.inputs import Button

def render_view():
    with Stack(base_classes=['p-8', 'bg-white', 'rounded-xl', 'shadow-md', 'items-center']):
        Text('Welcome to Nice Design OS', base_classes=['text-3xl', 'font-bold', 'text-gray-900', 'mb-4'])
        Text('Edit this file in product/views/ to see live updates.', base_classes=['text-gray-600', 'mb-6'])
        Button('Click Me', variant='primary', on_click=lambda: print('Button Clicked!', flush=True))
"""
    (views_dir / "dashboard.py").write_text(placeholder_view_content)
    
    typer.echo(typer.style("Nice Design OS project initialized successfully!", fg=typer.colors.GREEN))
    typer.echo("Run `nice-design start` to launch the Live Preview engine.")

@app.command()
def start():
    """Start the Live Preview Engine."""
    typer.echo("Starting Live Preview Engine...")
    import sys
    # Add cwd to path so we can import product.views if needed
    if str(Path.cwd()) not in sys.path:
        sys.path.insert(0, str(Path.cwd()))
        
    from nice_design.server import run_server
    run_server()

if __name__ == "__main__":
    app()
