# DesignGUI - Nice Design OS

DesignGUI is a Python Design Operating System built on top of [NiceGUI](https://nicegui.io/). It provides a 100% custom Tailwind-driven UI library and a Live Preview engine designed specifically to empower AI Agents (Cursor, Windsurf, Copilot) to autonomously construct beautiful, responsive user interfaces using the **"Prompt as Code" 5-Loop Workflow**.

## Features

- **Pure Tailwind CSS**: Bypasses Quasar's default styling, giving you complete control over your application's visual language.
- **AI-First Architecture**: Features a local CLI that generates strictly typed context files and IDE rule sets (`.cursorrules`, `.windsurfrules`, etc.) steering LLMs towards perfect component usage.
- **Live Preview Engine**: An instantaneous hot-reloading server powered by `watchdog` that renders your Python UI visually the moment the AI saves a `.py` file.
- **Rich Component Ecosystem**: Includes extensive UI blocks covering primitives (Box, Flex, Stack), interactive inputs, standard layouts (Sidebar, Header), and complex composites (StatGrid, AuthForm, DataFeed).
- **Global Ready**: Built-in support for multiple locales, automatic RTL orientation mapping, and semantic typography integration.
- **Production Export API**: Effortlessly compile your prototype into a headless `main.py` routing structure ready for edge deployment.

## Installation

```bash
pip install designgui
```

## Quick Start

1. Initialize DesignGUI inside your project folder to set up the `.designgui/` hidden workspace and inject AI tracking rules:
   ```bash
   designgui init
   ```

2. Start the Live Preview Engine to activate hot-reloading:
   ```bash
   designgui start
   ```

3. Open your browser to `http://localhost:8080`.
4. Prompt your AI Agent (e.g. Cursor) to build a new screen. The engine will instantly render changes saved to `.designgui/product/views/`.

## The 5-Loop Workflow

DesignGUI trains your AI IDE using a strictly structured pipeline:

- **Phase 1 (Vision)**: Outline concept concepts and Pydantic models in `.designgui/product/models.py`.
- **Phase 2 (Shell)**: Build global layout wrappers in `.designgui/product/shell.py`.
- **Phase 3 (Section)**: Generate mock data and UI views in `.designgui/product/views/*.py`.
- **Phase 4 (Screen)**: Wire Python callbacks (`on_click=...`) and inject state.

You can explicitly trigger these behaviors using `designgui init` hooks mapped to standard `.md` workflows inside `.designgui/commands/`.

## Export to Production

When your application looks perfect, bundle it dynamically:

```bash
designgui export --host 0.0.0.0 --port 8080
```
This generates an optimized, headless backend routing payload inside `production_app/main.py`.

## License

MIT License. See `LICENSE` for details.
