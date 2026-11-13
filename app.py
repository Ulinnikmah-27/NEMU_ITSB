"""Entry point: python -m streamlit run app.py"""
import os,time,sqlite3
import streamlit as st
from backend.db import init_db,connect
from backend import auth
from frontend import views as v
from frontend.theme import setup
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
    st.session_state.pop('uid',None);v.auth_page();st.stop()
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
