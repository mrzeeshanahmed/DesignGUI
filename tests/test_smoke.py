"""
Smoke Tests for DesignGUI
=========================
Fast, zero-dependency regression gates.
No NiceGUI event loop required — uses hasattr() and inspect.getsource()
to validate structure without runtime dependencies.
"""
import inspect

import designgui
from designgui.ui_lib import (
    TailwindElement, Box, Flex, Stack, Container, Text, Divider,
    Button, Input, ToggleSwitch, Slider, RadioGroup, Select, Checkbox, Textarea,
    Image, Icon, Avatar, DropdownMenu, Table, Tabs, TabPanel, Accordion, Card, Badge, Modal,
    Sidebar, Header, Sheet,
    Skeleton, Spinner, Toast,
    AuthForm, StatGrid, EmptyState, Stepper, TopNav, DataFeed
)


def test_version_exists():
    """designgui.__version__ must be a non-empty string."""
    assert isinstance(designgui.__version__, str)
    assert len(designgui.__version__) > 0


def test_all_exports_importable():
    """Every symbol declared in ui_lib.__all__ must be importable.
    This catches any future export omission like the TabPanel bug."""
    from designgui import ui_lib
    for name in ui_lib.__all__:
        obj = getattr(ui_lib, name, None)
        assert obj is not None, f"'{name}' is listed in __all__ but is not importable from designgui.ui_lib"


def test_sheet_has_close_method():
    """Sheet must define close() — without it, clicking X crashes the app."""
    assert hasattr(Sheet, 'close'), "Sheet.close() is missing"
    assert callable(getattr(Sheet, 'close')), "Sheet.close is not callable"


def test_select_has_border_class():
    """Select.__init__ source must include 'border' as a standalone Tailwind class.
    Without it, border-gray-300 (color only) renders an invisible border."""
    src = inspect.getsource(Select.__init__)
    # Check for 'border' as a standalone string entry in the classes list
    # Must NOT match substrings like 'border-gray-300'
    assert "'border'" in src or '"border"' in src, (
        "Select.__init__ is missing the standalone 'border' class. "
        "border-gray-300 sets color only; 'border' sets border-width: 1px."
    )
