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
from frontend.user_guide import render_guide

def main():
    st.set_page_config(page_title='NEMU · Minat UKM ITSB',page_icon=str(ROOT/'assets/logo_nemu.png'),layout='wide',initial_sidebar_state='expanded')
    try:
        for key in ['NEMU_ADMIN_USERNAME','NEMU_ADMIN_PASSWORD','NEMU_DEMO_USERNAME']+CONFIG_KEYS:
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
    if st.session_state.pop('clear_login_password',False):st.session_state.pop('login_password',None)
    setup(me)
    if not me:
        if is_frozen():st.warning('NEMU sedang dalam pemeliharaan. Silakan masuk sebagai admin atau coba lagi nanti.')
        st.session_state.pop('uid',None);v.auth_page();st.stop()
    if is_frozen():
        if me['role']=='admin':render_backup(me)
        else:st.warning('NEMU sedang dalam pemeliharaan. Silakan coba lagi nanti.')
        st.stop()
    from backend.demo import allowed
    if allowed(me):
        demo_page(me)
    else:
        render_workspace(me)

def render_workspace(me):
    menus={'mahasiswa':{'Dashboard':v.dashboard,'Analisis':v.render_analytics,'Panduan Penggunaan':render_guide,'Profil':v.profile,'Kuesioner':v.questionnaire,'Katalog UKM':v.catalog,'Rekomendasi':v.recommendations,'Pendaftaran':v.registrations,'Keamanan akun':v.account},
           'admin':{'Dashboard':v.dashboard,'Analisis':v.render_analytics,'Panduan Penggunaan':render_guide,'Kelola UKM':v.admin_clubs,'Logo dan aset':v.admin_assets,'Kelola akun':v.admin_users,'Pendaftaran':v.registrations,'Riwayat rekomendasi':v.admin_recommendations,'Pengaturan':v.settings,'Keamanan akun':v.account},
           'pengurus':{'Dashboard':v.dashboard,'Analisis':v.render_analytics,'Panduan Penggunaan':render_guide,'Pendaftar UKM':v.registrations,'Katalog UKM':v.catalog,'Keamanan akun':v.account}}
    from frontend.navigation import render_navigation
    menu=render_navigation(me,menus)
    if st.session_state.get('flash'):st.success(st.session_state.pop('flash'))
    try:menus[me['role']][menu](me)
    except auth.AppError as e:st.error(str(e))
    except RuntimeError:st.error('Data belum dapat dimuat. Silakan coba lagi atau hubungi admin.')
    except sqlite3.IntegrityError:st.error('Data bertabrakan dengan perubahan terbaru. Muat ulang halaman lalu coba lagi.')
    st.caption('NEMU · Institut Teknologi Sains Bandung')


def _clear_view_state():
    keep={'uid','login_at','database_identity','demo_token','demo_role','demo_role_picker','sidebar_compact'}
    for key in list(st.session_state):
        if key not in keep:del st.session_state[key]

def _switch_demo():
    st.session_state['demo_role']=st.session_state['demo_role_picker']
    _clear_view_state()

def demo_page(source_user):
    from backend.demo import get_token,workspace,reset
    from backend.db import connect
    source_id=source_user['id']
    try:
        token=get_token(source_id,st.session_state.get('demo_token'))
        if token!=st.session_state.get('demo_token'):
            _clear_view_state();st.session_state['demo_token']=token
        roles={'mahasiswa':'Mahasiswa','pengurus':'Pengurus UKM','admin':'Admin'}
        with st.sidebar:
            st.markdown('**🎓 Mode Penilaian Dosen**')
            selected=st.selectbox('Lihat sebagai',list(roles),format_func=roles.get,key='demo_role_picker',on_change=_switch_demo)
            st.session_state['demo_role']=selected
            st.caption('Data contoh terpisah · perubahan tidak memengaruhi data asli.')
            if st.button('Mulai ulang demo',icon=':material/restart_alt:',key='reset_demo'):
                st.session_state['demo_token']=reset(source_id,token);_clear_view_state();st.rerun()
        st.info('Mode demo dosen · '+roles[selected]+' · Data latihan khusus sesi ini. Pilih POV melalui sidebar. Perubahan demo dapat hilang saat sesi atau server berakhir.')
        with workspace(source_id,token) as actors:
            actor=auth.current(actors[selected])
            if not actor:
                st.warning('Akun latihan pada POV ini sudah dinonaktifkan. Pilih Mulai ulang demo untuk mengembalikan data awal.');return
            if selected=='pengurus':
                with st.sidebar:
                    clubs={r['id']:r['nama'] for r in s_demo_clubs(actor)}
                    uid=st.selectbox('UKM demo yang dikelola',list(clubs),format_func=clubs.get,key='demo_manager_club')
                if uid!=actor['ukm_id']:
                    with connect(True) as c:c.execute('UPDATE users SET ukm_id=? WHERE id=?',(uid,actor['id']))
                    actor=auth.current(actor['id'])
            render_workspace(actor)
    except auth.AppError as e:st.error(str(e))

def s_demo_clubs(actor):
    from backend.service import clubs
    return clubs(actor['id'],True)

with request_scope():main()
