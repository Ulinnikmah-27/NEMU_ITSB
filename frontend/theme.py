import streamlit as st
import base64
from backend.db import ROOT
CSS='''
<style>
.stApp {background:#f5f7fc;}
.block-container{max-width:1180px;padding-top:5.2rem;padding-bottom:3rem}
h1,h2,h3{letter-spacing:-.035em;color:#172244}
[data-testid="stSidebar"]{background:#192344}
[data-testid="stSidebar"] p,[data-testid="stSidebar"] label,[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3 {color:#f4f6ff}
[data-testid="stVerticalBlockBorderWrapper"]{background:white;border-radius:18px}
[data-testid="stMetric"]{background:white;padding:18px;border-radius:14px;border:1px solid #e3e7f2}
.hero{background:linear-gradient(110deg,#273c79,#6b58ba);padding:28px 32px;border-radius:22px;margin-bottom:22px;color:white}
.hero h1{color:white;font-size:2.3rem;margin:0}.hero p{margin:8px 0 0;color:#e1e7ff}
.stButton>button{border-radius:10px}
[data-testid="stSidebar"] .stButton>button{background:#fff;color:#17243c!important;border:1px solid #dce5f3}
[data-testid="stSidebar"] .stButton>button p{color:#17243c!important}
[data-testid="stSidebar"] button[kind="headerNoPadding"]{color:#e8efff!important}
[data-testid="stSidebarCollapseButton"]{opacity:1!important;visibility:visible!important}
</style>'''
def setup(me=None):
    st.markdown(CSS,unsafe_allow_html=True)

def hero():
    logo=ROOT/'assets/logo_nemu.png'
    data=logo.read_bytes() if logo.is_file() else None
    if st.session_state.get('uid'):
        from backend.service import asset
        data=asset(st.session_state['uid'],'nemu') or data
    emblem=('data:image/png;base64,'+base64.b64encode(data).decode()) if data else ''
    image=f'<img src="{emblem}" alt="Logo NEMU" style="width:140px;height:140px;object-fit:contain;border-radius:16px;flex-shrink:0">' if emblem else ''
    st.markdown(f'<div class="hero" style="display:flex;align-items:center;gap:24px;flex-wrap:wrap">{image}<div><h1>NEMU</h1><p>Navigasi Eksplorasi Minat UKM · Institut Teknologi Sains Bandung</p><p>Temukan minat, kenali potensi, dan pilih komunitasmu.</p></div></div>',unsafe_allow_html=True)
