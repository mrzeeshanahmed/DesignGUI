from .base import TailwindElement

class Box(TailwindElement):
    def __init__(self, base_classes: list[str] = None):
        super().__init__('div', base_classes)

class Flex(TailwindElement):
    def __init__(self, base_classes: list[str] = None):
        classes = ['flex', 'flex-row']
        if base_classes:
            classes.extend(base_classes)
        super().__init__('div', classes)

class Stack(TailwindElement):
    def __init__(self, base_classes: list[str] = None):
        classes = ['flex', 'flex-col']
        if base_classes:
            classes.extend(base_classes)
        super().__init__('div', classes)

class Container(TailwindElement):
    def __init__(self, base_classes: list[str] = None):
        classes = ['container', 'mx-auto']
        if base_classes:
            classes.extend(base_classes)
        super().__init__('div', classes)

class Text(TailwindElement):
    def __init__(self, text: str = '', base_classes: list[str] = None):
        super().__init__('span', base_classes)
        self._text = text
        self._props['innerHTML'] = text

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = str(value)
        self._props['innerHTML'] = self._text
        self.update()

class Divider(TailwindElement):
    def __init__(self, base_classes: list[str] = None):
        classes = ['w-full', 'h-px', 'bg-gray-200']
        if base_classes:
            classes.extend(base_classes)
        super().__init__('div', classes)
