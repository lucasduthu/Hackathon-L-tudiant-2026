"""Dashboard : point d'entrée personnalisé — suivi de la démarche, recommandations,
événements à proximité et prochaines actions. Tout est dérivé du profil."""
import html

import streamlit as st

from utils import go, persist_profile
from components import (render_sidebar, milestone_stepper, progress_ring_svg,
                        metier_card, event_card, tags_html)
from engine import (journey_milestones, journey_progress, profile_completion,
                    derived_tastes, match_events)
from data import EVENTS, TINDER_CAREERS, INTERESTS
from ai import suggest_metier_cards, resolve_fiche_url

_EMOJI = {"Technique": "", "Innovation": "", "Données": "", "Humain": "",
          "Créativité": "", "Art": "", "Business": "", "Management": "",
          "International": "", "Terrain": "", "Recherche": "", "Communication": ""}


def _local_recos(tastes):
    """Recommandations hors-ligne (sans Ollama) : métiers du deck dont les mots-clés
    recoupent les goûts, sinon métiers aimés, sinon top du deck."""
    tags = {t.lower() for t in tastes["tags"]}
    pool = [c for c in TINDER_CAREERS
            if tags & {k.lower() for k in c.get("keywords", [])}]
    pool = pool or [{"title": t, "emoji": "", "keywords": []} for t in tastes["liked"]] or TINDER_CAREERS
    out = []
    for c in pool[:3]:
        out.append({"title": c["title"], "sector": "Piste pour toi", "emoji": c.get("emoji", ""),
                    "extract": ", ".join(c.get("keywords", [])), "url": resolve_fiche_url(c["title"])})
    return out


def _get_recos(profile, tastes):
    """Cache les recommandations en session (clé = signature des goûts) : évite de
    rappeler l'IA à chaque interaction."""
    key = "|".join(tastes["tags"]) + "::" + (profile.get("persona") or "")
    if st.session_state.get("dash_recos_key") == key and "dash_recos" in st.session_state:
        return st.session_state["dash_recos"]
    with st.spinner("ORI prépare tes recommandations…"):
        res = suggest_metier_cards(profile)
    cards = res.get("cards") or []
    if not cards:                       # Ollama indisponible → fallback local
        cards = _local_recos(tastes)
    st.session_state["dash_recos"] = cards
    st.session_state["dash_recos_key"] = key
    return cards


def _cta(col, ico, h, p, page, key):
    with col:
        ico_html = f'<div class="cta-ico">{ico}</div>' if ico else ""
        st.markdown(f'<div class="cta-card">{ico_html}'
                    f'<div class="cta-h">{h}</div><div class="cta-p">{p}</div></div>',
                    unsafe_allow_html=True)
        if st.button("Ouvrir →", use_container_width=True, key=key):
            go(page)


def page_dashboard():
    render_sidebar()
    profile = st.session_state.user_profile  # référence directe (mutation de saved_metiers)
    tinder = st.session_state.user_data.get("tinder_profile", {}) or {}
    tastes = derived_tastes(profile, tinder)
    comp = profile_completion(profile, tinder)
    saved_metiers = profile.get("saved_metiers", [])
    saved_events = profile.get("saved_events", [])
    milestones = journey_milestones(profile, tinder, st.session_state.messages,
                                    saved_metiers, saved_events)
    current = next((m for m in milestones if m["state"] == "current"), None)

    name = profile.get("persona_label") or st.session_state.username or ""
    hi = f"Salut {html.escape(name)}" if name else "Salut"
    st.markdown(f'<div class="page-head"><div class="greet">{hi}<br>'
                f'voici <span class="em">où tu en es</span></div>'
                f'<div class="page-sub">Ta recherche d\'orientation, pilotée par ce qu\'ORI sait de toi.</div></div>',
                unsafe_allow_html=True)

    # ── Suivi de la démarche ──
    st.markdown('<div class="card-h">Ta démarche d\'orientation</div>', unsafe_allow_html=True)
    progress = journey_progress(milestones)
    cols = st.columns([1, 3])
    with cols[0]:
        st.markdown(progress_ring_svg(progress, size=96), unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f'<div class="ring-txt" style="margin-bottom:.4rem;"><b>{progress}% du parcours</b> · '
                    f'profil complété à {comp["pct"]}%</div>', unsafe_allow_html=True)
        if current:
            st.markdown(f'<div class="page-sub">Prochaine étape : <b>{html.escape(current["label"])}</b> — '
                        f'{html.escape(current["desc"])}.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="page-sub">Bravo, tu as bouclé toutes les étapes de la démarche !</div>',
                        unsafe_allow_html=True)
    milestone_stepper(milestones)
    if current and st.button(f"Continuer : {current['cta']} →", type="primary",
                             use_container_width=True, key="journey_cta"):
        go(current["page"])

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Recommandations ──
    st.markdown('<div class="section-h">Recommandé pour toi</div><div class="section-rule"></div>',
                unsafe_allow_html=True)
    if tastes["tags"] or tastes["liked"]:
        recos = _get_recos(profile, tastes)
        for i, card in enumerate(recos):
            metier_card(card)
            kept = card["title"] in saved_metiers
            label = "Gardé" if kept else "Garder cette piste"
            if st.button(label, key=f"keep_{i}", use_container_width=True, disabled=kept):
                profile.setdefault("saved_metiers", []).append(card["title"])
                persist_profile()
                st.rerun()
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Autres pistes", use_container_width=True, key="refresh_recos"):
                st.session_state.pop("dash_recos_key", None)
                st.rerun()
        with c2:
            if st.button("Découvrir en swipant", use_container_width=True, key="reco_swipe"):
                go("explore")
    else:
        st.markdown('<div class="note">ORI a besoin de te connaître pour recommander juste. '
                    'Commence par un swipe ou complète ton profil.</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Lancer un swipe", type="primary", use_container_width=True, key="empty_swipe"):
                go("explore")
        with c2:
            if st.button("Compléter mon profil", use_container_width=True, key="empty_profile"):
                go("profile")

    # ── Tes goûts ──
    if tastes["tags"] or tastes["liked"] or tastes["work_env"] or tastes["values"]:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="section-h">Tes goûts, vus par ORI</div><div class="section-rule"></div>',
                    unsafe_allow_html=True)
        rows = []
        if tastes["tags"]:
            rows.append(("Centres d'intérêt", tags_html(tastes["tags"], red=True)))
        if tastes["liked"]:
            rows.append(("Métiers qui t'attirent", tags_html(tastes["liked"][:8])))
        if tastes["work_env"]:
            rows.append(("Environnement de travail", tags_html(tastes["work_env"])))
        if tastes["values"]:
            rows.append(("Tes valeurs", tags_html(tastes["values"])))
        for h, t in rows:
            st.markdown(f'<div class="insight"><div class="insight-h">{h}</div>{t}</div>',
                        unsafe_allow_html=True)

    # ── Événements près de toi ──
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-h">Près de toi</div><div class="section-rule"></div>',
                unsafe_allow_html=True)
    ranked = match_events(EVENTS, profile, tinder)
    top = [r for r in ranked if r["match"] > 0][:2] or ranked[:2]
    if tastes["tags"]:
        st.markdown(f'<div class="card-hint">{len([r for r in ranked if r["match"] > 0])} '
                    f'événement(s) en lien avec tes intérêts.</div>', unsafe_allow_html=True)
    for r in top:
        event_card(r)
    if st.button("Voir tous les événements →", use_container_width=True, key="dash_to_events"):
        go("events")

    # ── Prochaines actions ──
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-h">Continuer avec ORI</div><div class="section-rule"></div>',
                unsafe_allow_html=True)
    a, b, c = st.columns(3)
    _cta(a, "", "Discuter", "Pose tes questions, lis des fiches métier.", "chat", "cta_chat")
    _cta(b, "", "Explorer", "Swipe métiers, valeurs et environnements.", "explore", "cta_explore")
    _cta(c, "", "Mon profil", "Affine ce qu'ORI sait de toi.", "profile", "cta_profile")
