import html
from .base import TailwindElement
from nicegui import ui

class Skeleton(TailwindElement):
    def __init__(self, shape: str = 'rect', base_classes: list[str] = None):
        """
        Loading placeholder skeleton blocks.
        Shapes: 'rect', 'circle', 'text'
        """
        classes = ['animate-pulse', 'bg-gray-200']
        
        if shape == 'circle':
            classes.extend(['rounded-full', 'w-10', 'h-10'])
        elif shape == 'text':
            classes.extend(['h-4', 'rounded', 'w-3/4'])
        else:
            classes.extend(['h-32', 'rounded-md', 'w-full'])
            
        if base_classes:
            classes.extend(base_classes)
            
        super().__init__('div', classes)

class Spinner(TailwindElement):
    def __init__(self, size: str = 'w-8 h-8', border_width: str = 'border-4', color: str = 'border-blue-500', base_classes: list[str] = None):
        """
        Animated CSS spinner ring bypassing Quasar spinner element.
        """
        classes = ['inline-block', 'rounded-full', 'animate-spin', 'border-solid', 'border-t-transparent', size, border_width, color]
        if base_classes:
            classes.extend(base_classes)
            
        super().__init__('div', classes)

class Toast:
    @staticmethod
    def show(message: str, type: str = 'info', duration_ms: int = 3000):
        """
        Imperative Toast leveraging standard nicegui notify but with custom styling via HTML.
        """
        safe_msg = html.escape(message)
        
        # NiceGUI notify wraps Quasar directly.
        # Ensure we map tailwind semantic hex strings securely rather than class strings breaking QNotify.
        color_map = {
            'info': '#3b82f6',     # blue-500
            'success': '#22c55e',  # green-500
            'warning': '#f59e0b',  # amber-500
            'error': '#ef4444'     # red-500
        }
        hex_color = color_map.get(type, '#374151') # gray-700 fallback
        
        ui.notify(
            message=safe_msg,
            timeout=duration_ms,
            color=hex_color,
            position='bottom'
        )
