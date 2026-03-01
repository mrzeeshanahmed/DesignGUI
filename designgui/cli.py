import os
import json
import typer
from pathlib import Path

# Provide a global app description for the Typer help menu
app = typer.Typer(
    help=(
        "Nice Design OS CLI - The Python Design Operating System.\\n\\n"
        "This tool scaffolds a 100% custom Tailwind-driven UI prototyping workflow "
        "and injects intelligent IDE Agent rules so AI tools (Cursor, Windsurf, Copilot, etc.) "
        "can autonomously build your UI screens using the 'Prompt as Code' 5-Loop workflow."
    )
)

def smart_append_instruction(filepath: Path, instruction_text: str):
    """Safely append instruction pointers to IDE rule files without destroying existing rules."""
    if filepath.exists():
        content = filepath.read_text()
        if "DESIGNGUI_INSTRUCTIONS.md" in content:
            # We already injected the rules, do nothing
            return
    else:
        # Create parent directories if they don't exist (e.g., .github/)
        filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Append the pointer instruction
    with open(filepath, "a") as f:
        f.write(instruction_text)

def smart_remove_instruction(filepath: Path):
    """Safely remove DesignGUI Agent Rules from an IDE rule file."""
    if not filepath.exists():
        return
    content = filepath.read_text()
    if "# DesignGUI Agent Rules" in content:
        pointer_text_new = "\n\n# DesignGUI Agent Rules\nYou are operating in a DesignGUI project. You MUST read the .designgui/INSTRUCTIONS.md file before answering prompts or generating code.\n"
        pointer_text_old = "\n\n# DesignGUI Agent Rules\nYou are operating in a DesignGUI project. You MUST read the DESIGNGUI_INSTRUCTIONS.md file in the root directory before answering prompts or generating code.\n"
        
        content = content.replace(pointer_text_new, "")
        content = content.replace(pointer_text_old, "")
        
        if "# DesignGUI Agent Rules" in content:
            start_idx = content.find("\n\n# DesignGUI Agent Rules")
            if start_idx == -1:
                start_idx = content.find("# DesignGUI Agent Rules")
            if start_idx != -1:
                content = content[:start_idx]
                
        if not content.strip():
            filepath.unlink()
        else:
            filepath.write_text(content)

def smart_gitignore_append(cwd: Path):
    gitignore = cwd / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text()
        if ".designgui/" not in content and ".designgui" not in content:
            with open(gitignore, "a") as f:
                f.write("\n.designgui/\n")
    else:
        with open(gitignore, "w") as f:
            f.write(".designgui/\n")

def get_config():
    """Attempt to load the .designgui/config.json with gracefull fallbacks."""
    config_path = Path(".designgui/config.json")
    if config_path.exists():
        try:
            return json.loads(config_path.read_text())
        except Exception:
            pass
    # Default fallbacks
    return {
        "designgui_version": "1.0.0",
        "environment": "Unknown",
        "daemon_port": 8080,
        "paths": {
            "instructions": "DESIGNGUI_INSTRUCTIONS.md",
            "views": "product/views",
            "models": "product/models.py"
        }
    }

@app.command()
def init():
    """Initialize a new Nice Design OS project with guided setup and inject AI Agent rules."""
    cwd = Path.cwd()
    typer.echo(typer.style("Initializing Nice Design OS project...", fg=typer.colors.CYAN))
    
    # --- Interactive Guided Setup ---
    env_choices = """Which primary AI environment are you using?
[1] Cursor
[2] Windsurf
[3] Copilot/JetBrains
[4] Generic/Cloud IDE
[5] Autonomous Agent
Enter your choice:"""
    environment_input = typer.prompt(env_choices, default="1")
    
    env_map = {"1": "Cursor", "2": "Windsurf", "3": "Copilot/JetBrains", "4": "Generic/Cloud IDE", "5": "Autonomous Agent"}
    environment = env_map.get(environment_input, "Unknown")
    
    port_input = typer.prompt("What port should the live preview daemon run on?", default="8080")
    try:
        daemon_port = int(port_input)
    except ValueError:
        daemon_port = 8080
        
    config = {
        "designgui_version": "1.0.0",
        "environment": environment,
        "daemon_port": daemon_port,
        "paths": {
            "instructions": "DESIGNGUI_INSTRUCTIONS.md",
            "views": "product/views",
            "models": "product/models.py"
        }
    }
    
    # 1. Create hidden dir & save config
    designgui_dir = cwd / ".designgui"
    designgui_dir.mkdir(parents=True, exist_ok=True)
    commands_dir = designgui_dir / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)
    
    (designgui_dir / "config.json").write_text(json.dumps(config, indent=2))
    
    # 2. Create product views dir
    product_dir = designgui_dir / "product"
    views_dir = product_dir / "views"
    views_dir.mkdir(parents=True, exist_ok=True)
    
    (product_dir / "__init__.py").touch(exist_ok=True)
    (views_dir / "__init__.py").touch(exist_ok=True)
    
    # 3. Generate universal instruction file
    universal_instruction_text = """# Nice Design OS - Comprehensive Agent Instructions

You are operating in a Nice Design OS project. You must strictly follow these rules:

1. You are an expert Python UI developer using the `designgui.ui_lib` framework.
2. DO NOT use React, Vue, HTML, or standard NiceGUI elements like `ui.button` or `ui.input`.
3. ONLY use primitives from `designgui.ui_lib.primitives` (Container, Stack, Flex, Box, Text, Divider) and `designgui.ui_lib.inputs` (Button, Input).

## The 5-Loop Flow
When given a feature prompt, execute these steps:
- **Phase 1 (Vision)**: Outline concept in `.designgui/product/specs/vision.md` and Pydantic schema in `.designgui/product/models.py`.
- **Phase 2 (Shell)**: Build global layout wrapper in `.designgui/product/shell.py`.
- **Phase 3 (Section)**: Generate mock data and a UI view in `.designgui/product/views/{name}.py` using the primitive components.
- **Phase 4 (Screen)**: Wire Python callbacks (`on_click=...`) and inject state.
"""
    (designgui_dir / "INSTRUCTIONS.md").write_text(universal_instruction_text)
    
    # 4. Smart Append IDE Rules
    pointer_text = "\\n\\n# DesignGUI Agent Rules\\nYou are operating in a DesignGUI project. You MUST read the .designgui/INSTRUCTIONS.md file before answering prompts or generating code.\\n"
    
    rule_file_map = {
        "1": ".cursorrules",
        "2": ".windsurfrules",
        "3": ".github/copilot-instructions.md",
        "4": ".prompts.md"
    }
    
    selected_file = rule_file_map.get(environment_input)
    if selected_file:
        smart_append_instruction(cwd / selected_file, pointer_text)
        
    smart_gitignore_append(cwd)
    
    # 5. Write specific 5-loop command files for agents that support specific prompt interception
    vision_md = """# Product Vision & Models (/product-vision)
You are outlining the app concept and data structures in `.designgui/product/specs/vision.md` and `.designgui/product/models.py`."""
    shell_md = """# Design Shell (/design-shell)
You are building the layout in `.designgui/product/shell.py` using `Container, Stack, Flex, Box`."""
    section_md = """# Component API Cheat Sheet (/shape-section)
Use ONLY components from `designgui.ui_lib`. Scaffold a base feature screen in `.designgui/product/views/_.py`."""
    screen_md = """# Design Screen Refinement (/design-screen)
You are refining a view. Wire up Python callbacks (`on_click=lambda:...`) and manage state."""
    
    (commands_dir / "vision.md").write_text(vision_md)
    (commands_dir / "shell.md").write_text(shell_md)
    (commands_dir / "section.md").write_text(section_md)
    (commands_dir / "screen.md").write_text(screen_md)
    
    # Create placeholder
    placeholder_view_content = """from designgui.ui_lib.primitives import Stack, Text
from designgui.ui_lib.inputs import Button

def render_view():
    with Stack(base_classes=['p-8', 'bg-white', 'rounded-xl', 'shadow-md', 'items-center']):
        Text('Welcome to Nice Design OS', base_classes=['text-3xl', 'font-bold', 'text-gray-900', 'mb-4'])
        Text('Edit this file in .designgui/product/views/ to see live updates.', base_classes=['text-gray-600', 'mb-6'])
        Button('Click Me', variant='primary', on_click=lambda: print('Button Clicked!', flush=True))
"""
    (views_dir / "dashboard.py").write_text(placeholder_view_content)
    
    typer.echo(typer.style("Nice Design OS project initialized successfully!", fg=typer.colors.GREEN))
    typer.echo(f"Run `designgui start` or `designgui daemon` to launch on port {daemon_port}.")

@app.command()
def export(host: str = typer.Option("0.0.0.0", help="Host address for production app"), 
           port: int = typer.Option(8080, help="Port for production app")):
    """Export the prototype to a production-ready standalone application optimized for edge deployment (e.g. Raspberry Pi)."""
    import shutil
    
    cwd = Path.cwd()
    config = get_config()
    views_path = config["paths"]["views"]
    
    product_dir = cwd / Path(views_path).parent
    prod_app_dir = cwd / "production_app"
    
    if not product_dir.exists():
        typer.echo(typer.style(f"Error: {product_dir.name} directory not found. Have you initialized?", fg=typer.colors.RED))
        raise typer.Exit(1)
        
    typer.echo(f"Exporting product to production_app/ ...")
    
    if prod_app_dir.exists():
        shutil.rmtree(prod_app_dir)
    shutil.copytree(product_dir, prod_app_dir / "product")
    
    main_py_content = f"""from nicegui import ui

# Dynamically import the AI generated view.
from product.views.dashboard import render_view

@ui.page('/')
def index():
    render_view()

if __name__ in {{"__main__", "__mp_main__"}}:
    # Reload and show are FALSE for production edge/headless optimization
    ui.run(title='Production App', host='{host}', port={port}, reload=False, show=False)
"""
    (prod_app_dir / "main.py").write_text(main_py_content)
    
    typer.echo(typer.style("Export complete!", fg=typer.colors.GREEN))
    typer.echo(f"Run `cd production_app` and `python main.py` to start the headless server on {host}:{port}.")

@app.command()
def start():
    """Start the Live Preview Engine in the foreground equipped with hot-reloading file selection."""
    config = get_config()
    port = config.get("daemon_port", 8080)
    views_path = config.get("paths", {}).get("views", "product/views")
    typer.echo(f"Starting Live Preview Engine on port {port}...")
    import sys
    if str(Path.cwd()) not in sys.path:
        sys.path.insert(0, str(Path.cwd()))
        
    from designgui.server import run_server
    run_server(port=port, views_path=views_path)

@app.command()
def daemon(port: int = typer.Option(None, help="Port to run the daemon on (overrides config.json)")):
    """Run the live-preview engine as a background watcher for autonomous agents."""
    config = get_config()
    target_port = port if port else config.get("daemon_port", 8080)
    views_path = config.get("paths", {}).get("views", "product/views")
    typer.echo(f"Initializing Autonomous Daemon on port {target_port}...")
    typer.echo(f"Agents can write .py files to {views_path}/ to dynamically generate interactive dashboards.")
    
    import sys
    if str(Path.cwd()) not in sys.path:
        sys.path.insert(0, str(Path.cwd()))
        
    from designgui.server import run_server
    run_server(port=target_port, views_path=views_path)

@app.command("remove")
def remove():
    """Safely removes DesignGUI from the project."""
    import shutil
    cwd = Path.cwd()
    typer.echo("Removing DesignGUI from the project...")
    
    rule_files = [".cursorrules", ".windsurfrules", ".clinerules", ".github/copilot-instructions.md", ".prompts.md"]
    for rf in rule_files:
        smart_remove_instruction(cwd / rf)
        
    designgui_dir = cwd / ".designgui"
    if designgui_dir.exists():
        shutil.rmtree(designgui_dir, ignore_errors=True)
        
    legacy_instructions = cwd / "DESIGNGUI_INSTRUCTIONS.md"
    if legacy_instructions.exists():
        legacy_instructions.unlink()
        
    typer.echo(typer.style("DesignGUI has been safely removed from this project.", fg=typer.colors.GREEN))

if __name__ == "__main__":
    app()
