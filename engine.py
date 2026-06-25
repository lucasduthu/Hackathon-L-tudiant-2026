"""Logique métier pure (sans IA, sans Streamlit) : connaissance de l'utilisateur.

Toute l'app gravite autour du profil. Ce module centralise les calculs dérivés du
profil pour que les vues restent fines : complétion, suivi de la démarche (parcours)
et matching d'événements. Fonctions pures et défensives (tolèrent les anciens profils
de data/users.json où certains champs manquent).
"""
from datetime import date

_MONTHS_FR = ["janv.", "févr.", "mars", "avr.", "mai", "juin",
              "juil.", "août", "sept.", "oct.", "nov.", "déc."]

# Objectifs « vides » trouvés dans les anciens profils → considérés comme non renseignés.
_INTENT_PLACEHOLDERS = {"", "pas de précision.", "pas de précision", "aucune", "—"}


def _nonempty(x):
    return bool(x) and (not isinstance(x, str) or x.strip())


def derived_tastes(profile, tinder):
    """Unifie centres d'intérêt déclarés (profil) et goûts déduits (swipes Tinder)."""
    profile = profile or {}
    tinder = tinder or {}
    interests = [i for i in (profile.get("interests") or []) if i]
    clusters = [c for c in (tinder.get("clusters") or []) if c]
    liked = [l for l in (tinder.get("liked_careers") or []) if l]
    work_env = [w for w in (tinder.get("work_environment") or []) if w]
    values = [v for v in (tinder.get("values") or []) if v]
    sectors = list(dict.fromkeys(
        [s for s in (profile.get("target_sectors") or []) if s]
        + [s for s in (tinder.get("sectors") or []) if s]
    ))
    # Tags de goût pour le matching (intérêts déclarés + clusters déduits).
    tags = list(dict.fromkeys(interests + clusters))
    return {
        "interests": interests, "clusters": clusters, "liked": liked,
        "work_env": work_env, "values": values, "sectors": sectors, "tags": tags,
    }


def has_explored(tinder):
    """L'utilisateur a-t-il déjà swipé au moins une thématique ?"""
    tinder = tinder or {}
    return any(_nonempty(tinder.get(k)) for k in
               ("clusters", "liked_careers", "work_environment", "values", "sectors"))


def has_intent(profile):
    intent = (profile or {}).get("intent", "")
    return _nonempty(intent) and intent.strip().lower() not in _INTENT_PLACEHOLDERS


def profile_completion(profile, tinder):
    """Score de complétion du profil (0-100) + liste des éléments manquants.

    Chaque signal renseigné rapproche d'une recherche d'orientation personnalisée.
    """
    profile = profile or {}
    checks = [
        ("Ton statut", _nonempty(profile.get("persona"))),
        ("Ton niveau d'études", _nonempty(profile.get("study_level")) and profile.get("study_level") != "—"),
        ("Ta ville", _nonempty(profile.get("city"))),
        ("Tes centres d'intérêt", _nonempty(profile.get("interests"))),
        ("Tes secteurs visés", _nonempty(profile.get("target_sectors"))),
        ("Ton objectif", has_intent(profile)),
        ("Un premier swipe", has_explored(tinder)),
    ]
    done = sum(1 for _, ok in checks if ok)
    pct = round(done / len(checks) * 100)
    missing = [label for label, ok in checks if not ok]
    return {"pct": pct, "done": done, "total": len(checks), "missing": missing}


def journey_milestones(profile, tinder, conversations, saved_metiers=None, saved_events=None):
    """Les 5 étapes de la démarche d'orientation, avec leur état.

    state ∈ {done, current, todo} : « current » = première étape non terminée.
    Chaque étape porte un deep-link (page) et un libellé de CTA.
    """
    profile = profile or {}
    saved_metiers = saved_metiers or []
    saved_events = saved_events or []
    has_chatted = any(m.get("role") == "user" for m in (conversations or []))
    liked = (tinder or {}).get("liked_careers") or []

    specs = [
        ("present", "Se présenter", "Dis à ORI qui tu es",
         "profile", "Compléter mon profil",
         _nonempty(profile.get("persona")) and (
             (profile.get("study_level") not in (None, "", "—")) or _nonempty(profile.get("city")))),
        ("explore", "Explorer tes goûts", "Swipe des métiers et des univers",
         "explore", "Lancer un swipe",
         has_explored(tinder) or _nonempty(profile.get("interests"))),
        ("target", "Cibler des métiers", "Garde les pistes qui t'attirent",
         "explore", "Découvrir des métiers",
         _nonempty(saved_metiers) or _nonempty(liked)),
        ("deepen", "Approfondir avec ORI", "Pose tes questions, lis les fiches",
         "chat", "Discuter avec ORI",
         has_chatted),
        ("act", "Passer à l'action", "Repère un événement près de toi",
         "events", "Voir les événements",
         _nonempty(saved_events)),
    ]

    milestones, current_assigned = [], False
    for key, label, desc, page, cta, done in specs:
        if done:
            state = "done"
        elif not current_assigned:
            state, current_assigned = "current", True
        else:
            state = "todo"
        milestones.append({"key": key, "label": label, "desc": desc,
                           "page": page, "cta": cta, "state": state})
    return milestones


def journey_progress(milestones):
    """% d'étapes terminées."""
    if not milestones:
        return 0
    done = sum(1 for m in milestones if m["state"] == "done")
    return round(done / len(milestones) * 100)


# ── Événements ────────────────────────────────────────────────────────────────
def format_date_fr(iso):
    try:
        d = date.fromisoformat(iso)
    except (ValueError, TypeError):
        return iso or ""
    return f"{d.day} {_MONTHS_FR[d.month - 1]} {d.year}"


def match_events(events, profile, tinder, filters=None):
    """Classe les événements par affinité avec le profil, après filtrage.

    Retourne une liste de dicts {event, score, match} triée par (score desc, date asc).
    `match` = nombre de recouvrements thèmes+secteurs (sert au badge « affinité »).
    filters : {city, theme, fmt} ; valeur "Tout" / None = pas de filtre.
    """
    filters = filters or {}
    tastes = derived_tastes(profile, tinder)
    # Comparaison insensible à la casse : les clusters issus du swipe métiers sont en
    # minuscules libres (« communication »), les thèmes d'événements en casse titre.
    user_themes = {t.lower() for t in tastes["tags"]}
    user_sectors = {s.lower() for s in tastes["sectors"]}
    home_city = (profile or {}).get("city")

    fcity = filters.get("city")
    ftheme = filters.get("theme")
    ffmt = filters.get("fmt")  # "Présentiel" | "En ligne" | None/"Tout"
    today = date.today()

    rows = []
    for ev in events:
        if fcity and fcity != "Tout" and ev["city"] != fcity:
            continue
        if ftheme and ftheme != "Tout" and ftheme not in ev.get("themes", []):
            continue
        if ffmt == "En ligne" and not ev.get("online"):
            continue
        if ffmt == "Présentiel" and ev.get("online"):
            continue

        theme_hits = user_themes & {t.lower() for t in ev.get("themes", [])}
        sector_hits = user_sectors & {s.lower() for s in ev.get("sectors", [])}
        match = len(theme_hits) + len(sector_hits)
        score = 3 * len(theme_hits) + 2 * len(sector_hits)
        if home_city and ev["city"] == home_city:
            score += 2
        elif ev.get("online"):
            score += 1
        try:
            if 0 <= (date.fromisoformat(ev["date"]) - today).days <= 90:
                score += 1
        except (ValueError, TypeError, KeyError):
            pass
        rows.append({"event": ev, "score": score, "match": match})

    rows.sort(key=lambda r: (-r["score"], r["event"].get("date", "")))
    return rows
