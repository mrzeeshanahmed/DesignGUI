from typing import Callable, Optional, Any
from .base import TailwindElement

class Button(TailwindElement):
    def __init__(self, text: str = 'Button', on_click: Optional[Callable] = None, variant: str = 'primary', base_classes: list[str] = None):
        """
        Custom Tailwind Button extending raw HTML <button>
        """
        classes = [
            'px-4', 'py-2', 'rounded', 'font-medium', 'focus:outline-none', 'transition-colors', 'duration-200', 'cursor-pointer'
        ]
        if base_classes:
            classes.extend(base_classes)
            
        super().__init__('button', classes)
        
        # We manually inject the text using HTML content
        self._props['innerHTML'] = text
        
        # Variants dictionary
        variants = {
            'primary': 'bg-blue-600 text-white hover:bg-blue-700',
            'ghost': 'bg-transparent text-gray-700 hover:bg-gray-100',
            'outline': 'bg-transparent border border-gray-300 text-gray-700 hover:bg-gray-50'
        }
        self.apply_variant(variants, variant)
        
        if on_click:
            self.on('click', on_click)


class Input(TailwindElement):
    def __init__(self, placeholder: str = '', value: str = '', on_change: Optional[Callable] = None, base_classes: list[str] = None):
        """
        Custom Tailwind Input extending raw HTML <input>
        """
        classes = [
            'px-3', 'py-2', 'border', 'border-gray-300', 'rounded', 'shadow-sm', 
            'focus:outline-none', 'focus:border-blue-500', 'focus:ring-1', 'focus:ring-blue-500'
        ]
        if base_classes:
            classes.extend(base_classes)
            
        super().__init__('input', classes)
        
        self.value = value
        self._props['placeholder'] = placeholder
        self._props['value'] = value
        
        # Handle the raw DOM input event
        # When user types, nicegui sends an event, we update internal value and call user callback if any
        def handle_input(e: Any):
            val = e.args.get('target.value', e.args) # Fallback if just passed directly
            self.value = val
            self._props['value'] = val
            if on_change:
                on_change(val)
                
        # To get the raw value back from the input event, we must tell nicegui what event data to include
        # In Vue, native input events pass an Event object where the value is in target.value
        self.on('input', handle_input, args=['target.value'])
        
    def bind_value_to(self, target_object, target_name: str):
        """Helper to simulate two-way binding or pushing value to model."""
        def handle_change(v):
            setattr(target_object, target_name, v)
        self.on('input', lambda e: handle_change(e.args.get('target.value', e.args)), args=['target.value'])
        # Initialize
        setattr(target_object, target_name, self.value)
        return self
