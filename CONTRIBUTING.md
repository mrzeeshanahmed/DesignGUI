# Contributing to DesignGUI

Thank you for your interest in contributing to the Nice Design OS!

DesignGUI relies strictly on extending its native Tailwind CSS framework layer.

## Guidelines
1. **No Quasar Components**: Do not utilize standard NiceGUI UI elements mapped to Quasar (such as `ui.button`, `ui.input`). You must construct or use the native wrappers in `designgui.ui_lib`.
2. **Prop Bindings**: To keep inputs completely modular, construct `TailwindElement`(s) and leverage the native `self._props['innerHTML']` rendering structure paired with standard Python `html.escape` sanitation avoiding code injections.
3. **Locale Execution**: When updating CLI commands natively within `cli.py`, append your text strings identically into `locale/en.json` pulling the dictionary mapping natively through `get_locale_strings()` bypassing raw prints.

### Testing
Use `designgui start` passing generic models directly out of `.designgui/product/views/dashboard.py` mimicking AI operations to review bindings dynamically before pull requests.
