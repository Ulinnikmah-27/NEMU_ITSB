import os
from .db import connect
from .auth import create_user

def bootstrap_env():
    username=os.environ.get('NEMU_ADMIN_USERNAME');password=os.environ.get('NEMU_ADMIN_PASSWORD')
    if not username or not password:return
    with connect(True) as c:
        if getattr(c,'is_postgres',False):c.execute('SELECT pg_advisory_xact_lock(782670041)')
        if not c.execute("SELECT 1 FROM users WHERE role='admin'").fetchone():create_user(c,username,password,'Admin NEMU','admin')
