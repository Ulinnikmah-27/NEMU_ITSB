"""One-time schema/bootstrap preparation; does not cache private user data."""
import streamlit as st
from backend.db import init_db
from backend.bootstrap import bootstrap_env
@st.cache_resource(show_spinner=False)
def prepare_database(storage_key):
    init_db();bootstrap_env()
    return True
