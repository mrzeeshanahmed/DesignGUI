import html
from typing import Callable, Optional, Any, List
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
        
        # We manually inject the text using HTML content securely
        self._props['innerHTML'] = html.escape(str(text))
        
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
        
        # Add state tracking for bound change listeners to avoid duplicate events
        self._on_change_callback = on_change
        
        # Handle the raw DOM input event
        # When user types, nicegui sends an event, we update internal value and call user callback if any
        def handle_input(e: Any):
            # Safe extraction avoiding passing raw dict arrays into layout
            val = e.args.get('target.value', '') if isinstance(e.args, dict) else ''
            self.value = val
            self._props['value'] = val
            if self._on_change_callback:
                self._on_change_callback(val)
                
        self.on('input', handle_input, args=['target.value'])
        
    def bind_value_to(self, target_object, target_name: str):
        """Helper to simulate two-way binding or pushing value to model."""
        def handle_change(v):
            setattr(target_object, target_name, v)
            
        # Instead of directly binding a second input map causing duplicates, hook into existing callback loop.
        old_cb = self._on_change_callback
        def chained_cb(val):
            if old_cb:
                old_cb(val)
            handle_change(val)
            
        self._on_change_callback = chained_cb
        # Initialize
        setattr(target_object, target_name, self.value)
        return self

class ToggleSwitch(TailwindElement):
    def __init__(self, label: str = "", value: bool = False, on_change: Optional[Callable] = None, base_classes: list[str] = None):
        """
        Tailwind Wrapper for a checkbox acting as a toggle switch.
        """
        classes = ['flex', 'items-center', 'cursor-pointer']
        if base_classes:
            classes.extend(base_classes)
        super().__init__('label', classes)
        
        self.value = value
        self._on_change_callback = on_change
        
        self._input_id = f"toggle-{id(self)}"
        
        from nicegui import ui
        with self:
            with ui.element('div').classes('relative'):
                self._input = ui.element('input').classes('sr-only peer').props(f'type="checkbox" id="{self._input_id}"')
                if self.value:
                    self._input.props('checked')
                ui.element('div').classes('w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[\'\'] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600')
            ui.element('span').classes('ml-3 text-sm font-medium text-gray-900').set_text(label)
            
        def handle_change(e: Any):
            if e.args and isinstance(e.args, dict) and 'target.checked' in e.args:
                self.value = bool(e.args.get('target.checked'))
            else:
                self.value = not self.value
                
            if self.value:
                self._input.props('checked')
            else:
                self._input.props(remove='checked')
                
            if self._on_change_callback:
                self._on_change_callback(self.value)
                
        self.on('change', handle_change)

class Slider(TailwindElement):
    def __init__(self, min: float = 0, max: float = 100, step: float = 1, value: float = 50, on_change: Optional[Callable] = None, base_classes: list[str] = None):
        """
        Tailwind Wrapper for an input[type=range].
        """
        classes = ['w-full', 'h-2', 'bg-gray-200', 'rounded-lg', 'appearance-none', 'cursor-pointer']
        if base_classes:
            classes.extend(base_classes)
        super().__init__('input', classes)
        
        self._props['type'] = 'range'
        self._props['min'] = min
        self._props['max'] = max
        self._props['step'] = step
        self._props['value'] = value
        
        self.value = value
        self._on_change_callback = on_change
        
        def handle_input(e: Any):
            try:
                val = float(e.args.get('target.value', self.value)) if isinstance(e.args, dict) else float(e.args)
            except (ValueError, TypeError):
                val = self.value
                
            self.value = val
            self._props['value'] = val
            if self._on_change_callback:
                self._on_change_callback(val)
                
        self.on('input', handle_input, args=['target.value'])

class RadioGroup(TailwindElement):
    def __init__(self, options: List[str], value: str, name: str = None, on_change: Optional[Callable] = None, base_classes: list[str] = None):
        """
        Tailwind Wrapper for a group of radio buttons.
        """
        classes = ['flex', 'flex-col', 'space-y-2']
        if base_classes:
            classes.extend(base_classes)
        super().__init__('div', classes)
        
        self.value = value
        self.options = options
        self._name = name if name else f"radio-group-{id(self)}"
        self._on_change_callback = on_change
        self._radio_elements = {}
        
        from nicegui import ui
        with self:
            for opt in self.options:
                safe_opt = html.escape(opt)
                with ui.element('label').classes('flex items-center cursor-pointer'):
                    radio = ui.element('input').classes('w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500').props(f'type="radio" value="{safe_opt}" name="{self._name}"')
                    if opt == self.value:
                        radio.props('checked')
                    self._radio_elements[opt] = radio
                    ui.element('span').classes('ml-2 text-sm font-medium text-gray-900').set_text(opt)
                    
        def handle_change(e: Any):
            val = e.args.get('target.value', self.value) if isinstance(e.args, dict) else self.value
            self.value = val
            for opt, radio in self._radio_elements.items():
                if opt == val:
                    radio.props('checked')
                else:
                    radio.props(remove='checked')
                    
            if self._on_change_callback:
                self._on_change_callback(val)
                
        self.on('change', handle_change, args=['target.value'])

class Select(TailwindElement):
    def __init__(self, options: List[str], value: str = None, on_change: Optional[Callable] = None, base_classes: list[str] = None):
        """
        Tailwind Wrapper for a native HTML <select>.
        """
        classes = ['block', 'w-full', 'pl-3', 'pr-10', 'py-2', 'text-base', 'border', 'border-gray-300', 'focus:outline-none', 'focus:ring-blue-500', 'focus:border-blue-500', 'sm:text-sm', 'rounded-md', 'bg-white']
        if base_classes:
            classes.extend(base_classes)
        super().__init__('select', classes)
        
        self.value = value if value else (options[0] if options else None)
        self.options = options
        self._on_change_callback = on_change
        self._option_elements = {}
        
        from nicegui import ui
        with self:
            for opt in self.options:
                safe_opt = html.escape(opt)
                option_el = ui.element('option').props(f'value="{safe_opt}"').set_text(opt)
                if opt == self.value:
                    option_el.props('selected')
                self._option_elements[opt] = option_el
                
        def handle_change(e: Any):
            val = e.args.get('target.value', self.value) if isinstance(e.args, dict) else self.value
            self.value = val
            
            for opt, el in self._option_elements.items():
                if opt == val:
                    el.props('selected')
                else:
                    el.props(remove='selected')
            
            if self._on_change_callback:
                self._on_change_callback(val)
                
        self.on('change', handle_change, args=['target.value'])

class Checkbox(TailwindElement):
    def __init__(self, label: str = "", value: bool = False, on_change: Optional[Callable] = None, base_classes: list[str] = None):
        """
        Tailwind Wrapper for a native HTML <input type="checkbox">.
        """
        classes = ['flex', 'items-center', 'cursor-pointer']
        if base_classes:
            classes.extend(base_classes)
        super().__init__('label', classes)
        
        self.value = value
        self._on_change_callback = on_change
        
        from nicegui import ui
        with self:
            self._input = ui.element('input').classes('h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded').props('type="checkbox"')
            if self.value:
                self._input.props('checked')
            ui.element('span').classes('ml-2 block text-sm text-gray-900').set_text(label)
            
        def handle_change(e: Any):
            if e.args and isinstance(e.args, dict) and 'target.checked' in e.args:
                self.value = bool(e.args.get('target.checked'))
            else:
                self.value = not self.value
                
            if self.value:
                self._input.props('checked')
            else:
                self._input.props(remove='checked')
                
            if self._on_change_callback:
                self._on_change_callback(self.value)
                
        self.on('change', handle_change)

class Textarea(TailwindElement):
    def __init__(self, placeholder: str = '', value: str = '', on_change: Optional[Callable] = None, rows: int = 4, base_classes: list[str] = None):
        """
        Custom Tailwind Textarea extending raw HTML <textarea>
        """
        classes = [
            'block', 'w-full', 'px-3', 'py-2', 'border', 'border-gray-300', 'rounded-md', 'shadow-sm', 
            'focus:outline-none', 'focus:border-blue-500', 'focus:ring-1', 'focus:ring-blue-500', 'sm:text-sm'
        ]
        if base_classes:
            classes.extend(base_classes)
            
        super().__init__('textarea', classes)
        
        self.value = value
        self._props['placeholder'] = placeholder
        self._props['rows'] = rows
        self._props['value'] = value
        
        self._on_change_callback = on_change
        
        def handle_input(e: Any):
            val = e.args.get('target.value', '') if isinstance(e.args, dict) else ''
            self.value = val
            self._props['value'] = val
            if self._on_change_callback:
                self._on_change_callback(val)
                
        self.on('input', handle_input, args=['target.value'])
