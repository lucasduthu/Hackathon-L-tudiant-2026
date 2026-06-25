"""Événements : salons, JPO, forums et webinaires d'orientation, classés par
affinité avec le profil et filtrables par ville / thématique / format."""
import streamlit as st

from utils import go, persist_profile
from components import render_sidebar, event_card
from engine import match_events, derived_tastes
from data import EVENTS, CITIES, INTERESTS


def page_events():
    render_sidebar()
    profile = st.session_state.user_profile  # référence directe (mutation de saved_events)
    tinder = st.session_state.user_data.get("tinder_profile", {}) or {}
    tastes = derived_tastes(profile, tinder)
    saved = profile.get("saved_events", [])

    # Pré-sélectionne la ville du profil au premier affichage.
    if not st.session_state.get("_events_init"):
        if profile.get("city") in CITIES:
            st.session_state.events_city = profile["city"]
        st.session_state._events_init = True

    st.markdown('<div class="page-head"><span class="page-eyebrow">Près de toi</span>'
                '<div class="greet">Des <span class="em">événements</span> pour avancer</div>'
                '<div class="page-sub">Salons, portes ouvertes et webinaires, classés selon tes intérêts.</div></div>',
                unsafe_allow_html=True)

    st.markdown('<div class="card-hint">Sélection d\'exemples — chaque lien renvoie vers la page '
                'L\'Étudiant correspondante (salon, secteur, alternance…).</div>',
                unsafe_allow_html=True)

    if not tastes["tags"] and not tastes["sectors"]:
        st.markdown('<div class="note">Renseigne tes centres d\'intérêt (profil ou swipe) pour que '
                    'les événements soient triés selon <b>tes</b> goûts.</div>', unsafe_allow_html=True)
        if st.button("Faire un swipe", use_container_width=True, key="events_to_explore"):
            go("explore")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.selectbox("Ville", ["Tout"] + CITIES, key="events_city")
    with c2:
        st.selectbox("Thématique", ["Tout"] + INTERESTS, key="events_theme")
    with c3:
        st.selectbox("Format", ["Tout", "Présentiel", "En ligne"], key="events_fmt")

    filters = {"city": st.session_state.events_city,
               "theme": st.session_state.events_theme,
               "fmt": st.session_state.events_fmt}
    ranked = match_events(EVENTS, profile, tinder, filters)
    n_match = len([r for r in ranked if r["match"] > 0])

    st.markdown(f'<div class="card-hint">{len(ranked)} événement(s) · '
                f'{n_match} en lien avec ton profil · {len(saved)} dans ton agenda</div>',
                unsafe_allow_html=True)

    if not ranked:
        st.markdown('<div class="note">Aucun événement avec ces filtres. Élargis ta recherche.</div>',
                    unsafe_allow_html=True)
        return

    for i, row in enumerate(ranked):
        ev = row["event"]
        event_card(row)
        cols = st.columns([3, 2])
        in_agenda = ev["title"] in saved
        with cols[0]:
            label = "Dans mon agenda" if in_agenda else "Ajouter à mon agenda"
            if st.button(label, use_container_width=True, key=f"agenda_{i}"):
                lst = profile.setdefault("saved_events", [])
                if in_agenda:
                    lst.remove(ev["title"])
                else:
                    lst.append(ev["title"])
                persist_profile()
                st.rerun()
        with cols[1]:
            st.link_button("En savoir plus ↗", ev.get("url", "#"), use_container_width=True)
