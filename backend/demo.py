"""Authenticated teacher's private, ephemeral workspace; no production role elevation."""
import atexit,secrets,tempfile,threading,time,os
from pathlib import Path
from contextlib import contextmanager
from .storage_context import _demo_path,demo_path
from .auth import AppError
_registry={};_lock=threading.RLock();TTL=8*3600

def allowed(user):
    return bool(user and user.get('aktif') and user.get('role')=='mahasiswa' and user.get('username')==os.environ.get('NEMU_DEMO_USERNAME','dosen_nemu'))

def _authorize(real_actor):
    if demo_path():raise AppError('Ruang demo tidak boleh dibuat dari sesi demo lain.')
    from .auth import current
    user=current(real_actor)
    if not allowed(user):raise AppError('Akun ini tidak memiliki akses mode penilaian.')
    return user

def _seed():
    from .db import init_db,connect
    from .auth import create_user
    from .service import save_answers,register_clubs,decide
    init_db()
    with connect(True) as c:
        admin=create_user(c,'demo_admin','LatihanNEMU2026!','Admin Demo','admin')
        student=create_user(c,'demo_mahasiswa','LatihanNEMU2026!','Mahasiswa Demo','mahasiswa',nim='DEMO001',prodi='Sains Data',angkatan='2025')
        other=create_user(c,'demo_pendaftar','LatihanNEMU2026!','Pendaftar Contoh','mahasiswa',nim='DEMO002',prodi='Bisnis Digital',angkatan='2025')
        ukm=c.execute('SELECT id FROM ukm ORDER BY id LIMIT 1').fetchone()['id']
        manager=create_user(c,'demo_pengurus','LatihanNEMU2026!','Pengurus Demo','pengurus',ukm_id=ukm)
        c.execute("UPDATE settings SET value=? WHERE key='periode'",('"DEMO-2026"',))
    answer=dict(semester=3,minat=['olahraga'],bakat=['kerja sama'],kemampuan=['futsal'],tingkat='Pemula',pola='kelompok',lokasi='keduanya',komitmen='tinggi')
    for who in [student,other]:
        save_answers(who,answer);register_clubs(who,[ukm])
    with connect() as c:rid=c.execute('SELECT id FROM pendaftaran WHERE user_id=?',(other,)).fetchone()['id']
    decide(admin,rid,'Diterima','Contoh hasil seleksi untuk demonstrasi.')
    return {'admin':admin,'mahasiswa':student,'pengurus':manager}

def _new(owner):
    with _lock:
        now=time.time()
        for key,w in list(_registry.items()):
            if now-w['touched']>TTL and not w['in_use']:
                w['temp'].cleanup();del _registry[key]
        if len(_registry)>=64:raise AppError('Ruang demo sedang penuh. Coba lagi nanti.')
        temp=tempfile.TemporaryDirectory(prefix='nemu_demo_')
        token=secrets.token_urlsafe(32);p=Path(temp.name)/'demo.db'
        scope=_demo_path.set(p)
        try:
            from .request_cache import request_scope
            with request_scope():actors=_seed()
        except Exception:temp.cleanup();raise
        finally:_demo_path.reset(scope)
        _registry[token]=dict(owner=owner,temp=temp,path=p,actors=actors,touched=now,in_use=0)
        return token

def get_token(real_actor,token=None):
    _authorize(real_actor)
    with _lock:
        if token in _registry and _registry[token]['owner']==real_actor:return token
        if token in _registry:raise AppError('Ruang demo bukan milik sesi ini.')
    return _new(real_actor)

@contextmanager
def workspace(real_actor,token):
    _authorize(real_actor)
    with _lock:
        w=_registry.get(token)
        if not w or w['owner']!=real_actor:raise AppError('Ruang demo sudah berakhir. Silakan masuk kembali.')
        w['touched']=time.time();w['in_use']+=1
    scope=_demo_path.set(w['path'])
    from .request_cache import request_scope
    try:
        with request_scope():yield w['actors']
    finally:
        _demo_path.reset(scope)
        with _lock:w['in_use']-=1

def reset(real_actor,token):
    _authorize(real_actor)
    with _lock:
        w=_registry.get(token)
        if w and w['owner']!=real_actor:raise AppError('Ruang demo bukan milik sesi ini.')
        if w:
            if w['in_use']:raise AppError('Ruang demo masih digunakan. Coba kembali.')
            w['temp'].cleanup();del _registry[token]
    return _new(real_actor)

def close_all():
    for w in _registry.values():w['temp'].cleanup()
    _registry.clear()
atexit.register(close_all)
