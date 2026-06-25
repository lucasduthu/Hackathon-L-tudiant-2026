"""Profil : la colonne vertébrale de l'app. L'utilisateur déclare qui il est et
ce qu'il vise ; ORI affiche aussi ce qu'il a déduit des swipes. Tout le reste de
l'app (dashboard, recommandations, événements) lit ce profil."""
import streamlit as st

from utils import go, persist_profile
from components import render_sidebar, progress_ring_svg, tags_html
from engine import profile_completion, derived_tastes, has_intent
from data import PERSONA_LABELS, NIVEAUX, INTERESTS, SECTEURS, CITIES, TIMELINES


def page_profile():
    render_sidebar()
    profile = st.session_state.user_profile
    tinder = st.session_state.user_data.get("tinder_profile", {}) or {}
    comp = profile_completion(profile, tinder)
    tastes = derived_tastes(profile, tinder)
    fresh = not profile.get("persona")

    st.markdown('<div class="page-head"><span class="page-eyebrow">Ton profil</span>'
                '<div class="greet">Ce qu\'ORI <span class="em">sait de toi</span></div>'
                '<div class="page-sub">Plus ORI te connaît, plus ses conseils sont justes. '
                'Tu peux tout modifier ici.</div></div>', unsafe_allow_html=True)

    if fresh:
        st.markdown('<div class="note">On fait connaissance ? Renseigne au moins ton statut, '
                    'ta ville et tes centres d\'intérêt pour démarrer.</div>', unsafe_allow_html=True)

    # ── Complétion ──
    cols = st.columns([1, 3])
    with cols[0]:
        st.markdown(progress_ring_svg(comp["pct"], size=92), unsafe_allow_html=True)
    with cols[1]:
        if comp["missing"]:
            st.markdown(f'<div class="ring-txt"><b>Profil complété à {comp["pct"]}%</b><br>'
                        f'Il manque : {", ".join(comp["missing"])}.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="ring-txt"><b>Profil complet</b><br>'
                        'ORI a tout ce qu\'il faut pour t\'orienter finement.</div>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Formulaire ──
    persona_keys = list(PERSONA_LABELS)
    cur_persona = profile.get("persona")
    tl_keys = list(TIMELINES)
    cur_tl = profile.get("timeline") if profile.get("timeline") in TIMELINES else "exploring"

    with st.form("profile_form"):
        st.markdown('<div class="card-h">Qui es-tu ?</div>', unsafe_allow_html=True)
        persona = st.radio("Je suis…", persona_keys,
                           index=persona_keys.index(cur_persona) if cur_persona in persona_keys else 2,
                           format_func=lambda k: PERSONA_LABELS[k], horizontal=True)
        c1, c2 = st.columns(2)
        with c1:
            niveau = st.selectbox("Niveau d'études", NIVEAUX,
                                  index=NIVEAUX.index(profile["study_level"])
                                  if profile.get("study_level") in NIVEAUX else 0)
            city = st.selectbox("Ma ville", ["—"] + CITIES,
                                index=(["—"] + CITIES).index(profile["city"])
                                if profile.get("city") in CITIES else 0)
        with c2:
            specialty = st.text_input("Filière / spécialité", value=profile.get("specialty", ""),
                                      placeholder="ex : Terminale STMG, L1 éco-gestion…")
            timeline = st.selectbox("Mon échéance", tl_keys, index=tl_keys.index(cur_tl),
                                    format_func=lambda k: TIMELINES[k])

        st.markdown('<div class="card-h" style="margin-top:.6rem;">Ce qui t\'intéresse</div>',
                    unsafe_allow_html=True)
        interests = st.multiselect("Centres d'intérêt", INTERESTS,
                                   default=[x for x in tastes["interests"] if x in INTERESTS])
        sectors = st.multiselect("Secteurs visés", SECTEURS,
                                 default=[x for x in profile.get("target_sectors", []) if x in SECTEURS])
        intent = st.text_area("Mon objectif / là où j'en suis",
                              value=profile.get("intent", "") if has_intent(profile) else "",
                              placeholder="ex : J'hésite entre la tech et la finance…", height=80)

        if st.form_submit_button("Enregistrer mon profil", type="primary", use_container_width=True):
            profile["persona"] = persona
            profile["persona_label"] = PERSONA_LABELS[persona]
            profile["study_level"] = niveau
            profile["city"] = "" if city == "—" else city
            profile["specialty"] = specialty.strip()
            profile["timeline"] = timeline
            
            # Conserver les centres d'intérêt déduits (ceux hors de INTERESTS) pour éviter la suppression
            old_interests = profile.get("interests", [])
            swiped_interests = [x for x in old_interests if x not in INTERESTS]
            profile["interests"] = list(dict.fromkeys(interests + swiped_interests))
            
            profile["target_sectors"] = sectors
            profile["intent"] = intent.strip()
            persist_profile()
            st.session_state.pop("dash_recos_key", None)  # force le recalcul des recos
            st.toast("Profil enregistré")  # survit au rerun (contrairement à st.success)
            st.rerun()

    # ── Insights déduits des swipes ──
    if tastes["clusters"] or tastes["liked"] or tastes["work_env"] or tastes["values"]:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="section-h">Déduit de tes swipes</div><div class="section-rule"></div>',
                    unsafe_allow_html=True)
        blocks = [("Univers de prédilection", tastes["clusters"], True),
                  ("Métiers qui t'attirent", tastes["liked"][:10], False),
                  ("Environnement de travail", tastes["work_env"], False),
                  ("Tes valeurs", tastes["values"], False)]
        for h, items, red in blocks:
            if items:
                st.markdown(f'<div class="insight"><div class="insight-h">{h}</div>'
                            f'{tags_html(items, red=red)}</div>', unsafe_allow_html=True)
        if st.button("Continuer à explorer", use_container_width=True, key="profile_to_explore"):
            go("explore")
    elif not fresh:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="note">Tu n\'as pas encore swipé. Le mode Explorer affine ton profil '
                    'avec tes goûts réels (métiers, valeurs, environnement).</div>', unsafe_allow_html=True)
        if st.button("Lancer un swipe", use_container_width=True, key="profile_to_explore2"):
            go("explore")
