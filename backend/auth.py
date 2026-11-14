import hashlib, secrets, hmac, re, time, sqlite3
from .db import connect,now
class AppError(ValueError): pass
ITERATIONS=600_000
def hash_password(password):
    if not isinstance(password,str) or not 8<=len(password)<=128:raise AppError('Password harus 8–128 karakter.')
    salt=secrets.token_hex(16)
    return f'pbkdf2_sha256${ITERATIONS}${salt}$'+hashlib.pbkdf2_hmac('sha256',password.encode(),salt.encode(),ITERATIONS).hex()
def verify_password(password,stored):
    try:
        _,n,salt,digest=stored.split('$')
        computed=hashlib.pbkdf2_hmac('sha256',password.encode(),salt.encode(),int(n)).hex()
        return hmac.compare_digest(computed,digest)
    except (ValueError,TypeError,AttributeError):return False
def clean_user(username):
    username=username.strip().lower()
    if not re.fullmatch(r'[a-z0-9_]{3,32}',username):raise AppError('Username 3–32 karakter: huruf, angka, atau underscore.')
    return username
def public(row):return {k:row[k] for k in row.keys() if k!='password_hash'} if row else None
def require(c,actor,roles):
    suffix=' FOR UPDATE' if getattr(c,'is_postgres',False) and c.write else ''
    u=c.execute('SELECT * FROM users WHERE id=? AND aktif=1'+suffix,(actor,)).fetchone()
    if not u or u['role'] not in roles:raise AppError('Akses tidak diizinkan.')
    return u
def create_user(c,username,password,nama,role='mahasiswa',nim=None,prodi='',angkatan='',ukm_id=None):
    username=clean_user(username);nama=nama.strip()
    if not 2<=len(nama)<=100:raise AppError('Nama harus 2–100 karakter.')
    if role=='mahasiswa' and (not nim or not re.fullmatch(r'[0-9A-Za-z-]{3,30}',nim)):raise AppError('Isi NIM yang valid.')
    try:
        return c.execute('INSERT INTO users(username,password_hash,role,nama,nim,prodi,angkatan,ukm_id,created_at) VALUES(?,?,?,?,?,?,?,?,?)',
                         (username,hash_password(password),role,nama,nim,prodi.strip(),angkatan.strip(),ukm_id,now())).lastrowid
    except sqlite3.IntegrityError:raise AppError('Username/NIM sudah digunakan atau UKM tidak valid.') from None
def register(username,password,nama,nim,prodi,angkatan):
    from .constants import validate_prodi
    prodi=validate_prodi(prodi)
    if not prodi.strip() or not re.fullmatch(r'20\d{2}',angkatan):raise AppError('Isi program studi dan angkatan empat digit.')
    with connect(True) as c:return create_user(c,username,password,nama,nim=nim.strip(),prodi=prodi,angkatan=angkatan)
def login(username,password):
    username=username.strip().lower();error=False
    with connect(True) as c:
        if getattr(c,'is_postgres',False):c.execute('SELECT pg_advisory_xact_lock(hashtext(?))',(username,))
        a=c.execute('SELECT * FROM login_attempts WHERE username=?',(username,)).fetchone()
        if a and a['locked_until']>time.time():raise AppError('Terlalu banyak percobaan. Coba lagi setelah 5 menit.')
        r=c.execute('SELECT * FROM users WHERE username=? AND aktif=1',(username,)).fetchone()
        if not r or not verify_password(password,r['password_hash']):
            attempts=(a['attempts'] if a and a['locked_until']==0 else 0)+1
            c.execute('INSERT OR REPLACE INTO login_attempts VALUES(?,?,?)',(username,attempts,time.time()+300 if attempts>=5 else 0));error=True
        else:c.execute('DELETE FROM login_attempts WHERE username=?',(username,))
    if error:raise AppError('Username atau password salah.')
    return public(r)
def current(actor):
    with connect() as c:
        try:return public(require(c,actor,['admin','mahasiswa','pengurus']))
        except AppError:return None
def change_password(actor,old,new):
    with connect(True) as c:
        u=require(c,actor,['admin','mahasiswa','pengurus'])
        if not verify_password(old,u['password_hash']):raise AppError('Password lama tidak sesuai.')
        c.execute('UPDATE users SET password_hash=? WHERE id=?',(hash_password(new),actor))
