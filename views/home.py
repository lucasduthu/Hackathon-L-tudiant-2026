import streamlit as st
from utils import go, reset_session


def _start_guest():
    reset_session()
    st.session_state.guest = True
    go("dashboard")


def page_home():
    st.markdown(
        """
        <div class="hero">
          <span class="eyebrow">Orientation propulsée par l'IA</span>
          <div class="hero-title">Trouve ta voie,<br><span class="em">étape par étape</span></div>
          <div class="hero-sub">
            ORI apprend à te connaître, suit ta démarche et te guide : recommandations,
            chat sourcé sur L'Étudiant, découverte par le swipe et événements près de toi.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Démarrer avec ORI", type="primary", use_container_width=True, key="cta_guest"):
            _start_guest()
    with col2:
        if st.button("J'ai déjà un compte", use_container_width=True, key="cta_login"):
            st.session_state.auth_mode = "login"
            go("auth")

    st.markdown(
        """
        <div class="trust">
          <span><b>100 % local</b> · aucune donnée envoyée</span>
          <span><b>300+</b> fiches L'Étudiant</span>
          <span><b>Sans inscription</b></span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-h">Ton espace orientation</div><div class="section-rule"></div>',
                unsafe_allow_html=True)

    feats = [
        ("Un dashboard qui te suit", "Tes recommandations et ta démarche d'orientation, au même endroit."),
        ("Chat ORI sourcé", "Parcoursup, débouchés, formations… ORI répond, appuyé sur L'Étudiant."),
        ("Le swipe qui te révèle", "Métiers, valeurs, environnement : découvre tes goûts en swipant."),
        ("Des événements pour toi", "Salons, JPO et webinaires près de chez toi, selon tes intérêts."),
    ]
    cols = st.columns(2)
    for i, (h, p) in enumerate(feats):
        with cols[i % 2]:
            st.markdown(
                f'<div class="feat" style="margin-bottom:.8rem;">'
                f'<div class="feat-h">{h}</div><div class="feat-p">{p}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown(
        '<div class="ori-foot">ORI — L\'Étudiant × Albert School · Alberthon 2026 · Groupe 08</div>',
        unsafe_allow_html=True,
    )
