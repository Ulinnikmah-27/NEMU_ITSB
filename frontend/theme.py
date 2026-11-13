import streamlit as st
CSS='''
<style>
.stApp {background:#f5f7fc;}
.block-container{max-width:1180px;padding-top:2rem;padding-bottom:3rem}
h1,h2,h3{letter-spacing:-.035em;color:#172244}
[data-testid="stSidebar"]{background:#192344}
[data-testid="stSidebar"] p,[data-testid="stSidebar"] label,[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3 {color:#f4f6ff}
[data-testid="stVerticalBlockBorderWrapper"]{background:white;border-radius:18px}
[data-testid="stMetric"]{background:white;padding:18px;border-radius:14px;border:1px solid #e3e7f2}
.hero{background:linear-gradient(110deg,#273c79,#6b58ba);padding:28px 32px;border-radius:22px;margin-bottom:22px;color:white}
.hero h1{color:white;font-size:2.3rem;margin:0}.hero p{margin:8px 0 0;color:#e1e7ff}
.stButton>button{border-radius:10px}
</style>'''
def setup(): st.markdown(CSS,unsafe_allow_html=True)
def hero():
    st.markdown('<div class="hero"><h1>🧭 NEMU</h1><p>Navigasi Eksplorasi Minat UKM · Institut Teknologi Sains Bandung</p><p>Temukan minat, kenali potensi, dan pilih komunitasmu.</p></div>',unsafe_allow_html=True)
