"""Cache limited to one script render; never shared between user sessions."""
from contextvars import ContextVar
from contextlib import contextmanager
from functools import wraps
from copy import deepcopy
_cache=ContextVar('nemu_request_cache',default=None)
@contextmanager
def request_scope():
    token=_cache.set({})
    try:yield
    finally:_cache.reset(token)
def invalidate():
    cache=_cache.get()
    if cache is not None:cache.clear()
def cached_read(fn):
    @wraps(fn)
    def wrapped(*args,**kwargs):
        cache=_cache.get()
        if cache is None:return fn(*args,**kwargs)
        key=(fn.__module__,fn.__name__,args,tuple(sorted(kwargs.items())))
        if key not in cache:cache[key]=deepcopy(fn(*args,**kwargs))
        return deepcopy(cache[key])
    return wrapped
