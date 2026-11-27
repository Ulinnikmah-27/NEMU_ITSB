import streamlit as st
import base64
from backend.db import ROOT
CSS='''
<style>
.stApp{background:radial-gradient(ellipse at 90% 0%,#eeecff 0,transparent 42%),#f5f7fc;color:#172244;}
.block-container{max-width:1240px;padding-top:3.8rem;padding-bottom:2rem;}
h1,h2,h3{letter-spacing:-.035em;color:#172244!important;}h1{font-size:2.1rem!important;}h2{font-size:1.65rem!important;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#19264b,#121d37)!important;}
[data-testid="stSidebar"] p,[data-testid="stSidebar"] label,[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3{color:#eef3ff!important;}
[data-testid="stMetric"]{background:#fff;padding:18px 20px;border-radius:17px;border:1px solid #e3e7f2;border-top:3px solid #8070cb;box-shadow:0 5px 20px #17224405;}
[data-testid="stMetricLabel"] p{color:#61708a!important;font-weight:500;}[data-testid="stMetricValue"]{color:#1a2b58!important;font-weight:650;}
[data-testid="stForm"]{background:#fff;border:1px solid #e4e8f2;border-radius:17px;padding:20px;}
[data-testid="stExpander"]{border:1px solid #e3e7f1;border-radius:13px;background:#ffffffbb;}
[data-testid="stAlert"]{border-radius:13px;}[data-testid="stDataFrame"]{border:1px solid #e3e7f1;border-radius:14px;overflow:hidden;}
.stButton>button,[data-testid="stFormSubmitButton"] button{border-radius:10px;font-weight:600;}
button[kind="primary"]{background:linear-gradient(110deg,#6c55c7,#5142a6);border-color:transparent;}button[kind="primary"] p{color:white!important;}
.hero{background:linear-gradient(110deg,#213f7c,#6350b6);padding:24px 28px;border-radius:22px;margin-bottom:20px;color:white;box-shadow:0 8px 28px #233c7810;}
.hero h1{color:white!important;font-size:2rem!important;margin:0}.hero p{margin:8px 0 0;color:#e2e8ff}
/* Explicit white foreground on dark menu. Do not inherit form-button colors. */
[data-testid="stSidebar"] .stButton>button{background:transparent!important;color:#eef3ff!important;border:1px solid transparent!important;box-shadow:none;}
[data-testid="stSidebar"] .stButton>button p,[data-testid="stSidebar"] .stButton>button span{color:#eef3ff!important;opacity:1!important;}
[data-testid="stSidebar"] .stButton>button:hover{background:#2b3c65!important;border-color:#465980!important;}
[data-testid="stSidebar"] .stButton>button[kind="primary"]{background:linear-gradient(100deg,#3b5db1,#6b52b9)!important;border-color:#8672cf!important;box-shadow:inset 3px 0 #ffcf5a,0 5px 13px #090f2730!important;}
[data-testid="stSidebar"] .stButton>button[kind="primary"] p{font-weight:700!important;}
[data-testid="stSidebar"] button:focus-visible{outline:2px solid #ffcf5a!important;outline-offset:2px;}
[data-testid="stSidebar"] [data-testid="stSelectbox"] label{color:#eef3ff!important;}
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"]{color:#182446!important;}
</style>'''

def setup(me=None):
    st.markdown(CSS,unsafe_allow_html=True)

def hero(me=None):
    logo=ROOT/'assets/logo_nemu.png'
    data=logo.read_bytes() if logo.is_file() else None
    if me:
        from backend.service import asset
        data=asset(me['id'],'nemu') or data
    emblem=('data:image/png;base64,'+base64.b64encode(data).decode()) if data else ''
    image=f'<img src="{emblem}" alt="Logo NEMU" style="width:140px;height:140px;object-fit:contain;border-radius:16px;flex-shrink:0">' if emblem else ''
    st.markdown(f'<div class="hero" style="display:flex;align-items:center;gap:24px;flex-wrap:wrap">{image}<div><h1>NEMU</h1><p>Navigasi Eksplorasi Minat UKM · Institut Teknologi Sains Bandung</p><p>Temukan minat, kenali potensi, dan pilih komunitasmu.</p></div></div>',unsafe_allow_html=True)
