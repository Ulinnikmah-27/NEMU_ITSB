"""CLI helper reads local Secrets without printing credentials."""
import os,tomllib
from .db import ROOT,CONFIG_KEYS

def load():
    p=ROOT/'.streamlit/secrets.toml'
    if p.is_file():
        values=tomllib.loads(p.read_text(encoding='utf-8'))
        for k in CONFIG_KEYS+['NEMU_ADMIN_USERNAME','NEMU_ADMIN_PASSWORD']:
            if k in values and k not in os.environ:os.environ[k]=str(values[k])
