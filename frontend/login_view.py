"""Responsive two-column entry screen using native password-manager attributes."""
import base64,os,time
import streamlit as st
from backend.db import ROOT
from backend import auth
from backend.constants import PROGRAM_STUDI

def _secret(key,default=''):
    try:return str(st.secrets.get(key,os.environ.get(key,default)))
    except (FileNotFoundError,st.errors.StreamlitSecretNotFoundError):return os.environ.get(key,default)

@st.dialog('Panduan Penggunaan NEMU',width='large')
def guide_dialog():
    from .user_guide import render_guide
    render_guide()

def auth_page():
    st.markdown('''<style>
    .stApp{background:radial-gradient(ellipse at 10% 20%,#e4e4ff 0,transparent 48%),#f4f5fc;}
    .block-container{max-width:1220px;padding-top:3.8rem;padding-bottom:1rem;}
    [data-testid="stSidebar"],[data-testid="stExpandSidebarButton"]{display:none!important;}
    .st-key-auth_form{background:rgba(255,255,255,.97);padding:28px;border-radius:0 26px 26px 0;border:1px solid #e6e7f4;box-shadow:0 15px 45px #29365c12;}
    .st-key-auth_form h2{font-size:1.85rem;letter-spacing:-.04em;line-height:1.15;}
    .st-key-auth_form [data-testid="stForm"]{border:0;padding:0;}
    .st-key-auth_form [data-testid="stVerticalBlock"]{gap:.55rem;}
    .st-key-auth_form [data-testid="stFormSubmitButton"] button{width:100%;background:linear-gradient(110deg,#7052cc,#5140ab);border:0;min-height:44px;}
    .st-key-auth_form [data-testid="stFormSubmitButton"] button p{color:white!important;font-weight:650;}
    .st-key-auth_form [data-testid="stExpander"]{background:#f2efff;border:1px solid #e2ddfa;border-radius:12px;}
    .nemu-intro{min-height:555px;box-sizing:border-box;border-radius:26px 0 0 26px;padding:40px 38px;background:radial-gradient(circle at 105% 0%,#aa91ec66 0,transparent 42%),linear-gradient(135deg,#183773,#5941b3);position:relative;overflow:hidden;color:white;}
    .intro-logo{display:flex;align-items:center;gap:18px;margin-bottom:32px;}
    .intro-logo img{width:90px;height:90px;object-fit:contain;background:white;border-radius:16px;padding:6px;box-sizing:border-box;}
    .intro-logo strong{font-size:32px;letter-spacing:2px;}.intro-logo small{display:block;font-size:12px;color:#dce5ff;line-height:1.6;}
    .nemu-intro h1{color:white!important;font-size:40px!important;line-height:1.13!important;letter-spacing:-.04em;margin:0 0 14px;max-width:470px;}
    .nemu-intro p{color:#e5eaff;font-size:16px;line-height:1.65;max-width:430px;}
    .intro-steps{display:flex;flex-wrap:wrap;gap:9px;margin-top:27px;}.intro-steps span{border:1px solid #ffffff60;border-radius:11px;padding:9px;font-size:12px;background:#ffffff0c;}
    .intro-route{position:absolute;width:360px;height:130px;bottom:-35px;right:-50px;border:2px dashed #c8beff60;border-radius:50%;transform:rotate(-20deg);}.intro-plane{position:absolute;bottom:24px;right:28px;font-size:38px;color:#ffd25a;transform:rotate(-20deg);}
    @media(max-width:900px){.nemu-intro{padding:28px;min-height:555px}.nemu-intro h1{font-size:32px!important}.st-key-auth_form{padding:24px 20px}.intro-steps span{font-size:11px}}
    @media(max-width:640px){.block-container{padding-top:2.6rem}.nemu-intro{min-height:0;border-radius:22px;padding:25px;margin-bottom:14px}.intro-logo{margin-bottom:20px}.intro-logo img{width:64px;height:64px}.nemu-intro h1{font-size:29px!important}.intro-route,.intro-plane{display:none}.intro-steps{margin-top:15px}.st-key-auth_form{border-radius:22px;padding:23px}}
    </style>''',unsafe_allow_html=True)
    left,right=st.columns([1.08,1],gap='small')
    with left:
        logo=base64.b64encode((ROOT/'assets/logo_nemu.png').read_bytes()).decode()
        st.markdown(f'''<section class="nemu-intro"><div class="intro-logo"><img src="data:image/png;base64,{logo}" alt="Logo NEMU"><div><strong>NEMU</strong><small>Navigasi Eksplorasi Minat UKM<br>Institut Teknologi Sains Bandung</small></div></div><h1>Temukan UKM yang sesuai dengan minatmu.</h1><p>Kenali potensi, jelajahi komunitas, dan mulai perjalananmu bersama NEMU.</p><div class="intro-steps"><span>⌕ &nbsp; Kenali Minat</span><span>♧ &nbsp; Temukan UKM</span><span>↗ &nbsp; Mulai Bergabung</span></div><div class="intro-route"></div><div class="intro-plane">➤</div></section>''',unsafe_allow_html=True)
    with right,st.container(key='auth_form'):
        st.subheader('Selamat datang di NEMU')
        st.caption('Masuk untuk mulai mengeksplorasi UKM.')
        a,b=st.tabs(['Masuk','DAFTAR'])
        with a,st.form('login'):
            un=st.text_input('Username',autocomplete='username',key='login_username')
            pw=st.text_input('Password',type='password',autocomplete='current-password',key='login_password')
            if st.form_submit_button('Masuk',type='primary'):
                try:
                    user=auth.login(un,pw)
                    # Do not retain submitted passwords in the long-lived session state.
                    st.session_state['uid']=user['id'];st.session_state['login_at']=time.time();st.session_state['clear_login_password']=True;st.rerun()
                except auth.AppError as e:st.error(str(e))
        with b,st.form('register',clear_on_submit=False):
            nama=st.text_input('Nama lengkap',autocomplete='name');nim=st.text_input('NIM')
            prodi=st.selectbox('Program studi',PROGRAM_STUDI,index=None,placeholder='Pilih program studi')
            angkatan=st.text_input('Angkatan',placeholder='2025')
            username=st.text_input('Username baru',autocomplete='username')
            p1=st.text_input('Password baru (minimal 8 karakter)',type='password',autocomplete='new-password')
            p2=st.text_input('Ulangi password',type='password',autocomplete='new-password')
            consent=st.checkbox('Saya setuju profil dan jawaban digunakan untuk rekomendasi; pengurus UKM pilihan saya dapat melihat jawaban untuk seleksi.')
            if st.form_submit_button('Buat akun mahasiswa',type='primary'):
                if p1!=p2:st.error('Password tidak sama.')
                elif not consent:st.error('Persetujuan penggunaan data diperlukan untuk melanjutkan.')
                else:
                    try:auth.register(username,p1,nama,nim,prodi,angkatan);st.success('Akun berhasil dibuat! Buka tab Masuk dan gunakan username serta password yang baru didaftarkan.')
                    except auth.AppError as e:st.error(str(e))
        password=_secret('NEMU_DEMO_PASSWORD')
        if password:
            with st.expander('🎓 Akun Demo untuk Dosen',expanded=False):
                st.caption('Satu akun untuk mencoba tiga sudut pandang pada data demo terpisah.')
                st.text('Username: '+_secret('NEMU_DEMO_USERNAME','dosen_nemu'))
                st.text('Password: '+password)
                st.caption('Gunakan akun demo yang sudah dibuat admin. Password di sini harus sama dengan password akun tersebut.')
        if st.button('Panduan Penggunaan',icon=':material/menu_book:',key='public_guide_toggle'):guide_dialog()
        st.caption('NEMU · Institut Teknologi Sains Bandung')
