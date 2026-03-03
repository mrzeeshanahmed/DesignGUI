from nicegui.element import Element

class TailwindElement(Element):
    """
    Base element for the Nice Design OS.
    Extends raw HTML elements to suppress Quasar default stylings.
    """
    def __init__(self, tag: str, base_classes: list[str] = None):
        super().__init__(tag)
        if base_classes:
            self.classes(' '.join(base_classes))
            
    def apply_variant(self, variant_dict: dict, selected: str):
        """Standard method to enforce predefined stylistic structures."""
        if selected in variant_dict:
            self.classes(variant_dict[selected])
        else:
            raise ValueError(f"Variant '{selected}' not found. Available options: {list(variant_dict.keys())}")
