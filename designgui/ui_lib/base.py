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
        """
        Applies a specific variant of Tailwind classes based on a selection key.
        """
        if selected in variant_dict:
            self.classes(variant_dict[selected])

    def bind_value(self, target_object, target_name: str):
        """
        Binds an HTML attribute (like value) to a target object property.
        Since we aren't using Quasar v-model, we must manage simple binding ourselves if needed.
        """
        # NiceGUI Element has bind_visibility, bind_text etc.
        # But we can leverage property bindings for attributes.
        self.bind_prop('value', target_object, target_name)
        return self
