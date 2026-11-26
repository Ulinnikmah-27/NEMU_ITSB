"""Compact icon rail and expanded navigation, sharing the same role menu."""
import base64,html
import streamlit as st
from backend.service import asset
ICONS={'Panduan Penggunaan':'menu_book','Dashboard':'space_dashboard','Analisis':'bar_chart','Profil':'person','Kuesioner':'quiz','Katalog UKM':'groups','Rekomendasi':'explore','Pendaftaran':'assignment','Keamanan akun':'shield','Kelola UKM':'groups','Logo dan aset':'palette','Kelola akun':'manage_accounts','Riwayat rekomendasi':'history','Pengaturan':'settings','Pendaftar UKM':'assignment_ind'}
def render_navigation(me,menus):
    compact=st.session_state.get('sidebar_compact',False)
    width=84 if compact else 260
    st.markdown(f'''<style>
    [data-testid="stSidebar"]{{width:{width}px!important;min-width:{width}px!important;max-width:{width}px!important;transform:none!important;}}
    [data-testid="stSidebarCollapseButton"],[data-testid="stExpandSidebarButton"]{{display:none!important;}}
    [data-testid="stSidebarUserContent"]{{padding:1rem .65rem!important;}}
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"]{{gap:.35rem;}}
    [data-testid="stSidebar"] .stButton>button{{min-height:43px;width:100%;background:transparent;color:#e6edff!important;border:0;justify-content:{'center' if compact else 'flex-start'};padding:.65rem {'0' if compact else '.8rem'};border-radius:12px;}}
    [data-testid="stSidebar"] .stButton>button p{{color:inherit!important;font-size:14px;}}
    [data-testid="stSidebar"] .stButton>button:hover{{background:#2b3c68;color:white!important;}}
    [data-testid="stSidebar"] .stButton>button[kind="primary"]{{background:#3457a6;color:white!important;box-shadow:inset 3px 0 #ffc84b;}}
    .nemu-brand{{display:flex;align-items:center;gap:12px;margin:8px 0 18px;}}
    .nemu-brand img{{width:{'56' if compact else '72'}px;height:{'56' if compact else '72'}px;object-fit:contain;background:white;border-radius:16px;padding:5px;box-sizing:border-box;box-shadow:0 5px 18px #0a102c55;}}
    .nemu-brand strong{{color:white;font-size:23px;letter-spacing:2px;}}
    .nemu-brand small{{display:block;color:#b9c9ed;font-size:11px;line-height:1.5;}}
    .nemu-user{{color:#b9c9ed;font-size:12px;margin:0 8px 14px;}}
    </style>''',unsafe_allow_html=True)
    key='navigation_'+me['role']
    options=menus[me['role']]
    if st.session_state.get(key) not in options:st.session_state[key]='Dashboard'
    with st.sidebar:
        if st.button('' if compact else 'Kecilkan menu',icon=':material/menu_open:' if not compact else ':material/menu:',help='Buka menu' if compact else 'Kecilkan menu',key='toggle_sidebar',use_container_width=True):
            st.session_state['sidebar_compact']=not compact;st.rerun()
        logo=asset(me['id'],'nemu')
        image=f'<img src="data:image/png;base64,{base64.b64encode(logo).decode()}" alt="Logo NEMU">' if logo else ''
        detail='' if compact else '<div><strong>NEMU</strong><small>Temukan minatmu.<br>Kenali komunitasmu.</small></div>'
        st.markdown(f'<div class="nemu-brand">{image}{detail}</div>',unsafe_allow_html=True)
        if not compact:st.markdown(f'<div class="nemu-user">{html.escape(me["nama"])} · {html.escape(me["role"].title())}</div>',unsafe_allow_html=True)
        for name in options:
            if st.button('' if compact else name,icon=f':material/{ICONS[name]}:',help=name,key='nav_button_'+me['role']+'_'+name,type='primary' if st.session_state[key]==name else 'secondary',use_container_width=True):
                st.session_state[key]=name;st.rerun()
        st.divider()
        if st.button('' if compact else 'Keluar',icon=':material/logout:',help='Keluar',key='logout_sidebar',use_container_width=True):st.session_state.clear();st.rerun()
    return st.session_state[key]
