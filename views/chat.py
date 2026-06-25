"""Chat ORI : la conversation augmentée par le RAG (questions, fiches métier,
suggestions). Le swipe a sa page dédiée (Explorer) — ici on renvoie vers elle.
Le profil s'édite sur la page Profil ; la sidebar n'affiche qu'un snapshot + l'historique."""
import html
import re
import time
import unicodedata

import streamlit as st

from utils import go
from db import save_user_data
from components import metier_card, tags_html, render_profile_sidebar, render_account_sidebar
from data import PERSONA_LABELS
from ai import call_ori_api, suggest_metier_cards, retrieve_metier_fiches

_CLUELESS = ["je sais pas", "sais pas quoi", "sais pas du tout", "aucune idee",
             "je suis perdu", "sais vraiment pas", "je sais pas ou", "aucune idee de metier"]
_METIER_SIGNALS = ["metier", "fiche", "debouche", "salaire", "devenir", "travailler dans",
                   "etudes pour", "formation pour", "fait quoi", "consiste", "c est quoi le"]
_SECTOR_WORDS = ["informatique", "developpeur", "data", "intelligence artificielle", "infirmier",
                 "medecin", "sante", "marketing", "communication", "commerce", "vente", "droit",
                 "avocat", "ingenieur", "architecte", "environnement", "design", "journalisme",
                 "finance", "banque", "comptab", "enseignement", "professeur", "sport", "cuisine",
                 "tourisme", "mode", "psycholog", "biologie", "chimie", "mecanique", "art"]

_SWIPE_SUGG = {"label": "Découvrir en swipant", "action": {"intent": "goto", "page": "explore"},
               "echo": "Je veux explorer en swipant"}
_PISTES_SUGG = {"label": "Des pistes pour moi", "action": {"intent": "suggest"},
                "echo": "Propose-moi des pistes"}


# ── Helpers ───────────────────────────────────────────────────────────────────
def _norm(s):
    s = (s or "").lower()
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def _echo(label):
    return re.sub(r"^[\W_]+", "", label).strip()


def _say(content, block=None, suggestions=None):
    st.session_state.messages.append({
        "role": "assistant", "content": content,
        "block": block, "suggestions": suggestions or [],
    })


def _persist():
    """Sauvegarde les comptes (les invités restent en session)."""
    if not st.session_state.logged_in or not st.session_state.username:
        return
    msgs = st.session_state.messages
    convs = st.session_state.all_conversations
    if msgs:
        if not st.session_state.current_conv_id:
            st.session_state.current_conv_id = str(time.time())
        first_user = next((m["content"] for m in msgs if m["role"] == "user"), None)
        title = (first_user[:34] + "…") if first_user and len(first_user) > 34 else (first_user or "Nouvelle discussion")
        entry = next((c for c in convs if c["id"] == st.session_state.current_conv_id), None)
        if entry:
            entry["messages"], entry["title"] = msgs, title
        else:
            convs.append({"id": st.session_state.current_conv_id, "title": title, "messages": msgs})
    save_user_data(st.session_state.username, profile=st.session_state.user_profile,
                   conversations=msgs, all_conversations=convs)


# ── Onboarding & menus ─────────────────────────────────────────────────────────
def _seed():
    _say(
        "Salut. Je suis **ORI**, ton conseiller d'orientation L'Étudiant. "
        "Pour bien t'aider, dis-moi d'abord où tu en es :",
        suggestions=[
            {"label": "Au collège", "action": {"intent": "persona", "value": "collegien"}},
            {"label": "Au lycée", "action": {"intent": "persona", "value": "lyceen"}},
            {"label": "Étudiant·e", "action": {"intent": "persona", "value": "etudiant"}},
            {"label": "Parent", "action": {"intent": "persona", "value": "parent"}},
        ],
    )


def _menu_suggestions():
    return [
        _SWIPE_SUGG,
        {"label": "J'ai une idée de métier", "action": {"intent": "ask_metier"}, "echo": "J'ai une idée de métier"},
        _PISTES_SUGG,
        {"label": "Questions Parcoursup", "action": {"intent": "free", "text": "C'est quoi Parcoursup et quelles sont les dates clés à retenir ?"}, "echo": "Questions Parcoursup"},
    ]


# ── Traitement des intentions ───────────────────────────────────────────────────
def _process_pending():
    action = st.session_state.pending
    st.session_state.pending = None
    intent = action.get("intent")
    profile = st.session_state.user_profile

    if intent == "goto":
        _persist()
        go(action.get("page", "dashboard"))
        return

    if intent == "persona":
        profile["persona"] = action["value"]
        profile["persona_label"] = PERSONA_LABELS.get(action["value"], action["value"])
        _say("Parfait. Qu'est-ce qui t'amène aujourd'hui ?", suggestions=_menu_suggestions())

    elif intent == "ask_metier":
        _say("Dis-moi quel métier ou domaine t'intéresse — par exemple *développeur*, "
             "*infirmier*, *marketing*, *droit*… et je te sors les fiches L'Étudiant.")

    elif intent == "suggest":
        with st.spinner("ORI cherche des pistes pour toi…"):
            res = suggest_metier_cards(profile)
        cards = res.get("cards") or []
        if cards:
            _say("D'après ce que je sais de toi, voici 3 pistes à explorer :",
                 block={"type": "metiers", "cards": cards},
                 suggestions=[
                     {"label": "En savoir plus sur l'une", "action": {"intent": "ask_metier"}, "echo": "Parle-moi d'un de ces métiers"},
                     _SWIPE_SUGG,
                 ])
        else:
            _say("Je n'ai pas encore assez d'infos pour des pistes fiables. "
                 "On découvre quelques métiers en swipant pour démarrer ?",
                 suggestions=[_SWIPE_SUGG])

    elif intent == "free":
        _handle_free(action.get("text", ""))

    _persist()
    st.rerun()


def _handle_free(text):
    profile = st.session_state.user_profile
    low = _norm(text)

    if any(t in low for t in _CLUELESS):
        _say("Pas de souci, c'est hyper courant. Le plus simple : tu me dis ce qui t'attire "
             "en swipant quelques métiers dans **Explorer**. On y va ?",
             suggestions=[_SWIPE_SUGG, _PISTES_SUGG])
        return

    is_metier = any(s in low for s in _METIER_SIGNALS) or any(w in low for w in _SECTOR_WORDS)
    with st.spinner("ORI réfléchit…"):
        answer = call_ori_api(st.session_state.messages, profile)
        fiches = retrieve_metier_fiches(text, k=3) if is_metier else []

    block = {"type": "metiers", "cards": fiches} if fiches else None
    _say(answer, block=block, suggestions=[_SWIPE_SUGG, _PISTES_SUGG])


# ── Rendu des messages ───────────────────────────────────────────────────────
def _render_block(block):
    if not block:
        return
    if block.get("type") == "metiers":
        for c in block.get("cards", []):
            metier_card(c)
    elif block.get("type") == "swipe_result":  # rétro-compat anciennes conversations
        clusters = tags_html(block.get("clusters", []), red=True)
        liked = tags_html(block.get("liked", []))
        st.markdown(
            '<div class="metier-card">'
            '<div class="metier-tag">Ton profil de goûts</div>'
            f'<div style="margin:.4rem 0;">{clusters}</div>'
            '<div style="font-size:.78rem;color:var(--le-muted);margin:.3rem 0 .2rem;">Métiers que tu as aimés</div>'
            f'<div>{liked}</div>'
            '</div>',
            unsafe_allow_html=True,
        )


def _render_message(msg):
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant"):
            if msg.get("content"):
                st.markdown(msg["content"])
            _render_block(msg.get("block"))


def _fire(suggestion):
    st.session_state.messages.append({"role": "user", "content": suggestion.get("echo") or _echo(suggestion["label"])})
    st.session_state.pending = suggestion["action"]
    st.rerun()


def _render_chips(suggestions, anchor):
    st.markdown('<div class="chips-label">Réponses rapides</div>', unsafe_allow_html=True)
    for r in range(0, len(suggestions), 2):
        row = suggestions[r:r + 2]
        cols = st.columns(len(row))
        for j, (col, s) in enumerate(zip(cols, row)):
            with col:
                if st.button(s["label"], key=f"chip_{anchor}_{r + j}", use_container_width=True):
                    _fire(s)


# ── Sidebar (snapshot profil + historique) ─────────────────────────────────────
def _new_conversation():
    _persist()
    st.session_state.messages = []
    st.session_state.current_conv_id = None
    st.session_state.pending = None
    st.rerun()


def _sidebar():
    with st.sidebar:
        render_profile_sidebar()
        if st.session_state.logged_in:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown('<div class="side-h">Mes discussions</div>', unsafe_allow_html=True)
            if st.button("＋ Nouvelle discussion", use_container_width=True, key="new_conv"):
                _new_conversation()
            for conv in reversed(st.session_state.all_conversations):
                active = conv["id"] == st.session_state.current_conv_id
                if st.button(("● " if active else "  ") + conv["title"], use_container_width=True,
                             key=f"conv_{conv['id']}", type="primary" if active else "secondary"):
                    _persist()
                    st.session_state.current_conv_id = conv["id"]
                    st.session_state.messages = conv["messages"]
                    st.rerun()
        render_account_sidebar()


# ── Page ────────────────────────────────────────────────────────────────────
def page_chat():
    _sidebar()

    if not st.session_state.messages:
        _seed()

    for msg in st.session_state.messages:
        _render_message(msg)

    if st.session_state.pending is not None:
        _process_pending()
    else:
        last = st.session_state.messages[-1] if st.session_state.messages else None
        if last and last["role"] == "assistant" and last.get("suggestions"):
            _render_chips(last["suggestions"], anchor=len(st.session_state.messages))

    text = st.chat_input("Écris à ORI…")
    if text:
        st.session_state.messages.append({"role": "user", "content": text})
        st.session_state.pending = {"intent": "free", "text": text}
        st.rerun()
