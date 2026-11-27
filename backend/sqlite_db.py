"""SQLite lokal; setiap koneksi mengaktifkan FK dan timeout, tulis dalam transaksi."""
import os, sqlite3, json
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
def now(): return datetime.now(timezone.utc).isoformat(timespec='seconds')
def path():
    from .storage_context import demo_path
    return demo_path() or Path(os.environ.get('NEMU_DB_PATH', str(ROOT/'database/nemu.db')))
@contextmanager
def connect(write=False):
    p=path();p.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(p, timeout=20);c.row_factory=sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON');c.execute('PRAGMA busy_timeout=20000')
    try:
        if write:c.execute('BEGIN IMMEDIATE')
        yield c
        c.commit()
    except Exception:
        c.rollback();raise
    finally:c.close()
def init_db():
    with connect() as c:
        c.execute('PRAGMA journal_mode=WAL')
        # Database versi lama tidak ditimpa otomatis.
        tables={r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if 'users' in tables and 'password_hash' not in {r[1] for r in c.execute('PRAGMA table_info(users)')}:
            raise RuntimeError('Database NEMU lama terdeteksi. Gunakan folder baru; baca docs/DATABASE.md.')
        c.executescript((ROOT/'backend/schema.sql').read_text())
    with connect(True) as c:
        if not c.execute('SELECT 1 FROM ukm LIMIT 1').fetchone():
            for p in json.loads((ROOT/'data/ukm_wawancara.json').read_text(encoding='utf-8')):
                c.execute('INSERT INTO ukm(slug,nama,kategori,profil,aktif,updated_at) VALUES(?,?,?,?,?,?)',
                          (p['slug'],p['nama'],p['kategori'],json.dumps(p,ensure_ascii=False),1,now()))
        for key,value in [('bobot',{'minat':40,'bakat':15,'kemampuan':15,'preferensi':20,'komitmen':10}),('periode','2026-2027'),('pendaftaran_buka',True)]:
            c.execute('INSERT OR IGNORE INTO settings VALUES(?,?)',(key,json.dumps(value)))
def setting(c,key):return json.loads(c.execute('SELECT value FROM settings WHERE key=?',(key,)).fetchone()[0])
def club(row):
    p=json.loads(row['profil']);p.update(id=row['id'],slug=row['slug'],nama=row['nama'],kategori=row['kategori'],aktif=bool(row['aktif']));return p
