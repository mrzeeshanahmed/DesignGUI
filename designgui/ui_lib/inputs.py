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
        
        # HTML DOM construction using relative grouping
        # The actual input is hidden, the div is styled based on peer-checked
        self._input_id = f"toggle-{id(self)}"
        
        def render_dom():
            checked_attr = 'checked' if self.value else ''
            safe_label = html.escape(label)
            
            dom = f"""
            <div class="relative">
                <input type="checkbox" id="{self._input_id}" class="sr-only peer" {checked_attr}>
                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </div>
            <span class="ml-3 text-sm font-medium text-gray-900">{safe_label}</span>
            """
            self._props['innerHTML'] = dom
            
        self.render_dom = render_dom # Make render_dom an instance method
        self.render_dom()
        
        # We need to bind to the change event of the native checkbox inside the label
        # NiceGUI captures events bubbling up to the wrapper label element natively
        def handle_change(e: Any):
            # Read the raw DOM checked state primarily, falling back to python inversion securely
            if e.args and isinstance(e.args, dict) and 'target.checked' in e.args:
                self.value = bool(e.args.get('target.checked'))
            else:
                self.value = not self.value
                
            self.render_dom()
            self.update()
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
            val = float(e.args.get('target.value', self.value)) if isinstance(e.args, dict) else float(e.args)
            self.value = val
            self._props['value'] = val
            if self._on_change_callback:
                self._on_change_callback(val)
                
        self.on('input', handle_input, args=['target.value'])

class RadioGroup(TailwindElement):
    def __init__(self, options: List[str], value: str, name: str = "radio-group", on_change: Optional[Callable] = None, base_classes: list[str] = None):
        """
        Tailwind Wrapper for a group of radio buttons.
        """
        classes = ['flex', 'flex-col', 'space-y-2']
        if base_classes:
            classes.extend(base_classes)
        super().__init__('div', classes)
        
        self.value = value
        self.options = options
        self._name = name
        self._on_change_callback = on_change
        
        def render_dom():
            dom = ""
            for opt in self.options:
                safe_opt = html.escape(opt)
                checked = 'checked' if opt == self.value else ''
                dom += f"""
                <div class="flex items-center">
                    <input type="radio" value="{safe_opt}" name="{self._name}" class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500" {checked}>
                    <label class="ml-2 text-sm font-medium text-gray-900">{safe_opt}</label>
                </div>
                """
            self._props['innerHTML'] = dom
            
        render_dom()
        
        def handle_change(e: Any):
            # Target value bubbling from radio click
            val = e.args.get('target.value', self.value) if isinstance(e.args, dict) else self.value
            self.value = val
            render_dom()
            self.update()
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
        
        def render_dom():
            dom = ""
            for opt in self.options:
                safe_opt = html.escape(opt)
                selected = 'selected' if opt == self.value else ''
                dom += f'<option value="{safe_opt}" {selected}>{safe_opt}</option>'
            self._props['innerHTML'] = dom
            
        render_dom()
        
        def handle_change(e: Any):
            val = e.args.get('target.value', self.value) if isinstance(e.args, dict) else self.value
            self.value = val
            render_dom()
            self.update()
            if self._on_change_callback:
                self._on_change_callback(val)
                
        self.on('change', handle_change, args=['target.value'])

class Checkbox(TailwindElement):
    def __init__(self, label: str = "", value: bool = False, on_change: Optional[Callable] = None, base_classes: list[str] = None):
        """
        Tailwind Wrapper for a native HTML <input type="checkbox">.
        """
        classes = ['flex', 'items-center']
        if base_classes:
            classes.extend(base_classes)
        super().__init__('div', classes)
        
        self.value = value
        self._on_change_callback = on_change
        
        def render_dom():
            checked_attr = 'checked' if self.value else ''
            safe_label = html.escape(label)
            dom = f"""
            <input type="checkbox" class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded" {checked_attr}>
            <label class="ml-2 block text-sm text-gray-900">{safe_label}</label>
            """
            self._props['innerHTML'] = dom
            
        render_dom()
        
        def handle_change(e: Any):
            if e.args and isinstance(e.args, dict) and 'target.checked' in e.args:
                self.value = bool(e.args.get('target.checked'))
            else:
                self.value = not self.value
                
            render_dom()
            self.update()
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
