"""Bounded PostgreSQL connection pool, shared by the process, not by transactions."""
import os,hashlib,json,threading,atexit
from contextlib import contextmanager
_pools={};_lock=threading.RLock()
def runtime_key():
    from .db import identity
    # A password change must get a new pool; raw passwords are never used as log keys.
    raw=[identity(),os.environ.get('NEMU_PG_PASSWORD',''),os.environ.get('NEMU_PG_TEST_DSN','')]
    return hashlib.sha256(json.dumps(raw).encode()).hexdigest()
def _configure(conn):
    conn.execute("SET search_path TO nemu, pg_catalog; SET statement_timeout TO '20s'; SET lock_timeout TO '15s'",prepare=False)
    conn.commit()
def get_pool():
    from psycopg_pool import ConnectionPool
    from psycopg.rows import dict_row
    key=runtime_key()
    with _lock:
        if key in _pools:return _pools[key]
        test=os.environ.get('NEMU_PG_TEST_DSN')
        if test:
            if os.environ.get('NEMU_TESTING')!='1':raise RuntimeError('Konfigurasi pengujian tidak diizinkan.')
            conninfo=test;kwargs={}
        else:
            if any(not os.environ.get(k) for k in ['NEMU_PG_HOST','NEMU_PG_USER','NEMU_PG_PASSWORD']):raise RuntimeError('Koneksi aplikasi belum dikonfigurasi lengkap.')
            conninfo='';kwargs=dict(host=os.environ['NEMU_PG_HOST'].strip(),port=int(os.environ.get('NEMU_PG_PORT','5432')),user=os.environ['NEMU_PG_USER'].strip(),password=os.environ['NEMU_PG_PASSWORD'],dbname=os.environ.get('NEMU_PG_DBNAME','postgres'),sslmode='require',connect_timeout=12)
        kwargs.update(row_factory=dict_row,prepare_threshold=None)
        pool=ConnectionPool(conninfo=conninfo,kwargs=kwargs,min_size=1,max_size=4,max_idle=120,max_lifetime=1800,timeout=15,configure=_configure,name='nemu',open=False)
        try:pool.open(wait=True,timeout=15)
        except Exception:
            pool.close();raise RuntimeError('Koneksi layanan data belum tersedia. Coba lagi sebentar atau hubungi admin.') from None
        _pools[key]=pool
        return pool
@contextmanager
def connection():
    from psycopg_pool import PoolTimeout
    from psycopg import OperationalError
    try:
        with get_pool().connection(timeout=15) as conn:yield conn
    except (PoolTimeout,OperationalError):raise RuntimeError('Layanan data sedang sibuk atau koneksi terputus. Silakan coba lagi.') from None
def close_pools():
    with _lock:
        for pool in _pools.values():pool.close()
        _pools.clear()
atexit.register(close_pools)
