"""Admin-only consistent SQLite snapshot and a write freeze for cutover."""
import sqlite3,tempfile,json
from pathlib import Path
from .db import connect
from .auth import require,verify_password,AppError
TABLES=['users','ukm','kuesioner','rekomendasi','pendaftaran','hasil_seleksi','assets']
FLAG='migration_freeze'
def is_frozen():
    with connect() as c:
        if getattr(c,'is_postgres',False):return False
        r=c.execute('SELECT value FROM settings WHERE key=?',(FLAG,)).fetchone()
        return bool(json.loads(r[0])) if r else False
def _verify(c,actor,password):
    u=require(c,actor,['admin'])
    if not verify_password(password,u['password_hash']):raise AppError('Password admin tidak sesuai.')
    return u
def freeze_snapshot(actor,password):
    with connect(True) as c:
        if getattr(c,'is_postgres',False):raise AppError('Database sudah PostgreSQL. Gunakan pg_dump untuk backup penuh.')
        _verify(c,actor,password)
        # A single SQLite write transaction waits for earlier writes, then protects later writes with triggers.
        for table in TABLES:
            for operation in ['INSERT','UPDATE','DELETE']:
                c.execute(f'''CREATE TRIGGER IF NOT EXISTS nemu_freeze_{table}_{operation.lower()} BEFORE {operation} ON {table}
                    WHEN EXISTS(SELECT 1 FROM settings WHERE key='migration_freeze' AND value='true')
                    BEGIN SELECT RAISE(ABORT,'Pendaftaran ditutup sementara untuk pemindahan database.'); END''')
        for operation in ['UPDATE','DELETE']:
            c.execute(f"""CREATE TRIGGER IF NOT EXISTS nemu_freeze_settings_{operation.lower()} BEFORE {operation} ON settings
                WHEN OLD.key!='migration_freeze' AND EXISTS(SELECT 1 FROM settings WHERE key='migration_freeze' AND value='true')
                BEGIN SELECT RAISE(ABORT,'Pengaturan dibekukan selama migrasi.'); END""")
        c.execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(FLAG,'true'))
    with tempfile.TemporaryDirectory() as directory:
        target=Path(directory)/'snapshot.db'
        with connect() as source:
            _verify(source,actor,password)
            dest=sqlite3.connect(target)
            try:source.backup(dest)
            finally:dest.close()
        with sqlite3.connect(target) as check:
            if check.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise AppError('Pemeriksaan backup gagal. Unduh ulang sebelum melanjutkan.')
            counts={t:check.execute('SELECT count(*) FROM '+t).fetchone()[0] for t in TABLES}
        return target.read_bytes(),counts
def resume(actor,password):
    with connect(True) as c:
        if getattr(c,'is_postgres',False):raise AppError('Database sudah PostgreSQL.')
        _verify(c,actor,password)
        c.execute('UPDATE settings SET value=? WHERE key=?',('false',FLAG))
