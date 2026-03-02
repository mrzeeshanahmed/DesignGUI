from .base import TailwindElement
from .primitives import Box, Flex, Stack, Text, Divider
from .inputs import Button, Input, ToggleSwitch
from .display import Icon, Avatar, DropdownMenu

class AuthForm(TailwindElement):
    def __init__(self, title: str = "Sign In", base_classes: list[str] = None):
        """
        Macro Composite Auth Block containing email, password, and sign-in button styled cleanly.
        """
        classes = ['max-w-md', 'w-full', 'bg-white', 'p-8', 'rounded-xl', 'shadow-md', 'border', 'border-gray-100']
        if base_classes:
            classes.extend(base_classes)
        super().__init__('div', classes)
        
        with self:
            with Stack(['w-full', 'space-y-6']).classes('m-0 w-full'):
                
                with Stack(['w-full', 'items-center', 'mb-6']):
                    Text(title, ['text-2xl', 'font-bold', 'text-gray-900'])
                    Text("Enter your credentials to access your account.", ['text-sm', 'text-gray-500', 'mt-2', 'text-center'])
                
                with Stack(['w-full', 'space-y-4']):
                    with Box(['w-full']):
                        Text("Email", ['block', 'text-sm', 'font-medium', 'text-gray-700', 'mb-1'])
                        self.email_input = Input(placeholder="user@example.com", base_classes=['w-full'])
                        
                    with Box(['w-full']):
                        Text("Password", ['block', 'text-sm', 'font-medium', 'text-gray-700', 'mb-1'])
                        self.password_input = Input(placeholder="••••••••", base_classes=['w-full'])
                        self.password_input._props['type'] = 'password'
                    
                    with Flex(['w-full', 'justify-between', 'items-center']):
                        self.remember_toggle = ToggleSwitch("Remember Me")
                        Button("Forgot password?", variant='ghost', base_classes=['text-sm', 'text-blue-600', 'hover:text-blue-500', 'px-0'])
                    
                    self.submit_btn = Button("Sign In", variant='primary', base_classes=['w-full', 'mt-6', 'py-3'])

class StatGrid(TailwindElement):
    def __init__(self, stats: list[dict], base_classes: list[str] = None):
        """
        Responsive grid displaying summary cards containing titles, values, and percentage impacts.
        stats schema: [{'label': 'Users', 'value': '1,200', 'trend': '+12%', 'positive': True}, ...]
        """
        classes = ['grid', 'grid-cols-1', 'md:grid-cols-3', 'gap-6', 'w-full']
        if base_classes:
            classes.extend(base_classes)
        super().__init__('div', classes)
        
        with self:
            for stat in stats:
                with Stack(['bg-white', 'rounded-xl', 'border', 'border-gray-200', 'p-6', 'shadow-sm', 'items-start']):
                    Text(stat.get('label', ''), ['text-sm', 'font-medium', 'text-gray-500'])
                    
                    with Flex(['items-baseline', 'mt-2', 'gap-2']):
                        Text(str(stat.get('value', '')), ['text-3xl', 'font-bold', 'text-gray-900'])
                        
                        trend = stat.get('trend')
                        is_pos = stat.get('positive', True)
                        
                        if trend:
                            color = 'text-green-600' if is_pos else 'text-red-600'
                            bg = 'bg-green-100' if is_pos else 'bg-red-100'
                            with Box(['inline-flex', 'items-baseline', 'px-2', 'py-0.5', 'rounded-full', 'text-sm', 'font-medium', bg, color]):
                                Text(trend)

class EmptyState(TailwindElement):
    def __init__(self, title: str, description: str, icon_name: str = "folder_open", action_text: str = None, base_classes: list[str] = None):
        """
        Standard empty state container with icon, description and action.
        """
        classes = ['flex', 'flex-col', 'items-center', 'justify-center', 'p-12', 'text-center', 'border-2', 'border-dashed', 'border-gray-300', 'rounded-lg', 'bg-gray-50']
        if base_classes:
            classes.extend(base_classes)
        super().__init__('div', classes)
        
        with self:
            Icon(icon_name, size="text-4xl", base_classes=['text-gray-400', 'mb-4'])
            Text(title, ['text-lg', 'font-medium', 'text-gray-900', 'mb-1'])
            Text(description, ['text-sm', 'text-gray-500', 'max-w-sm', 'mb-6'])
            
            if action_text:
                self.action_btn = Button(action_text, variant='primary')

class Stepper(TailwindElement):
    def __init__(self, steps: list[str], current_step: int = 0, base_classes: list[str] = None):
        """
        Horizontal step indicator diagram.
        """
        classes = ['flex', 'items-center', 'w-full', 'max-w-3xl', 'mx-auto', 'my-8']
        if base_classes:
            classes.extend(base_classes)
        super().__init__('div', classes)
        
        with self:
            for i, step_name in enumerate(steps):
                is_active = i == current_step
                is_completed = i < current_step
                
                # Container for step circle and text
                with Stack(['items-center', 'relative', 'z-10']):
                    bg_color = 'bg-blue-600' if is_active or is_completed else 'bg-gray-200'
                    text_color = 'text-white' if is_active or is_completed else 'text-gray-500'
                    
                    with Flex(['w-10', 'h-10', 'rounded-full', bg_color, text_color, 'items-center', 'justify-center', 'font-medium', 'text-sm', 'border-4', 'border-white']):
                        if is_completed:
                            Icon('check', size='text-sm')
                        else:
                            Text(str(i + 1))
                            
                    Text(step_name, ['text-xs', 'font-medium', 'mt-2', 'text-gray-900' if is_active else 'text-gray-500'])

                # Render connector line except for the last item
                if i < len(steps) - 1:
                    line_color = 'bg-blue-600' if is_completed else 'bg-gray-200'
                    with Box(['flex-auto', 'h-1', line_color, '-mt-6', 'mx-2']):
                        pass

class TopNav(TailwindElement):
    def __init__(self, title: str, user_name: str = "User", base_classes: list[str] = None):
        """
        Common application top navigation bar composite.
        """
        classes = ['w-full', 'bg-white', 'border-b', 'border-gray-200', 'h-16', 'flex', 'items-center', 'justify-between', 'px-6', 'shadow-sm']
        if base_classes:
            classes.extend(base_classes)
        super().__init__('nav', classes)
        
        with self:
            with Flex(['items-center', 'gap-4']):
                Text(title, ['text-xl', 'font-bold', 'text-gray-900'])
            
            with Flex(['items-center', 'gap-4']):
                Icon('notifications', base_classes=['text-gray-500', 'hover:text-gray-700', 'cursor-pointer'])
                self.user_dropdown = DropdownMenu(label=user_name, items=["Profile", "Settings", "Log out"])
                Avatar(initials=user_name[:2].upper())

class DataFeed(TailwindElement):
    def __init__(self, items: list[dict], base_classes: list[str] = None):
        """
        Vertical chronological activity feed composite.
        items: [{'title': '...', 'description': '...', 'time': '...', 'icon': '...'}]
        """
        classes = ['w-full', 'relative']
        if base_classes:
            classes.extend(base_classes)
        super().__init__('div', classes)
        
        with self:
            # Vertical timeline line traversing the background
            Box(['absolute', 'top-4', 'bottom-4', 'left-6', 'w-px', 'bg-gray-200', 'z-0'])
            
            with Stack(['space-y-8', 'w-full', 'relative', 'z-10']):
                for item in items:
                    with Flex(['items-start', 'gap-4', 'w-full']):
                        # Icon circle anchor
                        with Flex(['w-12', 'h-12', 'rounded-full', 'bg-blue-100', 'text-blue-600', 'items-center', 'justify-center', 'flex-shrink-0', 'ring-8', 'ring-white']):
                            Icon(item.get('icon', 'bolt'))
                            
                        # Content block
                        with Stack(['flex-1', 'pt-1']):
                            with Flex(['justify-between', 'items-baseline', 'w-full']):
                                Text(item.get('title', ''), ['text-sm', 'font-medium', 'text-gray-900'])
                                Text(item.get('time', ''), ['text-xs', 'text-gray-500'])
                            Text(item.get('description', ''), ['text-sm', 'text-gray-500', 'mt-1'])
