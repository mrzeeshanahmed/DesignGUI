import html
from typing import Optional, List, Dict
from nicegui import ui
from .base import TailwindElement

class Image(TailwindElement):
    def __init__(self, src: str, alt: str = "", base_classes: list[str] = None):
        """
        Tailwind Wrapper for native <img> tag.
        """
        classes = ['max-w-full', 'h-auto', 'object-cover', 'rounded']
        if base_classes:
            classes.extend(base_classes)
        super().__init__('img', classes)
        self._props['src'] = src
        self._props['alt'] = html.escape(alt)

class Icon(TailwindElement):
    def __init__(self, name: str, size: str = "w-6 h-6", base_classes: list[str] = None):
        """
        Tailwind Wrapper for material-icons or SVGs using span tags.
        Assumes material icons are embedded or can map to raw SVG classes.
        """
        classes = ['material-icons', size, 'flex-shrink-0']
        if base_classes:
            classes.extend(base_classes)
        super().__init__('span', classes)
        self._props['innerHTML'] = html.escape(name)

class Avatar(TailwindElement):
    def __init__(self, initials: str = "US", src: Optional[str] = None, base_classes: list[str] = None):
        """
        Image wrapper with a text fallback for user initials.
        """
        classes = ['inline-flex', 'items-center', 'justify-center', 'w-10', 'h-10', 'rounded-full', 'bg-gray-200', 'text-gray-600', 'font-medium', 'overflow-hidden']
        if base_classes:
            classes.extend(base_classes)
        
        super().__init__('div', classes)
        
        if src:
            # Inject an image innerly
            img_html = f'<img src="{html.escape(src)}" alt="{html.escape(initials)}" class="w-full h-full object-cover">'
            self._props['innerHTML'] = img_html
        else:
            self._props['innerHTML'] = html.escape(initials)

class DropdownMenu(TailwindElement):
    """
    A floating popover menu triggered by a click.
    Takes a label and a list of item strings.
    """
    def __init__(self, label: str, items: list, on_select=None):
        super().__init__('div')
        self.label = label
        self.items = items
        self.on_select = on_select
        self.classes('relative inline-block text-left group')
        self.render_dom()
        
    def render_dom(self):
        # The trigger button (always visible)
        with self:
            trigger_btn = TailwindElement('button').classes(
                'inline-flex justify-center w-full rounded-md border border-gray-300 '
                'shadow-sm px-4 py-2 bg-white text-sm font-medium text-gray-700 '
                'hover:bg-gray-50 focus:outline-none'
            ).props('type="button"')
            trigger_btn._props['innerHTML'] = html.escape(self.label)
            trigger_btn.on('click', lambda: self._toggle_menu())
            
            # The dropdown content (hidden by default, shown on group hover/click)
            self._menu_container = TailwindElement('div').classes(
                'hidden group-hover:block absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-50'
            )
            
            with self._menu_container:
                # Loop through items and create clickable native `a` tags
                menu_list = TailwindElement('div').classes('py-1').props('role="menu"')
                with menu_list:
                    for item in self.items:
                        def create_handler(i):
                            return lambda _: self._handle_select(i)
                        
                        a_tag = TailwindElement('a').classes(
                            'block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900 cursor-pointer'
                        )
                        # We use innerHTML prop securely just for the text payload
                        a_tag._props['innerHTML'] = html.escape(item)
                        a_tag.on('click', create_handler(item))

    def _toggle_menu(self):
        # Toggle menu visibility for both hover (desktop) and click (touch/mobile)
        self._menu_visible = not getattr(self, '_menu_visible', False)
        if self._menu_visible:
            self._menu_container.classes(remove='hidden')
        else:
            self._menu_container.classes('hidden')

    def _handle_select(self, item: str):
        if self.on_select:
            self.on_select(item)
        # Optional check: we could force hide the menu here by manipulating classes

class Table(TailwindElement):
    def __init__(self, columns: List[str], rows: List[Dict[str, str]], base_classes: list[str] = None):
        """
        Tailwind-styled data table bypassing Quasar's q-table.
        """
        classes = ['min-w-full', 'divide-y', 'divide-gray-200', 'border', 'border-gray-200', 'rounded-lg', 'overflow-hidden']
        if base_classes:
            classes.extend(base_classes)
        super().__init__('table', classes)
        
        thead_cols = ""
        for col in columns:
            thead_cols += f'<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50">{html.escape(col)}</th>'
            
        tbody_rows = ""
        for row in rows:
            tbody_rows += '<tr class="bg-white hover:bg-gray-50">'
            for col in columns:
                val = str(row.get(col, ""))
                tbody_rows += f'<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{html.escape(val)}</td>'
            tbody_rows += '</tr>'
            
        inner_dom = f"""
        <thead class="bg-gray-50">
            <tr>
                {thead_cols}
            </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
            {tbody_rows}
        </tbody>
        """
        
        self._props['innerHTML'] = inner_dom

class TabPanel(TailwindElement):
    """Container for individual tab content."""
    def __init__(self, name: str):
        super().__init__('div')
        self.name = name
        self.classes('w-full py-4')

class Tabs(TailwindElement):
    """
    State-managed horizontal navigation tabs toggling connected TabPanels.
    """
    def __init__(self, tabs: list[str], default_tab: str = None):
        super().__init__('div')
        self.classes('w-full')
        self.tabs = tabs
        self.active_tab = default_tab if default_tab else (tabs[0] if tabs else None)
        self.panels = {} # Maps name -> TabPanel
        self.tab_buttons = {} # Maps name -> Button element
        self.render_dom()
        
    def add_panel(self, panel: TabPanel):
        """Register a panel and update its initial visibility."""
        self.panels[panel.name] = panel
        if panel.name != self.active_tab:
            panel.classes('hidden')
            
    def render_dom(self):
        with self:
            nav_container = TailwindElement('nav').classes('flex space-x-4 border-b border-gray-200 w-full mb-4')
            with nav_container:
                for tab in self.tabs:
                    def create_handler(t):
                        return lambda _: self.set_tab(t)
                        
                    btn = TailwindElement('button').classes(
                        'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm focus:outline-none transition-colors duration-200'
                    ).props('type="button"')
                    btn._props['innerHTML'] = html.escape(tab)
                    btn.on('click', create_handler(tab))
                    
                    self.tab_buttons[tab] = btn
                    
        self._update_styles()
        
    def set_tab(self, tab_name: str):
        if tab_name == self.active_tab:
            return
        self.active_tab = tab_name
        self._update_styles()
        
        # Toggle panels explicitly
        for name, panel in self.panels.items():
            if name == tab_name:
                panel.classes(remove='hidden')
            else:
                panel.classes('hidden')
                
    def _update_styles(self):
        for name, btn in self.tab_buttons.items():
            if name == self.active_tab:
                btn.classes('border-indigo-500 text-indigo-600', remove='border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300')
            else:
                btn.classes('border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300', remove='border-indigo-500 text-indigo-600')

class Accordion(TailwindElement):
    """
    A collapsible section wrapping native HTML details/summary elements.
    Accepts rich content_html.
    """
    def __init__(self, title: str, content_html: str, safe_html: bool = False):
        super().__init__('details')
        self.title = title
        self.content_html = content_html
        self.safe_html = safe_html
        
        self.classes('group border-b border-gray-200 py-4')
        self.render_dom()
        
    def render_dom(self):
        processed_html = self.content_html if self.safe_html else html.escape(self.content_html)
        inner_dom = f"""
        <summary class="flex justify-between items-center font-medium cursor-pointer list-none text-gray-900">
            <span>{html.escape(self.title)}</span>
            <span class="transition group-open:rotate-180">
                <svg fill="none" height="24" shape-rendering="geometricPrecision" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" viewBox="0 0 24 24" width="24"><path d="M6 9l6 6 6-6"></path></svg>
            </span>
        </summary>
        <div class="text-gray-500 mt-3 hidden group-open:block">
            {processed_html}
        </div>
        """
        self._props['innerHTML'] = inner_dom
        self.update()

class Card(TailwindElement):
    def __init__(self, base_classes: list[str] = None):
        """
        A rounded, bordered Box container commonly used for grouping content.
        """
        classes = ['bg-white', 'overflow-hidden', 'shadow', 'rounded-lg', 'border', 'border-gray-200']
        if base_classes:
            classes.extend(base_classes)
        super().__init__('div', classes)

class Badge(TailwindElement):
    def __init__(self, text: str, variant: str = 'primary', base_classes: list[str] = None):
        """
        A minimal pill-shaped container for statuses or tags.
        """
        classes = ['inline-flex', 'items-center', 'px-2.5', 'py-0.5', 'rounded-full', 'text-xs', 'font-medium']
        if base_classes:
            classes.extend(base_classes)
        super().__init__('span', classes)
        
        self._props['innerHTML'] = html.escape(str(text))
        
        variants = {
            'primary': 'bg-blue-100 text-blue-800',
            'success': 'bg-green-100 text-green-800',
            'warning': 'bg-yellow-100 text-yellow-800',
            'danger': 'bg-red-100 text-red-800',
            'gray': 'bg-gray-100 text-gray-800',
        }
        self.apply_variant(variants, variant)



class Modal(TailwindElement):
    def __init__(self, title: str = "Dialog", on_close=None, base_classes: list[str] = None):
        """
        A Tailwind wrapper bridging NiceGUI's native dialog functions.
        Uses ui.dialog as the root base natively supporting open/close.
        """
        classes = ['fixed', 'inset-0', 'z-50', 'flex', 'items-center', 'justify-center', 'bg-black', 'bg-opacity-50', 'hidden']
        if base_classes:
            classes.extend(base_classes)
        super().__init__('div', classes)
        
        self.is_open = False
        self.on_close = on_close
        
        from .primitives import Box, Flex, Text
        from .inputs import Button
        
        with self:
            with Box(['bg-white', 'rounded-xl', 'shadow-2xl', 'w-full', 'max-w-md', 'overflow-hidden', 'transform', 'transition-all', 'flex', 'flex-col']).on('click', lambda: None, js_handler='event.stopPropagation()'):
                with Flex(['w-full', 'justify-between', 'items-center', 'px-6', 'py-4', 'border-b', 'border-gray-200']):
                    Text(title, ['text-lg', 'font-medium', 'text-gray-900']).classes('m-0')
                    close_btn = Button('X', variant='ghost', base_classes=['text-gray-400', 'hover:text-gray-500', 'p-1', 'm-0'])
                    close_btn.on('click', self.close)
                
                self.content_area = Box(['p-6'])
        
        self.on('click', self.close)

    def open(self):
        self.is_open = True
        self.classes(remove='hidden')
        return self

    def close(self):
        self.is_open = False
        self.classes('hidden')
        if self.on_close:
            self.on_close()

    def __enter__(self):
        return self.content_area.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.content_area.__exit__(exc_type, exc_val, exc_tb)
