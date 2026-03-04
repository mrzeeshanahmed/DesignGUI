![DesignGUI logo](assets/logo.png)

# DesignGUI — The Autonomous AI-Native UI Framework

[![PyPI version](https://badge.fury.io/py/designgui.svg)](https://badge.fury.io/py/designgui)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-mrzeeshanahmed-FFDD00?logo=buymeacoffee&logoColor=black)](https://www.buymeacoffee.com/mrzeeshanahmed)

**DesignGUI** is a headless, strictly-typed Python UI framework explicitly engineered for **Autonomous AI Agents** and **LLM-assisted development**.

It provides AI coding assistants (Cursor, Windsurf, GitHub Copilot, or custom SWE-agents) with a highly constrained, predictable, and composable Tailwind CSS component vocabulary. By forcing AI agents to use pre-built, secure layout wrappers instead of hallucinating raw HTML or complex frontend logic, DesignGUI guarantees beautiful, enterprise-grade user interfaces on the first prompt.

---

## ⚡ The Core Philosophy

AI agents are incredible at writing Python logic, but they are notoriously inconsistent at producing responsive, well-structured frontend CSS.

DesignGUI bridges this gap by acting as a **translation layer**. It provides a declarative Python API that completely abstracts the frontend. Agents just stack Python objects (`AuthForm`, `StatGrid`, `Sheet`, `Table`), and DesignGUI compiles them into a gorgeous, hot-reloading Tailwind frontend in real-time.

### Key Features

- 🤖 **Agent-First Vocabulary** — Ships with an injected `.designgui/INSTRUCTIONS.md` that teaches your IDE's AI exactly how to use the framework before generating a single line of code.
- 🔄 **Live Watchdog Engine** — Save a `.py` file and watch the browser instantly hot-reload. A singleton `watchdog` observer detects changes within ~100ms and re-executes the view module cleanly via `importlib`.
- 🛡️ **XSS Protected** — All user inputs and component labels are sanitised with `html.escape` by default throughout every component in the library.
- 📦 **Edge-Ready Export** — Run `designgui export` to compile your prototype into a lightweight, headless NiceGUI web server ready for Docker or Raspberry Pi deployments.
- 🌍 **RTL & i18n Ready** — Automatic RTL orientation mapping (`dir="rtl"`) for Arabic, Farsi, and Urdu locales.
- 🔒 **Secure by Default** — Persistent `storage_secret` auto-generated and saved in `config.json` on first run; never a hardcoded key in production.

---

## 🚀 Quickstart

**1. Install:**
```bash
pip install designgui
```

**2. Initialise a new project:**
```bash
designgui init
```
This prompts for your preferred AI IDE (Cursor, Windsurf, Copilot, etc.) and port, then wires up the entire `.designgui/` workspace and injects the strict agent rules into your IDE config file.

**3. Start the Live Preview:**
```bash
designgui start
# or run headless in the background:
designgui daemon
```
Open `http://localhost:8080`.

**4. Prompt your AI:**

Open `.designgui/product/views/dashboard.py` and tell your agent:

> *"Build me a SaaS dashboard using a Sidebar, a Header, and a StatGrid."*

The agent reads `INSTRUCTIONS.md`, writes the view file, and you watch the browser update live.

**5. Export to production:**
```bash
designgui export --host 0.0.0.0 --port 8080
```
Generates `production_app/main.py` — a headless NiceGUI router with `reload=False, show=False`, ready to deploy.

---

## 🏗️ The Component Ecosystem

Over 35 composable, Tailwind-native Python components organised in six layers:

| Layer | Components |
|---|---|
| **Primitives** | `Box`, `Flex`, `Stack`, `Container`, `Text`, `Divider` |
| **Inputs** | `Button`, `Input`, `ToggleSwitch`, `Slider`, `RadioGroup`, `Select`, `Checkbox`, `Textarea` |
| **Display** | `Image`, `Icon`, `Avatar`, `DropdownMenu`, `Table`, `Tabs`, `TabPanel`, `Accordion`, `Card`, `Badge`, `Modal` |
| **Layout** | `Sidebar`, `Header`, `Sheet` |
| **Feedback** | `Skeleton`, `Spinner`, `Toast` |
| **Composites** | `AuthForm`, `StatGrid`, `EmptyState`, `Stepper`, `TopNav`, `DataFeed` |

All components extend `TailwindElement`, which wraps NiceGUI's raw `Element` class directly — not a Quasar Vue component. Tailwind utility classes apply cleanly with no CSS specificity conflicts.

```python
from designgui.ui_lib.primitives import Stack, Container, Text
from designgui.ui_lib.inputs import Button
from designgui.ui_lib.composites import StatGrid

def render_view():
    with Container(base_classes=['p-8']):
        Text('Dashboard', base_classes=['text-3xl', 'font-bold', 'mb-6'])
        StatGrid(stats=[
            {'label': 'Users', 'value': '12,400', 'trend': '+8%', 'positive': True},
            {'label': 'Revenue', 'value': '$94,200', 'trend': '+12%', 'positive': True},
            {'label': 'Churn', 'value': '2.1%', 'trend': '-0.3%', 'positive': False},
        ])
        Button('Export Report', variant='primary', on_click=lambda: print('Exporting...'))
```

---

## 🔁 The 5-Loop Workflow

DesignGUI enforces a structured pipeline that every AI agent reads from `INSTRUCTIONS.md` before writing code:

| Phase | Location | Action |
|---|---|---|
| **1 — Vision** | `.designgui/product/models.py` | Define data shapes with Pydantic models |
| **2 — Shell** | `.designgui/product/shell.py` | Build global layout using `Container`, `Sidebar`, `Header` |
| **3 — Section** | `.designgui/product/views/{name}.py` | Write `render_view()` using component library + mock data |
| **4 — Screen** | Modify the view | Wire `on_click=`, `on_change=` callbacks and state |
| **5 — Export** | `production_app/` | Run `designgui export` to produce the headless build |

**The golden rule:** agents only import from `designgui.ui_lib`. No raw NiceGUI. No custom CSS.

---

## ⚙️ How It Works — End to End

### Installation & Setup

```bash
pip install designgui
```

This registers the `designgui` CLI entry point and ships four things: the component library (`designgui.ui_lib`), the CLI (`designgui.cli`), the live preview server (`designgui.server`), and locale strings (`designgui/locale/en.json`).

### The `.designgui/` Workspace

`designgui init` creates a hidden project workspace:

```
.designgui/
├── config.json          # Port, locale, font, secret, path settings
├── INSTRUCTIONS.md      # Full component API cheat sheet for AI agents
├── product/
│   ├── models.py        # (Phase 1) Pydantic models
│   ├── shell.py         # (Phase 2) Layout wrapper
│   └── views/
│       └── dashboard.py # Placeholder view
└── commands/
    ├── vision.md        # Phase 1 prompt intercept
    ├── shell.md         # Phase 2 prompt intercept
    ├── section.md       # Phase 3 component cheat sheet
    └── screen.md        # Phase 4 wiring guide
```

The `.designgui/` directory is appended to `.gitignore` automatically — it is a per-developer workspace, never committed.

### The Live Preview Engine

```
designgui start
    │
    ├─ Singleton watchdog Observer → watches views/
    │       on .py change → app.storage.general['last_modified'] = time.time()
    │
    ├─ @ui.page('/')
    │       ├─ Inject Tailwind CDN + font into <head>
    │       ├─ Set RTL/LTR on <html> and <body>
    │       ├─ Render preview chrome (title + view selector dropdown)
    │       └─ ui.timer(0.5s) → poll storage → re-import + render on change
    │
    └─ ui.run(port, reload=False)
```

**Hot-reload mechanism:** On each detected file change, the module is purged from `sys.modules`, reloaded fresh via `importlib.util.spec_from_file_location`, and `render_view()` is called inside the preview pane. Any exception is caught and displayed as a styled error block — the server never crashes.

### The Daemon Mode

`designgui daemon` spawns a fully detached background process (`DETACHED_PROCESS` on Windows, `start_new_session=True` on Unix), so autonomous agents can write and preview views without a human at the keyboard.

---

## 🔬 Deep Dive — NiceGUI Dependency

This is a **non-optional, structural dependency**. DesignGUI is not a library that uses NiceGUI as a convenience — it is built on top of NiceGUI's core runtime at every layer.

### Layer 1 — The Element System

```python
from nicegui.element import Element

class TailwindElement(Element):
    ...
```

`nicegui.element.Element` is the base class for every single component. It provides:

- **The Python-side DOM tree** — `with self:` in composites works because `Element` implements `__enter__`/`__exit__` to manage a context stack that routes children to the correct parent.
- **The `_props` dictionary** — `self._props['innerHTML'] = ...` is NiceGUI's mechanism for syncing Python-side property changes to the browser over WebSocket. `self.update()` flushes the change.
- **`self.classes(add=, remove=)`** — Used by `apply_variant`, all open/close toggles, and `Tabs` style switching.
- **`.on(event, handler, args=[])`** — The entire event system. Every `Button` click, every `Input` change, every `ToggleSwitch` toggle routes through this.

### Layer 2 — The Preview Server

| NiceGUI API | Role in DesignGUI |
|---|---|
| `ui.page('/')` | Registers the preview route with the Starlette/uvicorn router |
| `ui.run(port=, reload=, show=)` | Starts the ASGI server and WebSocket endpoint |
| `ui.add_head_html()` | Injects Tailwind CDN and font CSS into `<head>` |
| `ui.query('html').props(...)` | Sets RTL direction on the root element |
| `ui.timer(0.5, fn)` | Drives the per-client hot-reload polling loop |
| `ui.notify(...)` | Shows reload success/error toasts |
| `app.storage.general` | Cross-client shared state for watchdog timestamps |

### Layer 3 — Toast

`Toast.show()` calls `ui.notify()` directly — the one place where Quasar's `QNotify` surfaces into the public API.

### What Removing NiceGUI Would Cost

NiceGUI is as fundamental to DesignGUI as Flask is to a Flask application. Removing it would require: a new DOM-in-Python abstraction, a new WebSocket communication layer, a new ASGI server, a replacement for `ui.timer()` async integration, and a replacement for `ui.notify()`.

> **Version note:** `pyproject.toml` pins `nicegui>=1.4.0,<3.0.0`. If NiceGUI ever makes a breaking change to `Element`, `_props`, or `.on()`, every component breaks simultaneously — the ceiling bound protects against silent breakage on fresh installs.

---

## 🙏 Acknowledgements

DesignGUI was not built in a vacuum. It represents a synthesis of two brilliant open-source philosophies:

### [NiceGUI](https://github.com/zauberzeug/nicegui) — by Zauberzeug

The entire live preview and backend WebSocket routing engine of DesignGUI is powered by NiceGUI. Zauberzeug has built one of the most elegant, developer-friendly Python UI frameworks in existence. DesignGUI utilises NiceGUI's underlying Quasar/Vue.js bridge and enforces a strict Tailwind-only abstraction layer on top of it. We highly recommend checking out NiceGUI for general-purpose Python web development.

### [Design-OS](https://github.com/buildermethods/design-os) — by Builder Methods

The structural philosophy, the Shape→Shell methodology, and the concept of an AI-enforced component vocabulary were heavily inspired by Design-OS. Builder Methods proved that drastically constraining an AI's vocabulary makes its architectural output remarkably reliable. DesignGUI is an attempt to bring that exact philosophy into the Python ecosystem.

---

## 📜 License

DesignGUI is open-source software licensed under the **MIT License**. See [`LICENSE`](LICENSE) for details.
