import html
import uuid
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
            classes.append('rounded-full')
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
        
        bg_colors = {
            'success': 'bg-green-500',
            'error': 'bg-red-500',
            'warning': 'bg-yellow-500',
            'info': 'bg-blue-500'
        }
        
        color_class = bg_colors.get(type, 'bg-gray-800')
        
        # Override the quasar default classes by injecting tailwind natively 
        # NiceGUI notify supports some kwargs but we must use styling overrides
        ui.notify(
            message=safe_msg,
            timeout=duration_ms,
            html=True,
            classes=f'{color_class} text-white font-medium p-4 rounded-md shadow-lg',
            position='bottom'
        )
