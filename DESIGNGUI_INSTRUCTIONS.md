# Nice Design OS - Comprehensive Agent Instructions

You are operating in a Nice Design OS project. You must strictly follow these rules:

1. You are an expert Python UI developer using the `nice_design.ui_lib` framework.
2. DO NOT use React, Vue, HTML, or standard NiceGUI elements like `ui.button` or `ui.input`.
3. ONLY use primitives from `nice_design.ui_lib.primitives` (Container, Stack, Flex, Box, Text, Divider) and `nice_design.ui_lib.inputs` (Button, Input).

## The 5-Loop Flow
When given a feature prompt, execute these steps:
- **Phase 1 (Vision)**: Outline concept in `product/specs/vision.md` and Pydantic schema in `product/models.py`.
- **Phase 2 (Shell)**: Build global layout wrapper in `product/shell.py`.
- **Phase 3 (Section)**: Generate mock data and a UI view in `product/views/{name}.py` using the primitive components.
- **Phase 4 (Screen)**: Wire Python callbacks (`on_click=...`) and inject state.
