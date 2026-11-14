"""Entry point NEMU: python -m streamlit run app.py"""
import os,time,sqlite3
import streamlit as st
from backend.db import CONFIG_KEYS,identity,ROOT,mode
from backend import auth
from backend.request_cache import request_scope
from backend.pool import runtime_key
from frontend import views as v
from frontend.theme import setup
from frontend.runtime import prepare_database
from frontend.backup_view import render_backup
from backend.backup import is_frozen

def main():
    st.set_page_config(page_title='NEMU · Minat UKM ITSB',page_icon=str(ROOT/'assets/logo_nemu.png'),layout='wide',initial_sidebar_state='expanded')
    try:
        for key in ['NEMU_ADMIN_USERNAME','NEMU_ADMIN_PASSWORD']+CONFIG_KEYS:
            if key in st.secrets:os.environ[key]=str(st.secrets[key])
    except (FileNotFoundError,st.errors.StreamlitSecretNotFoundError):pass
    try:prepare_database(runtime_key())
    except (RuntimeError,auth.AppError,sqlite3.DatabaseError):
        st.error('NEMU belum dapat memuat data. Silakan coba lagi atau hubungi admin.');st.stop()
    if st.session_state.get('database_identity')!=identity():
        st.session_state.clear();st.session_state['database_identity']=identity()
    if st.session_state.get('uid') and time.time()-st.session_state.get('login_at',0)>8*3600:
        st.session_state.clear();st.session_state['database_identity']=identity();st.info('Sesi berakhir. Silakan masuk kembali.')
    try:me=auth.current(st.session_state.get('uid')) if st.session_state.get('uid') else None
    except RuntimeError:
        st.error('Data belum dapat dimuat. Silakan coba lagi.');st.stop()
    setup(me)
    if not me:
        if is_frozen():st.warning('NEMU sedang dalam pemeliharaan. Silakan masuk sebagai admin atau coba lagi nanti.')
        st.session_state.pop('uid',None);v.auth_page();st.stop()
    if is_frozen():
        if me['role']=='admin':render_backup(me)
        else:st.warning('NEMU sedang dalam pemeliharaan. Silakan coba lagi nanti.')
        st.stop()
    menus={'mahasiswa':{'Dashboard':v.dashboard,'Analisis':v.render_analytics,'Profil':v.profile,'Kuesioner':v.questionnaire,'Katalog UKM':v.catalog,'Rekomendasi':v.recommendations,'Pendaftaran':v.registrations,'Keamanan akun':v.account},
           'admin':{'Dashboard':v.dashboard,'Analisis':v.render_analytics,'Kelola UKM':v.admin_clubs,'Logo dan aset':v.admin_assets,'Kelola akun':v.admin_users,'Pendaftaran':v.registrations,'Riwayat rekomendasi':v.admin_recommendations,'Pengaturan':v.settings,'Keamanan akun':v.account},
           'pengurus':{'Dashboard':v.dashboard,'Analisis':v.render_analytics,'Pendaftar UKM':v.registrations,'Katalog UKM':v.catalog,'Keamanan akun':v.account}}
    from frontend.navigation import render_navigation
    menu=render_navigation(me,menus)
    if st.session_state.get('flash'):st.success(st.session_state.pop('flash'))
    try:menus[me['role']][menu](me)
    except auth.AppError as e:st.error(str(e))
    except RuntimeError:st.error('Data belum dapat dimuat. Silakan coba lagi atau hubungi admin.')
    except sqlite3.IntegrityError:st.error('Data bertabrakan dengan perubahan terbaru. Muat ulang halaman lalu coba lagi.')
    st.caption('NEMU · Institut Teknologi Sains Bandung')

with request_scope():main()
