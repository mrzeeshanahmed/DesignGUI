# Component API Cheat Sheet (/shape-section)

Use these exact components from `nice_design.ui_lib.primitives` and `nice_design.ui_lib.inputs`.

- `Text(text: str, base_classes: list[str] = None)`: A span wrapper for text.
- `Box(base_classes: list[str] = None)`: A div container.
- `Flex(base_classes: list[str] = None)`: A flex row container.
- `Stack(base_classes: list[str] = None)`: A flex column container.
- `Container(base_classes: list[str] = None)`: A centered max-width container.
- `Button(text: str, on_click: Callable = None, variant: str = 'primary', base_classes: list[str] = None)`: A button. Variants: 'primary', 'ghost', 'outline'.
- `Input(placeholder: str = '', value: str = '', on_change: Callable = None, base_classes: list[str] = None)`: A text input field. Use `.bind_value_to(obj, 'prop_name')` to bind.
- `Divider(base_classes: list[str] = None)`: A horizontal line.

1. Read `product/models.py` to understand the data.
2. Generate mock data arrays.
3. Scaffold a base feature screen in `product/views/{name}.py`.
