"""
Nice Design OS
"""
import importlib.metadata

try:
    __version__ = importlib.metadata.version("designgui")
except Exception:
    __version__ = "unknown"

