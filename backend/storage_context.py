"""Request-local database selection. Never changes process environment variables."""
from contextvars import ContextVar
_demo_path = ContextVar('nemu_demo_path', default=None)
def demo_path():return _demo_path.get()
