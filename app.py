from pathlib import Path

import streamlit as st

import services
import tema

st.set_page_config(page_title="UNGKEP JOWO", page_icon="🍗", layout="centered", initial_sidebar_state="collapsed")
st.markdown(f"<style>{(Path(__file__).parent / 'style.css').read_text()}{tema.css()}</style>", unsafe_allow_html=True)

beranda = st.Page("pages_app/beranda.py", title="Beranda", icon="🍗", default=True)
admin = st.Page("pages_app/admin.py", title="Admin", icon=":material/admin_panel_settings:")

# Halaman admin tidak muncul di menu; hanya bisa dibuka lewat ikon admin (khusus admin).
pages = [beranda] + ([admin] if services.is_admin() else [])
st.navigation(pages, position="hidden").run()
