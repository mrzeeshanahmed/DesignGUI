import json
import typer
import sys
import shutil
import importlib.metadata
import subprocess
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

def version_callback(value: bool):
    if value:
        try:
            version = importlib.metadata.version("designgui")
        except Exception:
            version = "unknown (not installed via pip)"
        typer.echo(f"DesignGUI Version: {version}")
        raise typer.Exit()

@app.callback()
def main(
    version: bool = typer.Option(None, "--version", "-v", callback=version_callback, is_eager=True, help="Show the application's version and exit.")
):
    pass

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

def get_locale_strings():
    """Load CLI localized strings."""
    locale_file = Path(__file__).parent / "locale" / "en.json"
    if locale_file.exists():
        try:
            return json.loads(locale_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    # Basic fallbacks if loading fails
    return {
        "cli_init_start": "Initializing Nice Design OS project...",
        "cli_init_success": "Nice Design OS project initialized successfully!",
        "cli_env_prompt": "Which primary AI environment are you using?",
        "cli_port_prompt": "What port should the live preview daemon run on?",
        "cli_export_error": "Error: {dir} directory not found. Have you initialized?",
        "cli_export_start": "Exporting product to production_app/ ...",
        "cli_export_success": "Export complete!",
        "cli_start_engine": "Starting Live Preview Engine on port {port}...",
        "cli_daemon_init": "Initializing Autonomous Daemon on port {port}...",
        "cli_remove_start": "Removing DesignGUI from the project...",
        "cli_remove_success": "DesignGUI has been safely removed from this project.",
        "cli_security_engine_warning": "⚠️  WARNING: DESIGNGUI EXECUTES PYTHON PAYLOADS DYNAMICALLY ⚠️\nThe Live Preview engine will automatically execute code dropped into the `.designgui/product/views/` directory. Do not place untrusted third-party scripts here.\n",
        "cli_security_daemon_warning": "⚠️  WARNING: DESIGNGUI EXECUTES PYTHON PAYLOADS DYNAMICALLY ⚠️\nThe Daemon engine will automatically execute code dropped into the `.designgui/product/views/` directory. Do not place untrusted third-party scripts here.\n"
    }

def smart_gitignore_append(cwd: Path):
    gitignore = cwd / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text(encoding="utf-8")
        if ".designgui/" not in content and ".designgui" not in content:
            with open(gitignore, "a", encoding="utf-8") as f:
                f.write("\n.designgui/\n")
    else:
        with open(gitignore, "w", encoding="utf-8") as f:
            f.write(".designgui/\n")

def get_config():
    """Attempt to load the .designgui/config.json with graceful fallbacks."""
    config_path = Path(".designgui/config.json")
    if config_path.exists():
        try:
            return json.loads(config_path.read_text())
        except Exception:
            pass
    # Default fallbacks
    try:
        fallback_version = importlib.metadata.version('designgui')
    except Exception:
        fallback_version = 'unknown'
        
    return {
        "designgui_version": fallback_version,
        "environment": "Unknown",
        "daemon_port": 8080,
        "paths": {
            "instructions": "DESIGNGUI_INSTRUCTIONS.md",
            "views": ".designgui/product/views",
            "models": ".designgui/product/models.py"
        }
    }

@app.command()
def init() -> None:
    """Initialize a new Nice Design OS project with guided setup and inject AI Agent rules."""
    cwd = Path.cwd()
    strings = get_locale_strings()
    typer.echo(typer.style(strings["cli_init_start"], fg=typer.colors.CYAN))
    
    # --- Interactive Guided Setup ---
    env_choices = f"""{strings["cli_env_prompt"]}
[1] Cursor
[2] Windsurf
[3] Copilot/JetBrains
[4] Generic/Cloud IDE
[5] Autonomous Agent
[6] Tongyi Lingma
[7] Baidu Comate
[8] CodeGeeX
Enter your choice:"""
    environment_input = typer.prompt(env_choices, default="1")
    
    env_map = {
        "1": "Cursor", "2": "Windsurf", "3": "Copilot/JetBrains",
        "4": "Generic/Cloud IDE", "5": "Autonomous Agent",
        "6": "Tongyi Lingma", "7": "Baidu Comate", "8": "CodeGeeX"
    }
    environment = env_map.get(environment_input, "Unknown")
    
    port_input = typer.prompt(strings["cli_port_prompt"], default="8080")
    try:
        daemon_port = int(port_input)
    except ValueError:
        daemon_port = 8080
        
    config = {
        "environment": environment,
        "daemon_port": daemon_port,
        "locale": "en-US",
        "font_family": "Inter, sans-serif",
        "paths": {
            "instructions": "DESIGNGUI_INSTRUCTIONS.md",
            "views": ".designgui/product/views",
            "models": ".designgui/product/models.py"
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

To build the interface:
1. Wrap the entire view in a `Container` from `designgui.ui_lib.primitives`.
2. Do not use standard NiceGUI `.classes()` chained directly onto NiceGUI elements unless strictly necessary. Instead, use the `base_classes` array constructor argument.
3. ONLY use components from `designgui.ui_lib`. Available Primitives: (Container, Stack, Flex, Box, Text, Divider). Inputs: (Button, Input, ToggleSwitch, Slider, RadioGroup, Select, Checkbox, Textarea). Display: (Image, Icon, Avatar, DropdownMenu, Table, Tabs, Accordion, Card, Badge, Modal). Layout: (Sidebar, Header, Sheet). Composites: (AuthForm, StatGrid, EmptyState, Stepper, TopNav, DataFeed). Feedback: (Toast, Skeleton, Spinner).
4. Use Tailwind CSS exclusively. Do not write custom CSS unless explicitly requested.

When building state logic:
- **Phase 1 (Vision)**: Outline concept in `.designgui/product/specs/vision.md` and Pydantic schema in `.designgui/product/models.py`.
- **Phase 2 (Shell)**: Build global layout wrapper in `.designgui/product/shell.py`.
- **Phase 3 (Section)**: Generate mock data and a UI view in `.designgui/product/views/{name}.py` using the primitive components.
- **Phase 4 (Screen)**: Wire Python callbacks (`on_click=...`) and inject state.
"""
    (designgui_dir / "INSTRUCTIONS.md").write_text(universal_instruction_text)
    
    # 4. Smart Append IDE Rules
    pointer_text = "\n\n# DesignGUI Agent Rules\nYou are operating in a DesignGUI project. You MUST read the .designgui/INSTRUCTIONS.md file before answering prompts or generating code.\n"
    
    rule_file_map = {
        "Cursor": ".cursorrules",
        "Windsurf": ".windsurfrules",
        "Copilot/JetBrains": ".github/copilot-instructions.md",
        "Tongyi Lingma": ".lingmarules",
        "Baidu Comate": ".comate_instructions",
        "CodeGeeX": ".codegeex_rules",
        "Generic/Cloud IDE": ".prompts.md",
        "Autonomous Agent": ".clinerules"
    }
    
    selected_file = rule_file_map.get(environment)
    if selected_file:
        smart_append_instruction(cwd / selected_file, pointer_text)
        
    smart_gitignore_append(cwd)
    
    # 5. Write specific 5-loop command files for agents that support specific prompt interception
    vision_md = """# Product Vision & Models (/product-vision)
You are outlining the app concept and data structures in `.designgui/product/specs/vision.md` and `.designgui/product/models.py`."""
    shell_md = """# Design Shell (/design-shell)
You are building the layout in `.designgui/product/shell.py` using `Container, Stack, Flex, Box`."""
    section_md = """# Component API Cheat Sheet (/shape-section)
Use ONLY components from `designgui.ui_lib`. Scaffold a base feature screen in `.designgui/product/views/_.py`.
Available Primitives: (Container, Stack, Flex, Box, Text, Divider).
Inputs: (Button, Input, ToggleSwitch, Slider, RadioGroup, Select, Checkbox, Textarea).
Display: (Image, Icon, Avatar, DropdownMenu, Table, Tabs, Accordion, Card, Badge).
Layout: (Sidebar, Header, Sheet, Modal).
Composites: (AuthForm, StatGrid, EmptyState, Stepper, TopNav, DataFeed).
Feedback: (Toast, Skeleton, Spinner)."""
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
    
    typer.echo(typer.style(strings["cli_init_success"], fg=typer.colors.GREEN))
    typer.echo(f"Run `designgui start` or `designgui daemon` to launch on port {daemon_port}.")

@app.command()
def export(host: str = typer.Option("0.0.0.0", help="Host address for production app"), 
           port: int = typer.Option(8080, help="Port for production app")) -> None:
    """Export the prototype to a production-ready standalone application optimized for edge deployment (e.g. Raspberry Pi)."""
    cwd = Path.cwd()
    config = get_config()
    views_path = config["paths"]["views"]
    
    views_dir = cwd / Path(views_path)
    product_dir = views_dir.parent
    prod_app_dir = cwd / "production_app"
    
    strings = get_locale_strings()
    
    if not product_dir.exists():
        err_msg = strings["cli_export_error"].format(dir=product_dir.name)
        typer.echo(typer.style(err_msg, fg=typer.colors.RED))
        raise typer.Exit(1)
        
    typer.echo(strings["cli_export_start"])
    
    if prod_app_dir.exists():
        shutil.rmtree(prod_app_dir)
    shutil.copytree(product_dir, prod_app_dir / "product")
    
    # Dynamically build router for all views
    imports = []
    routes = []
    
    py_files = [f.stem for f in views_dir.glob("*.py") if f.name != "__init__.py"]
    for view_name in py_files:
        imports.append(f"from product.views.{view_name} import render_view as render_{view_name}")
        route_path = '/' if view_name == 'dashboard' or len(py_files) == 1 and view_name == py_files[0] else f'/{view_name}'
        routes.append(f"""
@ui.page('{route_path}')
def route_{view_name}():
    render_{view_name}()
""")
        
    imports_block = "\n".join(imports)
    routes_block = "".join(routes)

    main_py_content = f"""from nicegui import ui

# Dynamically imported views
{imports_block}
{routes_block}

if __name__ in {{"__main__", "__mp_main__"}}:
    # Reload and show are FALSE for production edge/headless optimization
    ui.run(title='Production App', host='{host}', port={port}, reload=False, show=False)
"""
    (prod_app_dir / "main.py").write_text(main_py_content)
    
    typer.echo(typer.style(strings["cli_export_success"], fg=typer.colors.GREEN))
    typer.echo(f"Run `cd production_app` and `python main.py` to start the headless server on {host}:{port}.")

@app.command()
def start(port: int = typer.Option(None, hidden=True)) -> None:
    """Start the interactive Live Preview engine locally."""
    strings = get_locale_strings()
    
    typer.echo(typer.style(strings["cli_security_engine_warning"], fg=typer.colors.YELLOW))
    
    config = get_config()
    # strings = get_locale_strings() # Already called above
    if port is None:
        port = config.get("daemon_port", 8080)
    views_path = config.get("paths", {}).get("views", ".designgui/product/views")
    msg = strings["cli_start_engine"].format(port=port)
    typer.echo(msg)
    
    if str(Path.cwd()) not in sys.path:
        sys.path.insert(0, str(Path.cwd()))
        
    from designgui.server import run_server
    run_server(port=port, views_path=views_path)

@app.command("daemon")
def daemon_command(port: int = typer.Option(None, help="Port to run the daemon on (overrides config.json)")) -> None:
    """Initialize the backend daemon enabling Autonomous Agents to execute previews structurally in the background."""
    strings = get_locale_strings()
    
    typer.echo(typer.style(strings["cli_security_daemon_warning"], fg=typer.colors.YELLOW))
    
    config = get_config()
    # strings = get_locale_strings() # Already called above
    target_port = port if port else config.get("daemon_port", 8080)
    views_path = config.get("paths", {}).get("views", ".designgui/product/views")
    msg = strings["cli_daemon_init"].format(port=target_port)
    typer.echo(msg)
    typer.echo(f"Agents can write .py files to {views_path}/ to dynamically generate interactive dashboards.")
    
    if str(Path.cwd()) not in sys.path:
        sys.path.insert(0, str(Path.cwd()))
        
    cmd = [sys.executable, "-m", "designgui.cli", "start", "--port", str(target_port)]
    
    if sys.platform == "win32":
        # Windows detached process
        subprocess.Popen(cmd, creationflags=subprocess.DETACHED_PROCESS)
    else:
        # Unix/Linux background daemon
        subprocess.Popen(cmd, start_new_session=True)
        
    typer.echo(typer.style("Daemon launched successfully in the background.", fg=typer.colors.GREEN))

@app.command("remove")
def remove() -> None:
    """Safely removes DesignGUI from the project."""
    cwd = Path.cwd()
    strings = get_locale_strings()
    typer.echo(strings["cli_remove_start"])
    
    rule_files = [".cursorrules", ".windsurfrules", ".clinerules", ".github/copilot-instructions.md", ".prompts.md", ".lingmarules", ".comate_instructions", ".codegeex_rules"]
    for rf in rule_files:
        smart_remove_instruction(cwd / rf)
        
    designgui_dir = cwd / ".designgui"
    if designgui_dir.exists():
        shutil.rmtree(designgui_dir, ignore_errors=True)
        
    legacy_instructions = cwd / "DESIGNGUI_INSTRUCTIONS.md"
    if legacy_instructions.exists():
        legacy_instructions.unlink()

    production_app_dir = cwd / "production_app"
    if production_app_dir.exists():
        shutil.rmtree(production_app_dir, ignore_errors=True)
    
    typer.echo(typer.style(strings["cli_remove_success"], fg=typer.colors.GREEN))

if __name__ == "__main__":
    app()
