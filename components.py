import html
import math
from datetime import date

import streamlit as st

from utils import go, reset_session
from engine import profile_completion, derived_tastes, format_date_fr, _MONTHS_FR

LOGO_URL = "https://storage.letudiant.fr/build/gps/dist/assets/images/svg/logo/letudiant-white.svg"

# Onglets de navigation (clé de page, libellé).
NAV = [
    ("dashboard", "Accueil"),
    ("chat", "Chat ORI"),
    ("explore", "Explorer"),
    ("events", "Événements"),
    ("profile", "Profil"),
]


def render_nav(subtitle="Ton conseiller orientation IA"):
    st.markdown(
        f"""
        <div class="ori-nav">
          <div class="ori-nav-l">
            <span class="ori-mark">ORI</span>
            <img src="{LOGO_URL}" alt="L'Étudiant" />
            <span class="ori-pill">Beta</span>
          </div>
          <div class="ori-nav-r">{html.escape(subtitle)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_tabs(active):
    """Barre d'onglets cliquables. L'onglet actif est un bouton plein rouge (type primary)."""
    cols = st.columns(len(NAV))
    for col, (key, label) in zip(cols, NAV):
        with col:
            if st.button(label, key=f"tab_{key}", use_container_width=True,
                         type="primary" if key == active else "secondary"):
                if key != active:
                    go(key)
    st.markdown('<hr style="margin:.4rem 0 1rem;">', unsafe_allow_html=True)


# ── Petits composants visuels (HTML mono-ligne : cf. note metier_card) ─────────
def tags_html(items, red=False):
    cls = "ori-tag red" if red else "ori-tag"
    return "".join(f'<span class="{cls}">{html.escape(str(i))}</span>' for i in items if i)


def progress_ring_svg(pct, size=76):
    """Anneau de progression (string SVG, à intégrer dans un bloc HTML)."""
    pct = max(0, min(100, int(pct)))
    r = size / 2 - 7
    circ = 2 * math.pi * r
    dash = circ * pct / 100
    c = size / 2
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
        f'<circle cx="{c}" cy="{c}" r="{r:.1f}" fill="none" stroke="var(--le-grey-2)" stroke-width="7"/>'
        f'<circle cx="{c}" cy="{c}" r="{r:.1f}" fill="none" stroke="var(--le-red)" stroke-width="7" '
        f'stroke-linecap="round" stroke-dasharray="{dash:.1f} {circ:.1f}" transform="rotate(-90 {c} {c})"/>'
        f'<text x="50%" y="50%" text-anchor="middle" dy=".35em" class="ring-num">{pct}%</text>'
        f'</svg>'
    )


def milestone_stepper(steps):
    """Frise horizontale du suivi de la démarche (5 étapes done/current/todo)."""
    parts = ['<div class="stepper">']
    for i, s in enumerate(steps, 1):
        mark = "✓" if s["state"] == "done" else str(i)
        parts.append(
            f'<div class="step {s["state"]}">'
            f'<div class="dot">{mark}</div>'
            f'<span class="lbl">{html.escape(s["label"])}</span>'
            f'<span class="ds">{html.escape(s["desc"])}</span>'
            f'</div>'
        )
    parts.append('</div>')
    st.markdown("".join(parts), unsafe_allow_html=True)


def metier_card(card):
    """Carte fiche métier (titre, secteur, extrait, lien letudiant.fr). HTML mono-ligne :
    le parseur markdown de Streamlit laisse fuir des balises dès qu'un bloc HTML multi-lignes
    est « interrompu » par du contenu — le mono-ligne neutralise ce comportement."""
    title = html.escape(card.get("title", "Métier"))
    sector = html.escape(card.get("sector", ""))
    extract = html.escape(card.get("extract", ""))
    url = html.escape(card.get("url", "#"), quote=True)
    tag = f'<span class="metier-tag">{sector}</span>' if sector else ""
    desc = f'<div class="metier-desc">{extract}</div>' if extract else ""
    st.markdown(
        '<div class="metier-card">'
        '<div class="metier-top">'
        f'<div><div class="metier-title">{title}</div>{tag}</div>'
        '</div>'
        f'{desc}'
        f'<a class="metier-link" href="{url}" target="_blank" rel="noopener">Voir sur L\'Étudiant →</a>'
        '</div>',
        unsafe_allow_html=True,
    )


def swipe_card(card):
    """Carte du métier en cours de swipe (HTML mono-ligne)."""
    title = html.escape(card.get("title", "Métier"))
    kws = "".join(f'<span class="kw">{html.escape(k)}</span>' for k in card.get("keywords", []))
    st.markdown(
        '<div class="swipe-shell"><div class="swipe-card">'
        f'<div class="swipe-title">{title}</div>'
        f'<div class="swipe-kw">{kws}</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )


def event_card(row):
    """Carte d'un événement classé. row = {event, score, match}."""
    ev = row["event"]
    match = row.get("match", 0)
    try:
        d = date.fromisoformat(ev["date"])
        day, mon = d.day, _MONTHS_FR[d.month - 1].rstrip(".").upper()
    except (ValueError, TypeError, KeyError):
        day, mon = "", ""
    place = "En ligne" if ev.get("online") else f'{html.escape(ev.get("city", ""))}'
    badge = ('<span class="ev-badge">✦ Forte affinité</span>' if match >= 2
             else '<span class="ev-badge">✦ Pour toi</span>' if match == 1 else "")
    themes = tags_html(ev.get("themes", []))
    st.markdown(
        '<div class="ev-card">'
        f'<div class="ev-date"><div class="ev-day">{day}</div><div class="ev-mon">{mon}</div></div>'
        '<div class="ev-body">'
        f'<div class="ev-tags"><span class="ev-type">{html.escape(ev.get("type", ""))}</span>{badge}</div>'
        f'<div class="ev-title">{html.escape(ev.get("title", ""))}</div>'
        f'<div class="ev-meta">{format_date_fr(ev.get("date", ""))} · {place} · {html.escape(ev.get("org", ""))}</div>'
        f'<div class="ev-blurb">{html.escape(ev.get("blurb", ""))}</div>'
        f'<div>{themes}</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )


# ── Sidebar partagée : « Ce qu'ORI sait de toi » + compte ─────────────────────
def render_profile_sidebar():
    profile = st.session_state.user_profile or {}
    tinder = st.session_state.user_data.get("tinder_profile", {}) or {}
    comp = profile_completion(profile, tinder)
    tastes = derived_tastes(profile, tinder)

    st.markdown('<div class="side-h">Ce qu\'ORI sait de toi</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ring-wrap">'
        f'{progress_ring_svg(comp["pct"], size=64)}'
        f'<div class="ring-txt"><b>Profil {comp["pct"]}%</b><br>complété</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    base = [profile.get("persona_label"),
            profile.get("study_level") if profile.get("study_level") not in (None, "—") else None,
            profile.get("city")]
    base = [b for b in base if b]
    if base or tastes["tags"]:
        st.markdown(tags_html(base) + tags_html(tastes["tags"][:6], red=True), unsafe_allow_html=True)
    else:
        st.markdown('<div class="note">Complète ton profil ou swipe : ORI te connaîtra mieux.</div>',
                    unsafe_allow_html=True)

    if st.session_state.page != "profile":
        if st.button("Voir / compléter mon profil", use_container_width=True, key="side_to_profile"):
            go("profile")


def render_account_sidebar():
    st.markdown("<hr>", unsafe_allow_html=True)
    if st.session_state.logged_in:
        st.markdown(
            f'<div style="font-size:.8rem;color:var(--le-muted);">Connecté : '
            f'<b>{html.escape(st.session_state.username or "")}</b></div>',
            unsafe_allow_html=True,
        )
        if st.button("Se déconnecter", use_container_width=True, key="logout"):
            reset_session()
            go("home")
    else:
        st.markdown('<div class="note">Mode invité — ta progression ne sera pas sauvegardée.</div>',
                    unsafe_allow_html=True)
        if st.button("Créer un compte / Se connecter", use_container_width=True, key="to_auth"):
            go("auth")


def render_sidebar():
    """Sidebar standard (pages hors chat) : snapshot profil + compte."""
    with st.sidebar:
        render_profile_sidebar()
        render_account_sidebar()
