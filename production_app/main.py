from nicegui import ui

# Dynamically import the AI generated view.
from product.views.dashboard import render_view

@ui.page('/')
def index():
    render_view()

if __name__ in {"__main__", "__mp_main__"}:
    # Reload and show are FALSE for production edge/headless optimization
    ui.run(title='Production App', host='127.0.0.1', port=9000, reload=False, show=False)
