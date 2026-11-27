"""Explicit SQLite(local) or PostgreSQL(Supabase); no silent fallback on errors."""
import os,json,sqlite3
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
CONFIG_KEYS=['NEMU_DATABASE_MODE','NEMU_PG_HOST','NEMU_PG_PORT','NEMU_PG_USER','NEMU_PG_PASSWORD','NEMU_PG_DBNAME']
def now():return datetime.now(timezone.utc).isoformat(timespec='seconds')
def path():
    from .storage_context import demo_path
    return demo_path() or Path(os.environ.get('NEMU_DB_PATH',str(ROOT/'database/nemu.db')))
def mode():
    from .storage_context import demo_path
    if demo_path():return 'sqlite'
    value=os.environ.get('NEMU_DATABASE_MODE','sqlite').strip().lower()
    if value not in ['sqlite','postgres']:raise RuntimeError('NEMU_DATABASE_MODE harus sqlite atau postgres.')
    return value
def pg_raw():
    try:import psycopg
    except ImportError:raise RuntimeError('Driver PostgreSQL belum terpasang. Pasang requirements.txt versi baru.') from None
    from psycopg.rows import dict_row
    # Only the automated integration test can use a local socket without TLS.
    test_dsn=os.environ.get('NEMU_PG_TEST_DSN')
    if test_dsn:
        if os.environ.get('NEMU_TESTING')!='1':raise RuntimeError('Konfigurasi database pengujian tidak diizinkan.')
        return psycopg.connect(test_dsn,row_factory=dict_row,prepare_threshold=None)
    required=['NEMU_PG_HOST','NEMU_PG_USER','NEMU_PG_PASSWORD']
    if any(not os.environ.get(k) for k in required):raise RuntimeError('Secrets PostgreSQL belum lengkap. Isi HOST, USER, dan PASSWORD.')
    try:port=int(os.environ.get('NEMU_PG_PORT','5432'))
    except ValueError:raise RuntimeError('Port PostgreSQL harus berupa angka.') from None
    try:
        return psycopg.connect(host=os.environ['NEMU_PG_HOST'].strip(),port=port,user=os.environ['NEMU_PG_USER'].strip(),password=os.environ['NEMU_PG_PASSWORD'],dbname=os.environ.get('NEMU_PG_DBNAME','postgres'),sslmode='require',connect_timeout=12,prepare_threshold=None,row_factory=dict_row)
    except psycopg.Error:raise RuntimeError('Koneksi Supabase gagal. Periksa Session pooler, password, port, dan status proyek di Secrets. Tidak dialihkan ke SQLite.') from None
@contextmanager
def connect(write=False):
    from .request_cache import invalidate
    if mode()=='sqlite':
        from .sqlite_db import connect as local
        with local(write) as c:yield c
        if write:invalidate()
        return
    from .postgres import Connection
    from .pool import connection
    with connection() as raw:
        yield Connection(raw,write)
    if write:invalidate()

def init_db():
    if mode()=='sqlite':
        from .sqlite_db import init_db as local_init
        local_init();return
    raw=pg_raw()
    try:
        # Multiple Streamlit sessions may initialize together; serialize schema/seed.
        raw.execute('SELECT pg_advisory_xact_lock(782670040)')
        raw.execute('CREATE SCHEMA IF NOT EXISTS nemu')
        raw.execute('REVOKE ALL ON SCHEMA nemu FROM PUBLIC')
        raw.execute('SET search_path TO nemu, pg_catalog')
        if raw.execute("SELECT to_regclass('nemu.schema_version') AS name").fetchone()['name'] is None:
            raw.execute((ROOT/'backend/schema_postgres.sql').read_text(encoding='utf-8'),prepare=False)
        raw.commit()
    except Exception:
        raw.rollback();raise RuntimeError('Inisialisasi tabel Supabase gagal. Periksa hak akses atau schema database. Data lama tidak dihapus.') from None
    finally:raw.close()
    with connect(True) as c:
        c.execute('SELECT pg_advisory_xact_lock(782670040)')
        if not c.execute('SELECT 1 FROM ukm LIMIT 1').fetchone():
            for p in json.loads((ROOT/'data/ukm_wawancara.json').read_text(encoding='utf-8')):
                c.execute('INSERT INTO ukm(slug,nama,kategori,profil,aktif,updated_at) VALUES(?,?,?,?,?,?)',(p['slug'],p['nama'],p['kategori'],json.dumps(p,ensure_ascii=False),1,now()))
        for k,v in [('bobot',{'minat':40,'bakat':15,'kemampuan':15,'preferensi':20,'komitmen':10}),('periode','2026-2027'),('pendaftaran_buka',True)]:c.execute('INSERT OR IGNORE INTO settings VALUES(?,?)',(k,json.dumps(v)))
def setting(c,key):return json.loads(c.execute('SELECT value FROM settings WHERE key=?',(key,)).fetchone()[0])
def club(row):
    p=json.loads(row['profil']);p.update(id=row['id'],slug=row['slug'],nama=row['nama'],kategori=row['kategori'],aktif=bool(row['aktif']));return p

def identity():
    import hashlib
    fields=[mode(),str(path())] if mode()=='sqlite' else [mode(),os.environ.get('NEMU_PG_HOST',''),os.environ.get('NEMU_PG_PORT','5432'),os.environ.get('NEMU_PG_USER',''),os.environ.get('NEMU_PG_DBNAME','postgres')]
    return hashlib.sha256(json.dumps(fields).encode()).hexdigest()
