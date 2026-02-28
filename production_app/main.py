from nicegui import ui

# Import your shell and views dynamically built by the AI
from product.views.dashboard import render_view

# Example: If you had a shell layout
# from product.shell import AppLayout 
# @ui.page('/')
# def index():
#     with AppLayout():
#         render_view()

@ui.page('/')
def index():
    render_view()

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title='Production App', port=8000)
