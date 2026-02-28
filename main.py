from nicegui import ui
from nice_design.ui_lib.primitives import Box, Flex, Stack, Container, Text, Divider
from nice_design.ui_lib.inputs import Button, Input

# Note: We still import `ui` to call ui.run(), but we DO NOT use ui.label, ui.button, etc.
# unless it's strictly for page setup/app structure.

@ui.page('/')
def index():
    # Setup standard full screen container
    ui.add_head_html('<script src="https://cdn.tailwindcss.com"></script>') # Ensure Tailwind is loaded if not auto
    
    # We must suppress quasar default body padding maybe, though nicegui handles some of it
    ui.query('body').classes('p-0 m-0 bg-gray-50')
    
    with Container(['py-10', 'px-4']):
        
        with Stack(['gap-8']):
            Text('Nice Design OS - component tests', ['text-3xl', 'font-bold', 'text-gray-900'])
            
            Divider()
            
            with Stack(['gap-4', 'bg-white', 'p-6', 'rounded-lg', 'shadow']):
                Text('Typography & Primitives', ['text-xl', 'font-semibold', 'text-gray-800'])
                
                with Flex(['gap-4', 'items-center']):
                    Box(['w-16', 'h-16', 'bg-red-500', 'rounded'])
                    Box(['w-16', 'h-16', 'bg-blue-500', 'rounded-full'])
                    Box(['w-16', 'h-16', 'bg-green-500', 'shadow-lg'])
            
            with Stack(['gap-4', 'bg-white', 'p-6', 'rounded-lg', 'shadow']):
                Text('Buttons (No Quasar)', ['text-xl', 'font-semibold', 'text-gray-800'])
                
                with Flex(['gap-4']):
                    Button('Primary Button', variant='primary', on_click=lambda: (print('PRIMARY CLICKED', flush=True), ui.notify('Primary Clicked!')))
                    Button('Ghost Button', variant='ghost', on_click=lambda: (print('GHOST CLICKED', flush=True), ui.notify('Ghost Clicked!')))
                    Button('Outline Button', variant='outline', on_click=lambda: (print('OUTLINE CLICKED', flush=True), ui.notify('Outline Clicked!')))
                    
            with Stack(['gap-4', 'bg-white', 'p-6', 'rounded-lg', 'shadow']):
                Text('Inputs & Forms', ['text-xl', 'font-semibold', 'text-gray-800'])
                
                class State:
                    name = ""
                    
                state = State()
                
                def on_input_change(v):
                    print(f'INPUT CHANGED: {v}', flush=True)
                    ui.notify(f'Input changed: {v}')

                Input('Enter your name...', on_change=on_input_change).bind_value_to(state, 'name')
                
                # Check if state binds
                with Flex(['gap-2', 'items-center']):
                    Button('Show State', variant='outline', on_click=lambda: (print(f'STATE IS: {state.name}', flush=True), ui.notify(f'Current state: {state.name}')))

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title='Nice Design OS - Test', port=8080, reload=False)
