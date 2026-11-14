"""Entry point: python -m streamlit run app.py"""
import os,time,sqlite3
import streamlit as st
from backend.db import init_db,connect
from backend import auth
from frontend import views as v
from frontend.theme import setup
"""Admin-only consistent SQLite snapshot and a write freeze for cutover."""
import sqlite3,tempfile,json
from pathlib import Path
from backend.db import connect
from backend.auth import require,verify_password,AppError
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

import streamlit as st
from datetime import datetime,timezone
from backend.auth import AppError

def mode():return 'sqlite'

def render_backup(me):
    st.header('Backup dan pemindahan database')
    if mode()=='postgres':
        st.success('Aplikasi memakai PostgreSQL. Akun dan pendaftaran dibaca dari database tersebut.')
        st.write('Backup penuh PostgreSQL menggunakan pg_dump. Lihat panduan dalam paket.');return
    st.write('Buat backup penuh dari database aplikasi yang sedang dibuka. Jika dibuka melalui web online, file ini berisi data web online; jika dibuka di localhost, file ini berisi data laptop.')
    st.warning('Membuat backup migrasi akan membekukan perubahan data agar tidak ada pendaftaran baru yang tertinggal. Akun admin tetap bisa login dan mengunduh ulang. Jika migrasi belum jadi, gunakan Buka kembali aplikasi.')
    with st.form('backup_full_form'):
        password=st.text_input('Password admin saat ini',type='password')
        save=st.form_submit_button('Bekukan dan siapkan backup penuh',type='primary')
        reopen=st.form_submit_button('Buka kembali aplikasi')
    if save:
        try:
            data,counts=freeze_snapshot(me['id'],password)
            st.session_state['full_backup_bytes']=data;st.session_state['full_backup_counts']=counts
        except AppError as e:st.error(str(e))
    if reopen:
        try:resume(me['id'],password);st.session_state.pop('full_backup_bytes',None);st.success('Aplikasi dibuka kembali. Jika nanti migrasi, buat backup terbaru dahulu.')
        except AppError as e:st.error(str(e))
    if st.session_state.get('full_backup_bytes'):
        st.write('Jumlah data pada backup:',st.session_state['full_backup_counts'])
        st.download_button('Unduh BACKUP PENUH NEMU (.db)',st.session_state['full_backup_bytes'],'nemu_backup_migrasi_'+datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')+'.db','application/octet-stream')
        st.info('Simpan file ini di laptop. File memuat password hash dan data pribadi; jangan unggah ke GitHub atau bagikan lewat tautan publik. Jangan beralih ke Supabase sebelum file berhasil diunduh.')
    if is_frozen():st.caption('Status: perubahan data SQLite sedang dibekukan untuk migrasi.')

st.set_page_config(page_title='NEMU · Minat UKM ITSB',page_icon='🧭',layout='wide')
# Streamlit Secrets hanya digunakan untuk bootstrap admin pada deployment demo.
try:
    for key in ['NEMU_ADMIN_USERNAME','NEMU_ADMIN_PASSWORD']:
        if key in st.secrets and not os.environ.get(key):os.environ[key]=str(st.secrets[key])
except (FileNotFoundError,st.errors.StreamlitSecretNotFoundError):pass
try:
    init_db()
    from backend.bootstrap import bootstrap_env
    bootstrap_env()
except (RuntimeError,auth.AppError,sqlite3.DatabaseError) as e:
    st.error('Inisialisasi gagal: '+str(e));st.stop()
setup()
if st.session_state.get('uid') and time.time()-st.session_state.get('login_at',0)>8*3600:
    st.session_state.clear();st.info('Sesi berakhir. Silakan masuk kembali.')
me=auth.current(st.session_state.get('uid')) if st.session_state.get('uid') else None
if not me:
    if is_frozen():st.warning('NEMU sedang memindahkan database. Silakan masuk sebagai admin untuk mengunduh backup.')
    st.session_state.pop('uid',None);v.auth_page();st.stop()
if me['role']=='admin':
    render_backup(me)
    st.divider()
if is_frozen():
    if me['role']!='admin':st.warning('NEMU sedang memindahkan database. Silakan coba lagi nanti.')
    st.stop()
menus={'mahasiswa':{'Dashboard':v.dashboard,'Analisis':v.render_analytics,'Profil':v.profile,'Kuesioner':v.questionnaire,'Katalog UKM':v.catalog,'Rekomendasi':v.recommendations,'Pendaftaran':v.registrations,'Keamanan akun':v.account},
       'admin':{'Dashboard':v.dashboard,'Analisis':v.render_analytics,'Kelola UKM':v.admin_clubs,'Logo dan aset':v.admin_assets,'Kelola akun':v.admin_users,'Pendaftaran':v.registrations,'Riwayat rekomendasi':v.admin_recommendations,'Pengaturan':v.settings,'Keamanan akun':v.account},
       'pengurus':{'Dashboard':v.dashboard,'Analisis':v.render_analytics,'Pendaftar UKM':v.registrations,'Katalog UKM':v.catalog,'Keamanan akun':v.account}}
with st.sidebar:
    from backend.service import asset
    logo=asset(me['id'],'nemu')
    if logo:st.image(logo,width=70)
    st.title('🧭 NEMU');st.write(me['nama']);st.caption(me['role'].upper())
    menu=st.radio('Navigasi',list(menus[me['role']]),key='navigation_'+me['role'])
    st.divider()
    if st.button('Keluar',use_container_width=True):st.session_state.clear();st.rerun()
if st.session_state.get('flash'):st.success(st.session_state.pop('flash'))
try:menus[me['role']][menu](me)
except auth.AppError as e:st.error(str(e))
except sqlite3.IntegrityError:st.error('Data bertabrakan dengan perubahan terbaru. Muat ulang halaman lalu coba lagi.')
st.caption('NEMU · ITSB · Profil UKM bersumber dari wawancara kelompok. Informasi yang belum terkonfirmasi perlu ditinjau pengurus.')
