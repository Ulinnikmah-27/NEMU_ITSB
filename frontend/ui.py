"""Shared visual components; all displayed metrics come from authorized backend data."""
import html
import streamlit as st

def page_intro(title,description,role):
    badge={'admin':'Admin','mahasiswa':'Mahasiswa','pengurus':'Pengurus UKM'}.get(role,role)
    st.markdown(f'<div class="workspace-heading"><div><div class="workspace-eyebrow">NEMU / {html.escape(badge)}</div><h2>{html.escape(title)}</h2><p>{html.escape(description)}</p></div><span class="workspace-badge">{html.escape(badge)}</span></div>',unsafe_allow_html=True)

def metrics(entries):
    colors=['purple','blue','gold','green']
    for col,(label,value,icon),color in zip(st.columns(len(entries)),entries,colors):
        with col:
            st.markdown(f'<div class="summary-card {color}"><span class="summary-icon" aria-hidden="true">{html.escape(icon)}</span><div><div class="summary-label">{html.escape(label)}</div><div class="summary-value">{html.escape(str(value))}</div></div></div>',unsafe_allow_html=True)

def empty_state(title,description):
    st.markdown(f'<div class="nemu-empty"><span aria-hidden="true">▥</span><h3>{html.escape(title)}</h3><p>{html.escape(description)}</p></div>',unsafe_allow_html=True)
