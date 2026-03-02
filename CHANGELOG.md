# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-02
### Added
- Core Live Preview engine using NiceGUI with strict Tailwind execution bindings.
- Built-in UI library encompassing layouts, display logic, primitives, inputs, composites, and feedback wrappers globally (`designgui.ui_lib`).
- Dynamic Watchdog-driven auto-reload hook bypassing the Quasar UI native reloads entirely rendering headless environments purely.
- Configurable `.designgui/config.json` system targeting IDE intercepts mapped inside `commands/` globally.
- RTL parsing properties skipping subsets natively for localized execution mappings avoiding structural flaws parsing right-to-left dynamically.
- `locale/en.json` lookup mechanism tracking generic terminal echo outputs securely.

### Fixed
- Duplicate DOM triggering loops inside standard `Inputs` mapping dict payloads.
- Stored XSS vulnerability intercepts masking inputs executing DOM attributes manually with `html.escape`.
- Broken Module resolution logic purging the `sys.modules` array tightly securing cache layers executing custom AI UI scripts.

### Security
- Injected explicit `--warning` messages dictating the raw Code Execution parameters rendering python environments natively locally via Daemons targeting arbitrary directories avoiding malicious AI injections executing blindly inside `server.py`.
