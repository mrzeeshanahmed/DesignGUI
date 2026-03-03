# DesignGUI — Pre-PyPI Deployment Implementation Plan

> **Audit date:** 2026-03-03 | **Package version:** 0.1.0  
> **Scope:** Full codebase audit against all reported issues plus independent discovery.  
> Every issue below is verified against the live source code. Claim vs. reality is stated explicitly.

---

## Part 1 — Verdict on All Reported Issues

This section adjudicates each issue that was submitted for review. Each is marked **CONFIRMED** (exists in code as described), **PARTIALLY CONFIRMED** (the concern is real but the cause/location differs), or **NOT PRESENT** (issue does not exist in the current code).

---

### Reported Issue 1 — Thread Leak & Multi-Tab Conflicts (`server.py`)

**Verdict: NOT PRESENT**

The description alleges that `preview_environment()` spins up a new `watchdog.Observer` thread on every page load. The current code does the opposite. A `_observer_instance` global singleton is declared at module level and `get_or_create_observer()` guards it with a `if _observer_instance is None` check. The Observer is started once inside `run_server()` before the `@ui.page('/')` route is registered. Per-client interaction uses a `ui.timer(0.5, check_for_updates)` which is correctly scoped per NiceGUI client context. No thread explosion occurs.

**No fix required for the stated problem.**

---

### Reported Issue 2 — Destructive Re-Rendering causing Focus Loss (`ui_lib/inputs.py`)

**Verdict: NOT PRESENT**

The description alleges that `ToggleSwitch`, `Select`, `Checkbox`, and `RadioGroup` call `render_dom()` on every `change` event, wiping the DOM. None of these components have a `render_dom()` method or any `innerHTML` reassignment in their event handlers. All four use incremental prop mutation:

- `ToggleSwitch`: `self._input.props('checked')` / `self._input.props(remove='checked')`
- `RadioGroup`: `radio.props('checked')` / `radio.props(remove='checked')` per option element
- `Checkbox`: `self._input.props('checked')` / `self._input.props(remove='checked')`
- `Select`: `el.props('selected')` / `el.props(remove='selected')` per option element

The DOM is built once in `__init__` and never wiped. No focus loss from this mechanism.

**No fix required for the stated problem.**

---

### Reported Issue 3 — Non-Functional Pseudo-Binding (`ui_lib/base.py`)

**Verdict: NOT PRESENT**

The description refers to a `bind_attribute(self, attr_name, target_object, target_name)` method with a broken watcher. No such method exists in `TailwindElement`. The class has exactly two methods: `__init__` and `apply_variant`. There is no dead binding code.

**No fix required for the stated problem.**

---

### Reported Issue 4 — Unsafe Type Injections in `Slider` (`ui_lib/inputs.py`)

**Verdict: NOT PRESENT — Already Fixed**

The description claims the `Slider` component has an unguarded `float()` cast. The actual code at line ~147 already wraps the cast in a `try/except (ValueError, TypeError)` block with a `val = self.value` fallback:

```python
try:
    val = float(e.args.get('target.value', self.value)) if isinstance(e.args, dict) else float(e.args)
except (ValueError, TypeError):
    val = self.value
```

**No fix required.**

---

### Reported Issue 5 — Dead Code in `Sheet.__init__` (`ui_lib/layout.py`)

**Verdict: CONFIRMED**

`Sheet.__init__` constructs a 15-line `header_dom` f-string template containing the header title and close-button SVG HTML. This variable is then immediately abandoned. The with-block below it constructs the same header using `Flex`, `Text`, and `Button` components. The dead code is fully inert but pollutes the file and creates confusion about which code path the header comes from.

**Fix required. See Section 2, Fix #5.**

---

### PyPI Blocker 1 — Malformed Classifier (`pyproject.toml`)

**Verdict: NOT PRESENT**

All classifiers in `pyproject.toml` are syntactically valid TOML strings on single lines. The `"Programming Language :: Python :: 3.11"` classifier is not split across lines. `twine check` would not reject this package for classifier reasons.

**No fix required.**

---

### PyPI Blocker 2 — `RadioGroup` Name Cross-Pollination (`ui_lib/inputs.py`)

**Verdict: NOT PRESENT**

The description alleges that `name` defaults to the literal string `"radio-group"`. The actual default is `f"radio-group-{id(self)}"`, which generates a unique name per Python object using its memory address. Multiple `RadioGroup` instances on the same page will each receive a distinct `name` attribute.

**No fix required.**

---

### PyPI Blocker 3 — `DropdownMenu` uses `ui.element('button')` (`ui_lib/display.py`)

**Verdict: NOT PRESENT**

`DropdownMenu.render_dom()` uses `TailwindElement('button')`, not `ui.element('button')`. Both the trigger button and all menu item `a` tags use `TailwindElement`. The Quasar CSS baseline leak described does not occur via this path.

**Note:** A different, real architectural issue was discovered in `DropdownMenu`. See Section 2, Fix #3.

---

### PyPI Blocker 4 — Untranslated Daemon Success String (`cli.py`)

**Verdict: NOT PRESENT**

The `daemon_command` uses `strings.get("cli_daemon_success", "Daemon launched successfully in the background.")`. The key `"cli_daemon_success"` is present in `designgui/locale/en.json`. The locale system is functioning correctly.

**No fix required.**

---

## Part 2 — Confirmed Real Issues (Discovered by Audit)

These are genuine bugs found by independently reading the source, distinct from the reported list.

---

### Fix #1 — Double HTML Escaping in `Sheet` Title

**File:** `designgui/ui_lib/layout.py`  
**Severity:** Medium — Data Integrity / Visual Corruption  
**Status:** Bug — renders HTML entities as literal text for titles containing `&`, `<`, `>`, `"`, `'`

**Root Cause:**

`Sheet.__init__` pre-escapes the title:
```python
self._title = html.escape(title)  # e.g., "Alerts &amp; Warnings"
```
Then passes it to `Text()`:
```python
Text(self._title, ['text-lg', 'font-medium', 'text-gray-900'])
```
`Text.__init__` calls `html.escape()` a second time:
```python
self._props['innerHTML'] = html.escape(str(text))  # becomes "Alerts &amp;amp; Warnings"
```
A title like `"User & Admin Panel"` renders in the browser as `"User &amp; Admin Panel"` instead of `"User & Admin Panel"`.

**Fix:** Remove the pre-escaping assignment. Pass `title` (raw) directly to `Text()` and let `Text` handle the single correct escaping:

```python
# BEFORE
self._title = html.escape(title)
...
Text(self._title, ['text-lg', 'font-medium', 'text-gray-900']).classes('m-0')

# AFTER
self._title = title  # raw; Text() will escape it correctly
...
Text(self._title, ['text-lg', 'font-medium', 'text-gray-900']).classes('m-0')
```

The `header_dom` template (dead code) also uses `self._title`, so it will be cleaned up as part of Fix #5.

---

### Fix #2 — Double HTML Escaping of Labels in `ToggleSwitch`, `RadioGroup`, `Checkbox`

**File:** `designgui/ui_lib/inputs.py`  
**Severity:** Medium — Data Integrity / Visual Corruption  
**Affects:** All three components when the label/option text contains `&`, `<`, `>`, `"`, `'`

**Root Cause:**

All three components call `html.escape()` on the user-supplied text, then pass the pre-escaped result to `set_text()`. NiceGUI's `set_text()` sets the DOM `textContent` (not `innerHTML`), which means the browser treats the value as literal text, not markup. Any HTML entities in the string are displayed verbatim.

Chain in `ToggleSwitch`:
```python
safe_label = html.escape(label)         # "R&amp;D" if label is "R&D"
ui.element('span')...set_text(safe_label)  # browser shows "R&amp;D"
```

Same pattern in `RadioGroup` (option span) and `Checkbox` (label span).

**Fix:** Remove `html.escape()` calls before `set_text()`. The method is inherently XSS-safe as it sets `textContent`.

```python
# BEFORE (ToggleSwitch)
safe_label = html.escape(label)
ui.element('span')...set_text(safe_label)

# AFTER
ui.element('span')...set_text(label)

# BEFORE (RadioGroup)
safe_opt = html.escape(opt)
...
ui.element('span')...set_text(safe_opt)

# AFTER
ui.element('span')...set_text(opt)

# BEFORE (Checkbox)
safe_label = html.escape(label)
ui.element('span')...set_text(safe_label)

# AFTER
ui.element('span')...set_text(label)
```

The `radio` input `value` attribute and `name` attribute must still use escaped values because they go into `.props()` attribute strings, not text content. Those `html.escape()` calls should be preserved:
```python
# KEEP this (attribute value in .props() string)
radio = ui.element('input').props(f'type="radio" value="{html.escape(opt)}" name="{self._name}"')
```

---

### Fix #3 — Unquoted Double-Quote Character Breaks `innerHTML` Prop in `DropdownMenu` and `Tabs`

**File:** `designgui/ui_lib/display.py`  
**Severity:** Medium — Robustness / Silent Rendering Failure  
**Affects:** `DropdownMenu` trigger button label and all `Tabs` tab button labels

**Root Cause:**

Both components inject text into the DOM via a `.props()` string template:
```python
# DropdownMenu
.props(f'innerHTML="{html.escape(self.label)}"')

# Tabs
.props(f'innerHTML="{html.escape(tab)}"')
```
`html.escape()` by default does **not** escape double-quote characters (`"` → `"`). If a label contains a `"` character — e.g. `'5" Display'` — the generated prop string becomes:
```
innerHTML="5" Display"
```
This terminates the attribute value early, leaving ` Display"` as dangling markup that NiceGUI's prop parser discards silently. The button renders with truncated or empty text.

**Fix:** Switch from the `.props()` string injection pattern to direct `_props['innerHTML']` assignment, which accepts a Python string without attribute-quoting concerns:

```python
# BEFORE (DropdownMenu)
TailwindElement('button')...props(f'innerHTML="{html.escape(self.label)}"')

# AFTER
btn = TailwindElement('button')...
btn._props['innerHTML'] = html.escape(self.label)
btn.update()

# BEFORE (Tabs)
btn = TailwindElement('button')...props(f'innerHTML="{html.escape(tab)}"')

# AFTER
btn = TailwindElement('button')...
btn._props['innerHTML'] = html.escape(tab)
```

---

### Fix #4 — Hardcoded `storage_secret` in `server.py`

**File:** `designgui/server.py`  
**Severity:** Medium — Security  

**Root Cause:**

```python
ui.run(..., storage_secret="dev_secret_key_123")
```
The `storage_secret` value is used by NiceGUI to sign its server-side storage (equivalent to a Flask `SECRET_KEY`). Hardcoding a known, public value in a published open-source package means every deployed DesignGUI instance uses the same signing secret. An attacker who knows the secret could forge or tamper with `app.storage` values.

**Fix:** Read the secret from `config.json` if present; generate and persist a random fallback if not:

```python
import secrets as _secrets

def _get_storage_secret(config: dict) -> str:
    """Return storage secret from config or generate + persist a random one."""
    secret = config.get("storage_secret")
    if secret:
        return secret
    # Generate and persist for this project instance
    new_secret = _secrets.token_hex(32)
    config_path = Path(".designgui/config.json")
    if config_path.exists():
        try:
            data = json.loads(config_path.read_text())
            data["storage_secret"] = new_secret
            config_path.write_text(json.dumps(data, indent=2))
        except Exception:
            pass
    return new_secret
```

Then in `run_server()`:
```python
config = {}
try:
    config = json.loads(Path(".designgui/config.json").read_text())
except Exception:
    pass
storage_secret = _get_storage_secret(config)
ui.run(..., storage_secret=storage_secret)
```

---

### Fix #5 — Dead Code: `header_dom` Template in `Sheet.__init__` (`ui_lib/layout.py`)

**File:** `designgui/ui_lib/layout.py`  
**Severity:** Low — Code Hygiene  
**Status:** Confirmed; `header_dom` is defined but never referenced

**Root Cause:**

The `Sheet.__init__` builds a multi-line f-string:
```python
header_dom = f"""
<div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
    <h2 class="text-lg font-medium text-gray-900">{self._title}</h2>
    <button ... onclick="this.parentElement.parentElement.classList.add('translate-x-full')">
        ...
    </button>
</div>
"""
```
The variable is never passed to `_props['innerHTML']` or used anywhere. The actual header is rendered by the `with self:` block using `Flex`, `Text`, and `Button` components below it.

**Fix:** Delete the entire `header_dom` f-string block and the dead comment that follows it.

---

### Fix #6 — No Upper Version Bound on `nicegui` in `pyproject.toml`

**File:** `pyproject.toml`  
**Severity:** Low — Deployment Risk  

**Root Cause:**

```toml
dependencies = [
    "nicegui>=1.4.0",  # no upper bound
    ...
]
```
`TailwindElement` inherits from `nicegui.element.Element` and uses `_props`, `self.classes()`, `self.on()`, and `self.update()` — all internal NiceGUI APIs. A major NiceGUI version bump with breaking API changes would silently destroy all 35+ components simultaneously on a fresh `pip install designgui`.

**Fix:**
```toml
"nicegui>=1.4.0,<3.0.0",
```
Set the ceiling to `<3.0.0` after verifying the test matrix passes on the latest 2.x release. Revisit when NiceGUI 3.0 is released.

---

### Fix #7 — `DropdownMenu` Click Toggle Is Non-Functional (`_toggle_menu` is `pass`)

**File:** `designgui/ui_lib/display.py`  
**Severity:** Low — UX, Mobile Accessibility  

**Root Cause:**

The trigger button has `on('click', lambda: self._toggle_menu())`. The `_toggle_menu` method body is:
```python
def _toggle_menu(self):
    pass
```
The dropdown visibility relies entirely on the CSS `group-hover:block` pattern, which only activates on pointer hover. On touch devices (mobile, tablet), hover does not exist. Clicking/tapping the trigger button fires `_toggle_menu`, which does nothing. The dropdown is permanently inaccessible on touch interfaces.

**Fix:** Implement `_toggle_menu` to toggle a CSS visibility class on `_menu_container`:

```python
def _toggle_menu(self):
    current_classes = self._menu_container.classes  # inspect current class string
    if 'hidden' in str(current_classes):
        self._menu_container.classes(remove='hidden')
    else:
        self._menu_container.classes('hidden')
```

Also update `_menu_container` initial class to use both `hidden` (default) and `group-hover:block` so hover still works on desktop while click toggle works everywhere.

---

## Part 3 — Complete Fix Priority Table

| # | File | Issue | Severity | Action Required |
|---|---|---|---|---|
| 1 | `ui_lib/layout.py` | Double HTML escape on `Sheet` title | Medium | Remove `html.escape()` from `self._title` assignment |
| 2 | `ui_lib/inputs.py` | Double HTML escape in `ToggleSwitch`, `RadioGroup`, `Checkbox` labels | Medium | Remove `html.escape()` before `set_text()` calls (keep it for `.props()` attribute injections) |
| 3 | `ui_lib/display.py` | Unquoted `"` breaks `innerHTML` prop in `DropdownMenu` + `Tabs` | Medium | Switch from `.props(f'innerHTML="..."')` to `._props['innerHTML'] = html.escape(text)` |
| 4 | `server.py` | Hardcoded `storage_secret` | Medium | Read from `config.json`; auto-generate and persist if absent |
| 5 | `ui_lib/layout.py` | Dead `header_dom` variable in `Sheet.__init__` | Low | Delete the unreachable f-string block |
| 6 | `pyproject.toml` | No `nicegui` upper version bound | Low | Add `<3.0.0` ceiling |
| 7 | `ui_lib/display.py` | `DropdownMenu._toggle_menu` is empty `pass` | Low | Implement class toggle on `_menu_container` |

---

## Part 4 — Phantom Issues Reference (Reported but Not in Code)

Documented for record-keeping. These were reported but independently verified to **not exist** in the current codebase.

| Reported | Claim | Actual Status |
|---|---|---|
| Thread Leak in `server.py` | New Observer spawned per page load | `_observer_instance` singleton already implemented in `get_or_create_observer()` |
| Destructive Re-Rendering in `inputs.py` | `render_dom()` wipes DOM on every change event | No component calls `render_dom()` after `__init__`; all change handlers use incremental `.props()` mutation |
| Dead `bind_attribute` in `base.py` | `TailwindElement` has a broken reactive binding method | Method does not exist; `TailwindElement` has only `__init__` and `apply_variant` |
| Unsafe `Slider` `float()` cast | Unguarded `ValueError` on bad WebSocket input | `try/except (ValueError, TypeError)` already wraps the cast |
| Malformed PyPI classifier in `pyproject.toml` | Newline splits `3.11` classifier | All classifier strings are valid single-line TOML |
| `RadioGroup` name cross-pollination | Hardcoded `name="radio-group"` default | Default generates `f"radio-group-{id(self)}"` — unique per instance |
| `DropdownMenu` uses `ui.element('button')` | Leaks raw NiceGUI object into public API | `render_dom()` uses `TailwindElement('button')` throughout |
| Untranslated daemon success string in `cli.py` | Hard-coded string bypasses locale system | Uses `strings.get("cli_daemon_success", ...)` — key present in `en.json` |

---

## Part 5 — Detailed Implementation Steps

### Step 1 — Fix `Sheet` Double Escape (`layout.py`)

**Location:** `Sheet.__init__`, around line 35 in `layout.py`

1. Change `self._title = html.escape(title)` to `self._title = title`
2. Remove the entire `header_dom = f"""..."""` block and the comment block immediately below it (approximately 15 lines ending with `# To keep it simple, we don't mix innerHTML...`)
3. The `Text(self._title, ...)` call remains unchanged — `Text.__init__` handles escaping correctly

**Before:**
```python
self.is_open = False
self._title = html.escape(title)

header_dom = f"""
<div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
    ... (15 lines of dead HTML template)
</div>
"""

# In strictly composable NiceGUI, ...
# Since NiceGUI adds children ...
# To keep it simple, ...

from .primitives import Box, Flex, Text
```

**After:**
```python
self.is_open = False
self._title = title

from .primitives import Box, Flex, Text
```

---

### Step 2 — Fix `set_text()` Double Escaping (`inputs.py`)

**Locations:**

a) `ToggleSwitch.__init__` (~line 95):
```python
# REMOVE this line:
safe_label = html.escape(label)
# CHANGE this line:
ui.element('span')...set_text(safe_label)
# TO:
ui.element('span')...set_text(label)
```

b) `RadioGroup.__init__` (~line 165):
```python
# REMOVE:
safe_opt = html.escape(opt)
# KEEP: radio.props(f'...value="{html.escape(opt)}"...')  ← this one stays
# CHANGE:
ui.element('span')...set_text(safe_opt)
# TO:
ui.element('span')...set_text(opt)
```

c) `Checkbox.__init__` (~line 235):
```python
# REMOVE:
safe_label = html.escape(label)
# CHANGE:
ui.element('span')...set_text(safe_label)
# TO:
ui.element('span')...set_text(label)
```

---

### Step 3 — Fix `innerHTML` Prop Injection in `DropdownMenu` and `Tabs` (`display.py`)

**Location a) `DropdownMenu.render_dom()`:**

Chain `.props(f'innerHTML="{html.escape(self.label)}"')` on the trigger button — split into two statements:
```python
trigger_btn = TailwindElement('button').classes(
    'inline-flex justify-center w-full rounded-md border border-gray-300 '
    'shadow-sm px-4 py-2 bg-white text-sm font-medium text-gray-700 '
    'hover:bg-gray-50 focus:outline-none'
).props('type="button"')
trigger_btn._props['innerHTML'] = html.escape(self.label)
trigger_btn.on('click', lambda: self._toggle_menu())
```

**Location b) `Tabs.render_dom()`:**

Change the `btn` creation from:
```python
btn = TailwindElement('button').classes(...).props('type="button"').props(f'innerHTML="{html.escape(tab)}"').on('click', create_handler(tab))
```
To:
```python
btn = TailwindElement('button').classes(...).props('type="button"')
btn._props['innerHTML'] = html.escape(tab)
btn.on('click', create_handler(tab))
```

---

### Step 4 — Fix Hardcoded `storage_secret` (`server.py`)

Add `_get_storage_secret()` helper function before `preview_environment()`. In `run_server()`, load `config.json` and call the helper instead of passing the hardcoded string literal.

```python
import secrets as _secrets

def _get_storage_secret() -> str:
    config_path = Path(".designgui/config.json")
    try:
        config = json.loads(config_path.read_text())
        if "storage_secret" in config:
            return config["storage_secret"]
        # Generate, persist, and return
        new_secret = _secrets.token_hex(32)
        config["storage_secret"] = new_secret
        config_path.write_text(json.dumps(config, indent=2))
        return new_secret
    except Exception:
        return _secrets.token_hex(32)
```

In `run_server()`, replace:
```python
ui.run(title='Nice Design OS - Live Preview', port=port, reload=False, storage_secret="dev_secret_key_123")
```
With:
```python
ui.run(title='Nice Design OS - Live Preview', port=port, reload=False, storage_secret=_get_storage_secret())
```

---

### Step 5 — Remove Dead `header_dom` Code (`layout.py`)

Already covered in Step 1. The `header_dom` f-string and the comment block below it are both deleted as part of that step.

---

### Step 6 — Add `nicegui` Upper Version Bound (`pyproject.toml`)

```toml
dependencies = [
    "nicegui>=1.4.0,<3.0.0",
    "typer>=0.9.0",
    "watchdog>=3.0.0"
]
```

---

### Step 7 — Implement `DropdownMenu._toggle_menu()` (`display.py`)

```python
def _toggle_menu(self):
    # Check if menu is currently hidden and toggle
    if hasattr(self, '_menu_container'):
        classes_str = ' '.join(self._menu_container._classes) if hasattr(self._menu_container, '_classes') else ''
        if 'hidden' in classes_str:
            self._menu_container.classes(remove='hidden')
        else:
            self._menu_container.classes('hidden')
```

---

## Part 6 — Verification Checklist

After all fixes are applied, run the following before tagging a release:

### Automated
```bash
# 1. Syntax validation — all ui_lib modules must compile cleanly
python -m py_compile designgui/ui_lib/base.py
python -m py_compile designgui/ui_lib/primitives.py
python -m py_compile designgui/ui_lib/inputs.py
python -m py_compile designgui/ui_lib/display.py
python -m py_compile designgui/ui_lib/layout.py
python -m py_compile designgui/ui_lib/feedback.py
python -m py_compile designgui/ui_lib/composites.py
python -m py_compile designgui/cli.py
python -m py_compile designgui/server.py

# 2. Full test suite — all 10 must pass
python -m pytest tests/ -v

# 3. Build and twine metadata check
python -m build
twine check dist/*
```

### Manual Spot-Checks
- [ ] Create a `Sheet("User & Admin")` — title should render as `User & Admin`, not `User &amp; Admin`
- [ ] Create a `ToggleSwitch("R&D Toggle")` — label should render as `R&D Toggle`
- [ ] Create a `DropdownMenu('Say "Hello"', ["Item 1"])` — button should render as `Say "Hello"` without truncation
- [ ] Create a `Tabs(['Tab "A"', 'Tab "B"'])` — tab labels should render correctly
- [ ] Run `designgui start`, open in 5 browser tabs simultaneously — confirm `ps aux | grep python` shows exactly one watchdog thread, not five
- [ ] Confirm `.designgui/config.json` gains a `storage_secret` field on first server start and retains it on restart
- [ ] Open `DropdownMenu` on a touch-capable device — confirm click opens the dropdown panel
- [ ] Verify `Sheet.__init__` no longer has the `header_dom` variable

---

*Plan generated: 2026-03-03*
