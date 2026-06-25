import streamlit as st

from db import save_user_data

# Schéma d'un message :
#   {"role": "user"|"assistant", "content": str,
#    "block": {...}|None,          # carte riche attachée (metiers / swipe_result)
#    "suggestions": [{"label","action","echo"}]}  # puces de réponse rapide (assistant)
#
# Les favoris (saved_metiers) et l'agenda (saved_events) vivent DANS user_profile
# afin d'être persistés tels quels par save_user_data(profile=...).

DEFAULTS = {
    "page": "home",
    "logged_in": False,
    "guest": False,
    "username": None,
    "user_data": {},
    "user_profile": {},
    "messages": [],
    "all_conversations": [],
    "current_conv_id": None,
    "auth_mode": "login",
    "pending": None,            # intent chat à traiter au prochain run
    # ── Explorer (mode Tinder multi-thématique) ──
    "explore_theme": "metiers",
    "explore_deck": None,       # {cards, idx, liked, disliked, choices} en cours
    "explore_result": None,     # résumé du dernier swipe terminé
    # ── Filtres Événements ──
    "events_city": "Tout",
    "events_theme": "Tout",
    "events_fmt": "Tout",
}


def go(page):
    st.session_state.page = page
    st.rerun()


def init_session_state():
    for k, v in DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v


def reset_session():
    for k, v in DEFAULTS.items():
        st.session_state[k] = v.copy() if isinstance(v, (list, dict)) else v


def persist_profile():
    """Sauvegarde profil + tinder_profile pour les comptes (no-op pour les invités)."""
    if st.session_state.logged_in and st.session_state.username:
        save_user_data(
            st.session_state.username,
            profile=st.session_state.user_profile,
            tinder_profile=st.session_state.user_data.get("tinder_profile", {}),
        )
