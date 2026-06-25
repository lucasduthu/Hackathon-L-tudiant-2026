"""Explorer : mode « Tinder » sur plusieurs thématiques (Métiers, Environnement,
Valeurs, Secteurs). Chaque session enrichit le profil — clusters, métiers aimés,
environnement de travail, valeurs, secteurs visés."""
import random

import streamlit as st

from utils import go, persist_profile
from components import render_sidebar, swipe_card, tags_html
from data import TINDER_ENVIRONMENTS, VALUES_PAIRS, SECTEURS
from ai import build_swipe_deck, clusters_from_liked, start_background_tinder_fetch, get_prefetched_tinder_cards

THEMES = [("metiers", "Métiers"), ("environnement", "Environnement"),
          ("valeurs", "Valeurs"), ("secteurs", "Secteurs")]

THEME_INFO = {
    "metiers": ("Swipe des métiers", "Garde ceux qui t'attirent, écarte les autres. "
                "ORI en déduit tes univers de prédilection.", "Lancer le swipe métiers"),
    "environnement": ("Ton environnement idéal", "Pour chaque duo, choisis ce qui te ressemble "
                      "le plus. Ça affine le cadre de travail qui te conviendrait.", "Commencer"),
    "valeurs": ("Tes valeurs au travail", "Choisis ce qui compte le plus pour toi dans chaque duo. "
                "ORI en tire ce qui te motive vraiment.", "Commencer"),
    "secteurs": ("Les secteurs qui t'attirent", "Garde les secteurs qui t'intéressent. "
                 "Ils orientent recommandations et événements.", "Commencer"),
}

_SEC_EMOJI = {"Informatique/Tech": "", "Santé": "", "Commerce": "", "Ingénierie": "",
              "Art/Design": "", "Sciences humaines": "", "Droit": "", "Environnement": "",
              "Enseignement": "", "Finance": "", "Communication": ""}


def _tinder():
    return st.session_state.user_data.setdefault("tinder_profile", {})


def _merge(existing, new, cap=None):
    out = list(dict.fromkeys([x for x in (existing or []) + (new or []) if x]))
    return out[:cap] if cap else out


# ── Construction des decks ────────────────────────────────────────────────────
def _build_deck(theme, profile):
    if theme == "metiers":
        username = st.session_state.username or "guest"
        # 1. Tenter de récupérer les cartes préchargées
        cards = get_prefetched_tinder_cards(username)
        
        # 2. Si aucune carte n'est préchargée, on fait une génération synchrone (avec fallback)
        if not cards:
            with st.spinner("ORI prépare des métiers à découvrir…"):
                seen = _tinder().get("liked_careers", [])
                cards = build_swipe_deck(profile, seen=seen, n=8)
                
        # 3. Lancer un préchargement en arrière-plan pour le tour suivant
        seen = _tinder().get("liked_careers", [])
        start_background_tinder_fetch(
            username,
            profile,
            seen,
            _tinder().get("liked_careers", []),
            [],
            10
        )
        return {"theme": theme, "mode": "swipe", "items": cards, "idx": 0, "liked": [], "disliked": []}
    if theme == "secteurs":
        items = [{"title": s, "emoji": _SEC_EMOJI.get(s, ""), "keywords": []}
                 for s in random.sample(SECTEURS, len(SECTEURS))]
        return {"theme": theme, "mode": "swipe", "items": items, "idx": 0, "liked": [], "disliked": []}
    pairs = TINDER_ENVIRONMENTS if theme == "environnement" else VALUES_PAIRS
    return {"theme": theme, "mode": "pair", "items": list(pairs), "idx": 0, "choices": []}


# ── Fin de session : on enrichit le profil ────────────────────────────────────
def _finish(deck):
    theme = deck["theme"]
    tinder = _tinder()
    profile = st.session_state.user_profile
    result = {"theme": theme, "lines": []}

    if theme == "metiers":
        liked = deck["liked"]
        titles = [c.get("title", "") for c in liked]
        clusters = clusters_from_liked(liked)
        tinder["liked_careers"] = _merge(tinder.get("liked_careers"), titles)
        tinder["clusters"] = _merge(tinder.get("clusters"), clusters, cap=6)
        if clusters:
            profile["interests"] = _merge(profile.get("interests"), clusters, cap=6)
        result["lines"] = [("Univers détectés", tinder["clusters"], True),
                           ("Métiers gardés", titles or ["aucun"], False)]
        result["empty"] = not titles
    elif theme == "secteurs":
        liked = [c["title"] for c in deck["liked"]]
        tinder["sectors"] = _merge(tinder.get("sectors"), liked)
        profile["target_sectors"] = _merge(profile.get("target_sectors"), liked)
        result["lines"] = [("Secteurs gardés", liked or ["aucun"], True)]
        result["empty"] = not liked
    else:
        choices = deck["choices"]
        if theme == "environnement":
            tinder["work_environment"] = choices
            result["lines"] = [("Ton environnement idéal", choices, True)]
        else:
            tinder["values"] = choices
            result["lines"] = [("Tes valeurs", choices, True)]
        result["empty"] = not choices

    persist_profile()
    st.session_state.explore_deck = None
    st.session_state.explore_result = result


# ── Rendu d'un swipe (métiers / secteurs) ─────────────────────────────────────
def _render_swipe(deck):
    if deck["idx"] >= len(deck["items"]):
        _finish(deck)
        st.rerun()
    card = deck["items"][deck["idx"]]
    st.markdown(f'<div class="swipe-progress">Carte {deck["idx"] + 1} / {len(deck["items"])} · '
                f'{len(deck["liked"])} gardé(s)</div>', unsafe_allow_html=True)
    swipe_card(card)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Pas pour moi", use_container_width=True, key=f"no_{deck['idx']}"):
            deck["disliked"].append(card); deck["idx"] += 1; st.rerun()
    with c2:
        if st.button("Ça m'attire", type="primary", use_container_width=True, key=f"yes_{deck['idx']}"):
            deck["liked"].append(card); deck["idx"] += 1; st.rerun()
    if st.button("Terminer →", use_container_width=True, key=f"done_{deck['idx']}"):
        _finish(deck); st.rerun()


# ── Rendu d'un duo (environnement / valeurs) ──────────────────────────────────
def _render_pair(deck):
    if deck["idx"] >= len(deck["items"]):
        _finish(deck)
        st.rerun()
    pair = deck["items"][deck["idx"]]
    st.markdown(f'<div class="swipe-progress">Duo {deck["idx"] + 1} / {len(deck["items"])}</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="swipe-shell"><div class="swipe-card">'
                '<div class="swipe-sub">Qu\'est-ce qui te ressemble le plus ?</div>'
                '</div></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button(pair["a"], use_container_width=True, key=f"a_{deck['idx']}"):
            deck["choices"].append(pair["a"]); deck["idx"] += 1; st.rerun()
    with c2:
        if st.button(pair["b"], use_container_width=True, key=f"b_{deck['idx']}"):
            deck["choices"].append(pair["b"]); deck["idx"] += 1; st.rerun()
    if st.button("Terminer →", use_container_width=True, key=f"pdone_{deck['idx']}"):
        _finish(deck); st.rerun()


def _render_result(result):
    st.success("Profil mis à jour. ORI te connaît un peu mieux.")
    if result.get("empty"):
        st.markdown('<div class="note">Tu n\'as rien gardé — pas grave, ça aussi c\'est une info. '
                    'Réessaie ou change de thématique.</div>', unsafe_allow_html=True)
    for line in result["lines"]:
        h, items, red = line if len(line) == 3 else (line[0], line[1], False)
        st.markdown(f'<div class="insight"><div class="insight-h">{h}</div>'
                    f'{tags_html(items, red=red)}</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Rejouer ce thème", use_container_width=True, key="replay"):
            st.session_state.explore_result = None
            st.session_state.explore_deck = None
            st.rerun()
    with c2:
        if st.button("Voir mes recommandations", type="primary", use_container_width=True, key="to_dash"):
            st.session_state.explore_result = None
            go("dashboard")


def _theme_selector(active):
    cols = st.columns(len(THEMES))
    for col, (key, label) in zip(cols, THEMES):
        with col:
            if st.button(label, use_container_width=True, key=f"th_{key}",
                         type="primary" if key == active else "secondary"):
                if key != active:
                    st.session_state.explore_theme = key
                    st.session_state.explore_deck = None
                    st.session_state.explore_result = None
                    st.rerun()


def page_explore():
    render_sidebar()
    st.markdown('<div class="page-head"><span class="page-eyebrow">Mode découverte</span>'
                '<div class="greet">Apprends à ORI <span class="em">ce que tu aimes</span></div>'
                '<div class="page-sub">Swipe différentes thématiques : chaque choix affine ton profil.</div></div>',
                unsafe_allow_html=True)

    theme = st.session_state.explore_theme
    _theme_selector(theme)
    st.markdown("<hr>", unsafe_allow_html=True)

    deck = st.session_state.explore_deck
    result = st.session_state.get("explore_result")

    if deck and deck.get("theme") == theme:
        (_render_pair if deck["mode"] == "pair" else _render_swipe)(deck)
    elif result and result.get("theme") == theme:
        _render_result(result)
    else:
        title, desc, start = THEME_INFO[theme]
        st.markdown(f'<div class="card"><div class="card-h">{title}</div>'
                    f'<div class="page-sub">{desc}</div></div>', unsafe_allow_html=True)
        if st.button(start, type="primary", use_container_width=True, key="start_deck"):
            st.session_state.explore_deck = _build_deck(theme, st.session_state.user_profile)
            st.session_state.explore_result = None
            st.rerun()
