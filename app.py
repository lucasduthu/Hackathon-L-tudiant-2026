import streamlit as st

from config import setup_config, load_css
from utils import init_session_state, go
from components import render_nav, render_tabs
from views.home import page_home
from views.auth import page_auth
from views.dashboard import page_dashboard
from views.chat import page_chat
from views.explore import page_explore
from views.events import page_events
from views.profile import page_profile

# ── Configuration ─────────────────────────────────────────────────────────────
setup_config()
load_css()
init_session_state()
render_nav()

# ── Routeur ───────────────────────────────────────────────────────────────────
# Pages applicatives : accessibles connecté OU en mode invité, avec la barre d'onglets.
APP_PAGES = {
    "dashboard": page_dashboard,
    "chat": page_chat,
    "explore": page_explore,
    "events": page_events,
    "profile": page_profile,
}

page = st.session_state.page

if page == "auth":
    page_auth()
elif page in APP_PAGES:
    if st.session_state.logged_in or st.session_state.guest:
        render_tabs(page)
        APP_PAGES[page]()
    else:
        go("home")
else:
    page_home()
