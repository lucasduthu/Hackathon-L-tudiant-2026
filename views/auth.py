import streamlit as st
from utils import go, reset_session
from db import login_user, register_user, load_db
from ai import start_background_tinder_fetch


def _enter(username, user_record):
    st.session_state.logged_in = True
    st.session_state.guest = False
    st.session_state.username = username
    st.session_state.user_data = user_record
    st.session_state.user_profile = user_record.get("profile", {})
    st.session_state.messages = user_record.get("conversations", []) or []
    st.session_state.all_conversations = user_record.get("all_conversations", []) or []
    st.session_state.current_conv_id = None
    # Préchauffe le paquet de swipe en arrière-plan.
    start_background_tinder_fetch(username, st.session_state.user_profile, [], [], [], 10)


def page_auth():
    _, center, _ = st.columns([1, 5, 1])
    with center:
        mode = st.session_state.auth_mode
        title = "Connexion" if mode == "login" else "Créer un compte"
        sub = "Retrouve tes discussions et ton profil." if mode == "login" else "Sauvegarde ta progression avec ORI."

        st.markdown(
            f'<div class="hero" style="padding-bottom:.4rem;">'
            f'<div class="hero-title" style="font-size:2.4rem;">{title}</div>'
            f'<div class="hero-sub" style="margin-bottom:.6rem;">{sub}</div></div>',
            unsafe_allow_html=True,
        )

        with st.form("auth_form"):
            username = st.text_input("Nom d'utilisateur", placeholder="ex : marie.dupont")
            password = st.text_input("Mot de passe", type="password", placeholder="••••••••")
            email = pw2 = None
            if mode == "register":
                email = st.text_input("Email (optionnel)", placeholder="marie@example.com")
                pw2 = st.text_input("Confirmer le mot de passe", type="password", placeholder="••••••••")
            submitted = st.form_submit_button(
                "Se connecter" if mode == "login" else "Créer mon compte", use_container_width=True
            )

        if submitted:
            if not username or not password:
                st.error("Remplis le nom d'utilisateur et le mot de passe.")
            elif mode == "login":
                ok, result = login_user(username, password)
                if ok:
                    _enter(username, result)
                    go("dashboard")
                else:
                    st.error(result)
            else:
                if password != pw2:
                    st.error("Les mots de passe ne correspondent pas.")
                elif len(password) < 6:
                    st.error("Le mot de passe doit faire au moins 6 caractères.")
                else:
                    ok, msg = register_user(username, password, email or "")
                    if ok:
                        _enter(username, load_db()["users"][username])
                        go("dashboard")
                    else:
                        st.error(msg)

        other = "register" if mode == "login" else "login"
        other_label = "Pas encore de compte ? Créer un compte" if mode == "login" else "Déjà un compte ? Se connecter"
        if st.button(other_label, use_container_width=True, key="switch_mode"):
            st.session_state.auth_mode = other
            st.rerun()

        c1, c2 = st.columns(2)
        with c1:
            if st.button("← Accueil", use_container_width=True, key="back_home"):
                go("home")
        with c2:
            if st.button("Continuer sans compte →", use_container_width=True, key="guest_from_auth"):
                reset_session()
                st.session_state.guest = True
                go("dashboard")
