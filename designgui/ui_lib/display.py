import html
import uuid
from typing import Optional, List, Dict
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
    def __init__(self, trigger_text: str = "Menu", items: List[str] = None, base_classes: list[str] = None):
        """
        Floating popover menu attached to a button.
        Uses native HTML details/summary natively styled.
        """
        classes = ['relative', 'inline-block', 'text-left']
        if base_classes:
            classes.extend(base_classes)
        super().__init__('details', classes)
        
        # We manually build the details/summary DOM structure
        _id = f"dropdown-{uuid.uuid4().hex[:6]}"
        
        safe_trigger = html.escape(trigger_text)
        
        list_items = ""
        if items:
            for item in items:
                safe_item = html.escape(item)
                list_items += f'<a href="#" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900" role="menuitem">{safe_item}</a>'
        
        inner_dom = f"""
        <summary class="inline-flex justify-center w-full rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none cursor-pointer list-none appearance-none">
            {safe_trigger}
            <svg class="-mr-1 ml-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
        </summary>
        <div class="origin-top-right absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-50">
            <div class="py-1" role="menu" aria-orientation="vertical" aria-labelledby="options-menu">
                {list_items}
            </div>
        </div>
        """
        
        # Override browser default summary arrow using styles via Tailwind plugins usually, but inline block removes it mostly
        self._props['innerHTML'] = inner_dom
        
        # Adding a bit of CSS to hide the default details marker if Tailwind prose doesn't
        self.style('summary::-webkit-details-marker { display: none; }')

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

class Tabs(TailwindElement):
    def __init__(self, tabs: List[str], base_classes: list[str] = None):
        """
        Horizontal navigation generating a flex row of styled buttons.
        """
        classes = ['flex', 'space-x-4', 'border-b', 'border-gray-200', 'w-full', 'mb-4']
        if base_classes:
            classes.extend(base_classes)
        super().__init__('div', classes)
        
        self._tabs = tabs
        self._active_tab = tabs[0] if tabs else None
        self._panels = {} # Map of tab name to Box container id or panel object
        
        # We'll render internal buttons manually using nicegui components attached as children
        from .inputs import Button
        for tab in tabs:
            is_active = (tab == self._active_tab)
            btn_classes = ['pb-2', 'pt-1', 'border-b-2', 'px-1']
            if is_active:
                btn_classes.extend(['border-blue-500', 'text-blue-600', 'font-medium'])
            else:
                btn_classes.extend(['border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300'])
                
            # NiceGUI container contexts
            with self:
                trigger = Button(text=tab, variant='ghost', base_classes=btn_classes)
                # Note: Binding visibility logic usually requires storing weakrefs or ID mapping to panels
                # We defer panel visibility toggling to outside composites or callback binds

class Accordion(TailwindElement):
    def __init__(self, title: str, content_html: str = "", base_classes: list[str] = None):
        """
        A details and summary HTML tag wrapper.
        """
        classes = ['w-full', 'border-b', 'border-gray-200', 'py-3']
        if base_classes:
            classes.extend(base_classes)
        super().__init__('details', classes)
        
        safe_title = html.escape(title)
        
        inner_dom = f"""
        <summary class="flex justify-between items-center font-medium cursor-pointer list-none text-gray-900 group">
            {safe_title}
            <span class="transition group-open:rotate-180">
                <svg fill="none" height="24" shape-rendering="geometricPrecision" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" viewBox="0 0 24 24" width="24"><path d="M6 9l6 6 6-6"></path></svg>
            </span>
        </summary>
        <div class="text-gray-500 mt-3 group-open:animate-fadeIn">
            {content_html}
        </div>
        """
        
        self._props['innerHTML'] = inner_dom
        self.style('summary::-webkit-details-marker { display: none; }')
