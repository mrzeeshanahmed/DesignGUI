import html
from .base import TailwindElement

class Sidebar(TailwindElement):
    def __init__(self, base_classes: list[str] = None):
        """
        A collapsible left navigation rail or expanded menu.
        """
        classes = ['h-screen', 'fixed', 'top-0', 'left-0', 'bg-white', 'border-r', 'border-gray-200', 'w-64', 'flex', 'flex-col', 'z-40']
        if base_classes:
            classes.extend(base_classes)
        super().__init__('aside', classes)

class Header(TailwindElement):
    def __init__(self, base_classes: list[str] = None):
        """
        A sticky top navigation bar.
        """
        classes = ['w-full', 'bg-white', 'border-b', 'border-gray-200', 'h-16', 'flex', 'items-center', 'px-4', 'sticky', 'top-0', 'z-30']
        if base_classes:
            classes.extend(base_classes)
        super().__init__('header', classes)

class Sheet(TailwindElement):
    def __init__(self, title: str = "Details", base_classes: list[str] = None):
        """
        A side-panel that slides in from the right edge of the screen.
        """
        classes = ['fixed', 'inset-y-0', 'right-0', 'w-96', 'bg-white', 'shadow-2xl', 'transform', 'transition-transform', 'duration-300', 'translate-x-full', 'z-50', 'flex', 'flex-col']
        if base_classes:
            classes.extend(base_classes)
        super().__init__('div', classes)
        
        self.is_open = False
        self._title = html.escape(title)
        
        header_dom = f"""
        <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h2 class="text-lg font-medium text-gray-900">{self._title}</h2>
            <button class="text-gray-400 hover:text-gray-500 focus:outline-none" onclick="this.parentElement.parentElement.classList.add('translate-x-full')">
                <span class="sr-only">Close panel</span>
                <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>
        </div>
        """
        
        # In strictly composable NiceGUI, the child elements injected over DOM innerHTML require specific targeting
        # Since NiceGUI adds children to the root tag, rendering inline static HTML headers directly works 
        # only if content goes into a slot OR if we let users inject into the container natively
        # To keep it simple, we don't mix innerHTML with nicegui children directly, we append children normally.
        
        from .primitives import Box, Flex, Text
        from .inputs import Button
        
        with self:
            with Flex(['w-full', 'justify-between', 'items-center', 'px-6', 'py-4', 'border-b', 'border-gray-200']):
                Text(self._title, ['text-lg', 'font-medium', 'text-gray-900']).classes('m-0')
                close_btn = Button('X', variant='ghost', base_classes=['text-gray-400', 'hover:text-gray-500', 'p-1', 'm-0'])
                close_btn.on('click', self.close)
            
            # Sub-container for consumer elements
            self.content_area = Box(['flex-1', 'overflow-y-auto', 'p-6'])
            
    def open(self):
        self.is_open = True
        self.classes(remove='translate-x-full')
        return self

    def close(self):
        self.is_open = False
        self.classes('translate-x-full')
        return self
        
    def __enter__(self):
        """Override standard NiceGUI context execution pointing nested children directly into content_area"""
        return self.content_area.__enter__()
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.content_area.__exit__(exc_type, exc_val, exc_tb)
        
    def default_slot(self):
        # When users use `with sheet:`, redirect elements into the content_area
        return self.content_area
