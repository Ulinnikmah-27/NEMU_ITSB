"""Seluruh aksi pengguna masuk lewat service; hak akses diperiksa ulang di backend."""
import json,re,sqlite3
from io import BytesIO
from PIL import Image,UnidentifiedImageError
from .db import connect,now,setting,club
from .auth import AppError,require,create_user,public,hash_password
from .recommendation import validate,rank,MINAT,BAKAT,SKILL,LEVELS,PREFER,LOC

def config(actor):
    with connect() as c:
        require(c,actor,['admin','mahasiswa','pengurus'])
        return {r['key']:json.loads(r['value']) for r in c.execute('SELECT * FROM settings')}
def clubs(actor,include_inactive=False):
    with connect() as c:
        u=require(c,actor,['admin','mahasiswa','pengurus'])
        return [club(r) for r in c.execute('SELECT * FROM ukm ORDER BY nama') if r['aktif'] or (include_inactive and u['role']=='admin')]
def latest_answers(actor):
    with connect() as c:
        require(c,actor,['mahasiswa'])
        r=c.execute('SELECT * FROM kuesioner WHERE user_id=? ORDER BY id DESC LIMIT 1',(actor,)).fetchone()
        return json.loads(r['jawaban']) if r else {}
def _recommend(c,actor,question_id,a):
    w=setting(c,'bobot');results=rank(a,[club(r) for r in c.execute('SELECT * FROM ukm WHERE aktif=1')],w)
    rid=c.execute('INSERT INTO rekomendasi(user_id,kuesioner_id,bobot,hasil,created_at) VALUES(?,?,?,?,?)',
                  (actor,question_id,json.dumps(w),json.dumps(results,ensure_ascii=False),now())).lastrowid
    return rid

def save_answers(actor,a):
    a=validate(a)
    with connect(True) as c:
        require(c,actor,['mahasiswa'])
        qid=c.execute('INSERT INTO kuesioner(user_id,versi,jawaban,created_at) VALUES(?,?,?,?)',(actor,'2.0',json.dumps(a,ensure_ascii=False),now())).lastrowid
        return _recommend(c,actor,qid,a)
def refresh_recommendations(actor):
    with connect(True) as c:
        require(c,actor,['mahasiswa'])
        q=c.execute('SELECT * FROM kuesioner WHERE user_id=? ORDER BY id DESC LIMIT 1',(actor,)).fetchone()
        if not q:raise AppError('Isi kuesioner terlebih dahulu.')
        return _recommend(c,actor,q['id'],json.loads(q['jawaban']))
def recommendations(actor):
    with connect() as c:
        require(c,actor,['mahasiswa'])
        r=c.execute('SELECT * FROM rekomendasi WHERE user_id=? ORDER BY id DESC LIMIT 1',(actor,)).fetchone()
        return {'id':r['id'],'hasil':json.loads(r['hasil']),'bobot':json.loads(r['bobot']),'created_at':r['created_at']} if r else None
def recommendations_admin(actor):
    with connect() as c:
        require(c,actor,['admin'])
        return [dict(r) for r in c.execute('SELECT r.id,u.nama,r.created_at,r.bobot,r.hasil FROM rekomendasi r JOIN users u ON u.id=r.user_id ORDER BY r.id DESC LIMIT 200')]
def register_clubs(actor,ids):
    if not ids or len(ids)>2 or len(set(ids))!=len(ids):raise AppError('Pilih satu atau dua UKM yang berbeda.')
    with connect(True) as c:
        require(c,actor,['mahasiswa'])
        if not setting(c,'pendaftaran_buka'):raise AppError('Pendaftaran sedang ditutup.')
        period=setting(c,'periode')
        existing=[dict(r) for r in c.execute('SELECT * FROM pendaftaran WHERE user_id=? AND periode=?',(actor,period))]
        active=[r for r in existing if r['status']!='Dibatalkan']
        if len(active)+len(ids)>2:raise AppError('Maksimal dua UKM per periode, termasuk yang sudah mendapat keputusan.')
        if any(r['ukm_id'] in ids for r in active):raise AppError('Kamu sudah mendaftar ke UKM tersebut.')
        rec=c.execute('SELECT * FROM rekomendasi WHERE user_id=? ORDER BY id DESC LIMIT 1',(actor,)).fetchone()
        if not rec:raise AppError('Isi kuesioner dan lihat rekomendasi sebelum mendaftar.')
        results={r['ukm_id']:r for r in json.loads(rec['hasil'])}
        for uid in ids:
            row=c.execute('SELECT * FROM ukm WHERE id=? AND aktif=1',(uid,)).fetchone()
            if not row or uid not in results:raise AppError('UKM tidak aktif atau belum tercakup dalam rekomendasi. Perbarui rekomendasi dahulu.')
            old=next((r for r in existing if r['ukm_id']==uid),None)
            if old:
                c.execute("UPDATE pendaftaran SET status='Menunggu',konfirmasi='Belum',catatan='',rekomendasi_id=?,skor=?,created_at=?,updated_at=? WHERE id=?",(rec['id'],results[uid]['skor'],now(),now(),old['id']))
            else:
                c.execute('INSERT INTO pendaftaran(user_id,ukm_id,periode,rekomendasi_id,skor,created_at,updated_at) VALUES(?,?,?,?,?,?,?)',(actor,uid,period,rec['id'],results[uid]['skor'],now(),now()))

def registrations(actor):
    with connect() as c:
        u=require(c,actor,['mahasiswa','pengurus','admin'])
        sql='''SELECT p.*,u.nama mahasiswa,u.nim,u.prodi,u.angkatan,k.nama ukm FROM pendaftaran p JOIN users u ON u.id=p.user_id JOIN ukm k ON k.id=p.ukm_id'''
        where,args=('',())
        if u['role']=='mahasiswa':where,args=(' WHERE p.user_id=?',(actor,))
        elif u['role']=='pengurus':where,args=(' WHERE p.ukm_id=?',(u['ukm_id'],))
        return [dict(r) for r in c.execute(sql+where+' ORDER BY p.id DESC',args)]
def cancel(actor,rid):
    with connect(True) as c:
        require(c,actor,['mahasiswa'])
        r=c.execute('SELECT * FROM pendaftaran WHERE id=? AND user_id=?',(rid,actor)).fetchone()
        if not r or r['status']!='Menunggu':raise AppError('Hanya pendaftaran sendiri yang masih menunggu yang dapat dibatalkan.')
        if r['periode']!=setting(c,'periode'):raise AppError('Periode pendaftaran ini sudah berakhir.')
        c.execute("UPDATE pendaftaran SET status='Dibatalkan',updated_at=? WHERE id=?",(now(),rid))
        c.execute('INSERT INTO hasil_seleksi(pendaftaran_id,actor_id,status,catatan,created_at) VALUES(?,?,?,?,?)',(rid,actor,'Dibatalkan','Dibatalkan mahasiswa',now()))
def decide(actor,rid,status,note):
    if status not in ['Menunggu','Diterima','Ditolak']:raise AppError('Status tidak valid.')
    if len(note)>2000:raise AppError('Catatan maksimal 2.000 karakter.')
    with connect(True) as c:
        u=require(c,actor,['admin','pengurus'])
        r=c.execute('SELECT * FROM pendaftaran WHERE id=?',(rid,)).fetchone()
        if not r or (u['role']=='pengurus' and r['ukm_id']!=u['ukm_id']):raise AppError('Pendaftaran ini bukan kewenanganmu.')
        if r['status']=='Dibatalkan':raise AppError('Pendaftaran sudah dibatalkan mahasiswa.')
        kuota=club(c.execute('SELECT * FROM ukm WHERE id=?',(r['ukm_id'],)).fetchone()).get('kuota')
        if status=='Diterima' and r['status']!='Diterima' and kuota is not None:
            n=c.execute("SELECT count(*) FROM pendaftaran WHERE ukm_id=? AND periode=? AND status='Diterima' AND konfirmasi!='Dilepas'",(r['ukm_id'],r['periode'])).fetchone()[0]
            if n>=kuota:raise AppError('Kuota UKM sudah penuh.')
        c.execute("UPDATE pendaftaran SET status=?,catatan=?,konfirmasi=CASE WHEN status=? THEN konfirmasi ELSE 'Belum' END,updated_at=? WHERE id=?",(status,note,status,now(),rid))
        c.execute('INSERT INTO hasil_seleksi(pendaftaran_id,actor_id,status,catatan,created_at) VALUES(?,?,?,?,?)',(rid,actor,status,note,now()))
def confirm(actor,rid,choice):
    if choice not in ['Diambil','Dilepas']:raise AppError('Konfirmasi tidak valid.')
    with connect(True) as c:
        require(c,actor,['mahasiswa'])
        r=c.execute("SELECT * FROM pendaftaran WHERE id=? AND user_id=? AND status='Diterima'",(rid,actor)).fetchone()
        if not r:raise AppError('Pendaftaran belum diterima atau bukan milikmu.')
        if r['periode']!=setting(c,'periode'):raise AppError('Periode sudah berakhir.')
        if r['konfirmasi']=='Dilepas':raise AppError('Tawaran yang dilepas tidak dapat diambil kembali. Hubungi pengurus.')
        c.execute('UPDATE pendaftaran SET konfirmasi=?,updated_at=? WHERE id=?',(choice,now(),rid))
        c.execute('INSERT INTO hasil_seleksi(pendaftaran_id,actor_id,status,catatan,created_at) VALUES(?,?,?,?,?)',(rid,actor,'Konfirmasi',choice,now()))
def history(actor,rid):
    # Daftar yang dapat diakses selalu ditentukan oleh role backend.
    if rid not in {r['id'] for r in registrations(actor)}:raise AppError('Riwayat tidak dapat diakses.')
    with connect() as c:return [dict(r) for r in c.execute('SELECT h.status,h.catatan,h.created_at,u.nama actor FROM hasil_seleksi h JOIN users u ON u.id=h.actor_id WHERE pendaftaran_id=? ORDER BY h.id',(rid,))]
def applicant_answers(actor,rid):
    with connect() as c:
        u=require(c,actor,['admin','pengurus'])
        r=c.execute('SELECT p.ukm_id,k.jawaban FROM pendaftaran p JOIN rekomendasi r ON r.id=p.rekomendasi_id JOIN kuesioner k ON k.id=r.kuesioner_id WHERE p.id=?',(rid,)).fetchone()
        if not r or (u['role']=='pengurus' and r['ukm_id']!=u['ukm_id']):raise AppError('Jawaban tidak dapat diakses.')
        return json.loads(r['jawaban'])
def update_profile(actor,nama,prodi,angkatan):
    from .constants import validate_prodi
    prodi=validate_prodi(prodi)
    if len(nama.strip())<2 or not prodi.strip() or not re.fullmatch(r'20\d{2}',angkatan):raise AppError('Lengkapi nama, prodi, dan angkatan.')
    with connect(True) as c:
        require(c,actor,['mahasiswa'])
        c.execute('UPDATE users SET nama=?,prodi=?,angkatan=? WHERE id=?',(nama.strip(),prodi.strip(),angkatan,actor))
def save_club(actor,p):
    if not re.fullmatch(r'[a-z0-9_\-]{2,50}',p['slug']) or not p['nama'].strip() or not p['kategori'].strip():raise AppError('Isi nama, kategori, dan slug yang valid.')
    for k,opts in [('minat',MINAT),('bakat',BAKAT),('kemampuan',SKILL)]:
        if not isinstance(p[k],list) or any(t not in opts for t in p[k]):raise AppError(f'Tag {k} tidak valid.')
    if not p['minat']:raise AppError('Pilih minimal satu minat UKM.')
    if p.get('pola') not in PREFER+[None] or p.get('lokasi') not in LOC+[None] or p.get('komitmen') not in LEVELS+[None]:raise AppError('Kriteria UKM tidak valid.')
    if p.get('kuota') is not None and (type(p['kuota']) is not int or p['kuota']<1):raise AppError('Kuota harus bilangan bulat positif atau kosong.')
    if p.get('pemula') not in [True,False,None]:raise AppError('Status pemula tidak valid.')
    with connect(True) as c:
        require(c,actor,['admin'])
        try:
            if p.get('id'):
                c.execute('UPDATE ukm SET slug=?,nama=?,kategori=?,profil=?,aktif=?,updated_at=? WHERE id=?',(p['slug'],p['nama'],p['kategori'],json.dumps(p,ensure_ascii=False),int(p['aktif']),now(),p['id']))
            else:c.execute('INSERT INTO ukm(slug,nama,kategori,profil,aktif,updated_at) VALUES(?,?,?,?,?,?)',(p['slug'],p['nama'],p['kategori'],json.dumps(p,ensure_ascii=False),int(p['aktif']),now()))
        except sqlite3.IntegrityError:raise AppError('Slug sudah digunakan.') from None

def archive_club(actor,uid):
    with connect(True) as c:
        require(c,actor,['admin'])
        # Arsip menjaga pendaftaran dan riwayat; tidak menghapus data yang berelasi.
        c.execute('UPDATE ukm SET aktif=0,updated_at=? WHERE id=?',(now(),uid))
def update_config(actor,weights,period,opened):
    if set(weights)!={'minat','bakat','kemampuan','preferensi','komitmen'} or any(type(v) is not int or not 0<=v<=100 for v in weights.values()) or sum(weights.values())!=100:raise AppError('Bobot harus bilangan bulat dengan total 100%.')
    if not 1<=len(period.strip())<=40:raise AppError('Periode harus 1–40 karakter.')
    with connect(True) as c:
        require(c,actor,['admin'])
        for k,v in [('bobot',weights),('periode',period.strip()),('pendaftaran_buka',bool(opened))]:c.execute('UPDATE settings SET value=? WHERE key=?',(json.dumps(v),k))
def users(actor):
    with connect() as c:
        require(c,actor,['admin'])
        return [public(r) for r in c.execute('SELECT * FROM users ORDER BY id')]
def create_manager(actor,username,password,nama,uid):
    with connect(True) as c:
        require(c,actor,['admin'])
        return create_user(c,username,password,nama,'pengurus',ukm_id=uid)
def set_user_active(actor,uid,active):
    with connect(True) as c:
        require(c,actor,['admin'])
        if uid==actor:raise AppError('Akun sendiri tidak dapat dinonaktifkan.')
        c.execute('UPDATE users SET aktif=? WHERE id=?',(int(active),uid))
def reset_password(actor,uid,new):
    with connect(True) as c:
        require(c,actor,['admin']);c.execute('UPDATE users SET password_hash=? WHERE id=?',(hash_password(new),uid))
def save_asset(actor,key,data):
    if len(data)>2*1024*1024:raise AppError('Ukuran logo maksimal 2 MB.')
    try:
        im=Image.open(BytesIO(data));im.verify()
        im=Image.open(BytesIO(data))
        if im.width*im.height>16_000_000:raise AppError('Resolusi logo terlalu besar.')
        im.thumbnail((800,800));out=BytesIO();im.convert('RGBA').save(out,format='PNG');data=out.getvalue()
    except (UnidentifiedImageError,OSError,Image.DecompressionBombError):raise AppError('Gunakan gambar PNG, JPG, atau WEBP yang valid.') from None
    with connect(True) as c:
        require(c,actor,['admin'])
        if key!='nemu':
            if not key.startswith('ukm:') or not key[4:].isdigit() or not c.execute('SELECT 1 FROM ukm WHERE id=?',(int(key[4:]),)).fetchone():raise AppError('Kunci logo tidak valid.')
        c.execute('INSERT OR REPLACE INTO assets VALUES(?,?,?)',(key,data,'image/png'))
def asset(actor,key):
    with connect() as c:
        require(c,actor,['mahasiswa','admin','pengurus'])
        r=c.execute('SELECT data FROM assets WHERE key=?',(key,)).fetchone();return r['data'] if r else None
