"""Couche IA : RAG local sur letudiant.fr + génération avec gemma3:1b via Ollama.

Les signatures publiques sont conservées pour que les vues n'aient pas à changer :
call_ori_api, get_ai_suggestions, get_tinder_suggestions_ai,
start_background_tinder_fetch, get_prefetched_tinder_cards, is_tinder_fetching.
"""
import json
import random
import re
import threading
import time
import unicodedata
import urllib.parse

from rag import ollama_client
from rag.index import get_retriever
from data import TINDER_CAREERS

ORI_PERSONA = (
    "Tu es ORI, un conseiller d'orientation chaleureux, expert et bienveillant pour des "
    "étudiants français. Tu réponds toujours en français, de façon claire et concrète. "
    "Quand le contexte issu de l'Etudiant.fr est fourni, appuie-toi dessus et reste fidèle "
    "à ces informations ; sinon réponds avec tes connaissances générales sans inventer de chiffres."
)

# Schémas de sortie structurée : Ollama force un JSON valide conforme (décodage contraint).
_SUGGESTIONS_SCHEMA = {
    "type": "object",
    "properties": {
        "suggestions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "metier": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["metier", "description"],
            },
        }
    },
    "required": ["suggestions"],
}

_TINDER_SCHEMA = {
    "type": "object",
    "properties": {
        "suggestions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "emoji": {"type": "string"},
                    "keywords": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["title", "emoji", "keywords"],
            },
        }
    },
    "required": ["suggestions"],
}


# ── Helpers ──────────────────────────────────────────────────────────────────
def _retrieve(query, k=None):
    try:
        return get_retriever().search(query, k=k)
    except Exception:
        return []


def _format_context(hits):
    if not hits:
        return ""
    blocks = [f"Source : {h['title']} ({h['url']})\n{h['text']}" for h in hits]
    return "\n\n---\n\n".join(blocks)


def _extract_json(text):
    """Extrait le premier objet/array JSON d'une réponse de LLM (tolère markdown et bavardage)."""
    text = (text or "").strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    starts = [s for s in (text.find("{"), text.find("[")) if s != -1]
    if starts:
        try:
            obj, _ = json.JSONDecoder().raw_decode(text[min(starts):])
            return obj
        except json.JSONDecodeError:
            pass
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


# ── Chat ─────────────────────────────────────────────────────────────────────
def call_ori_api(messages, user_profile):
    """Répond au dernier message de l'utilisateur en tant qu'ORI, augmenté par le RAG."""
    if not messages:
        return "Bonjour ! Je suis ORI, ton conseiller d'orientation. Comment puis-je t'aider ?"

    last_user_message = next(
        (m["content"] for m in reversed(messages) if m["role"] == "user"), "Bonjour"
    )
    context = _format_context(_retrieve(last_user_message))
    profile_summary = json.dumps(user_profile, ensure_ascii=False) if user_profile else "{}"
    history = "\n".join(
        f"{'Élève' if m['role'] == 'user' else 'ORI'} : {m['content']}" for m in messages[-6:]
    )

    prompt = (
        (f"Contexte issu de l'Etudiant.fr :\n{context}\n\n" if context else "")
        + f"Profil de l'élève : {profile_summary}\n\n"
        + f"Conversation :\n{history}\n\n"
        + "Réponds au dernier message de l'élève en tant qu'ORI."
    )

    try:
        return ollama_client.generate(prompt, system=ORI_PERSONA)
    except ollama_client.OllamaError:
        return ("Je n'arrive pas à joindre le modèle local (Ollama). "
                "Vérifie qu'Ollama tourne (`ollama serve`) puis réessaie.")


# ── Suggestions de métiers (« Des pistes pour moi ») ─────────────────────────
def get_ai_suggestions(user_profile):
    """Suggère 3 métiers au format {"suggestions": [{"metier", "description"}]}."""
    profile_summary = json.dumps(user_profile, ensure_ascii=False) if user_profile else "{}"
    interests = " ".join(user_profile.get("interests", [])) if user_profile else ""
    context = _format_context(_retrieve(f"métiers et formations pour un profil intéressé par {interests}".strip()))

    prompt = (
        (f"Contexte issu de l'Etudiant.fr :\n{context}\n\n" if context else "")
        + f"Profil de l'étudiant : {profile_summary}. "
        "Suggère 3 métiers pertinents pour ce profil, avec une très courte explication pour chacun."
    )

    last_error = None
    for _ in range(3):
        try:
            resp = ollama_client.generate(prompt, system=ORI_PERSONA, temperature=0.5, fmt=_SUGGESTIONS_SCHEMA)
        except ollama_client.OllamaError as e:
            last_error = e
            time.sleep(1)
            continue
        obj = _extract_json(resp)
        if isinstance(obj, dict) and obj.get("suggestions"):
            return obj
        if isinstance(obj, list) and obj:
            return {"suggestions": obj}

    if last_error is not None:
        return {"error": str(last_error), "suggestions": []}
    return {"suggestions": [
        {"metier": "Data Analyst", "description": "L'IA n'a pas pu générer les suggestions correctement."},
        {"metier": "Développeur", "description": "Réessaie pour obtenir des suggestions personnalisées."},
    ]}


# ── Suggestions « mode Tinder » ──────────────────────────────────────────────
def get_tinder_suggestions_ai(user_profile, seen_metiers, liked_metiers, disliked_metiers, batch_size=3):
    """Génère des cartes métiers au format {"suggestions": [{"title", "emoji", "keywords"}]}."""
    profile_summary = json.dumps(user_profile, ensure_ascii=False) if user_profile else "{}"
    seen_list = ", ".join(seen_metiers) if seen_metiers else "Aucun"
    liked_list = ", ".join(liked_metiers) if liked_metiers else "Aucun"
    disliked_list = ", ".join(disliked_metiers) if disliked_metiers else "Aucun"
    context = _format_context(_retrieve(f"métiers variés pour un profil aimant {liked_list}"))

    prompt = (
        (f"Contexte issu de l'Etudiant.fr :\n{context}\n\n" if context else "")
        + f"Tu es ORI. Profil de l'étudiant : {profile_summary}. "
        "Il découvre des métiers façon 'Tinder'. "
        f"Métiers déjà vus : {seen_list}. Aimés : {liked_list}. Non aimés : {disliked_list}. "
        f"Génère {batch_size} NOUVELLES suggestions de métiers originaux et pertinents, en tenant compte "
        "de ses goûts, sans répéter les métiers déjà vus. Chaque métier a un titre, un emoji et 3 mots-clés."
    )

    last_error = None
    for attempt in range(3):
        try:
            resp = ollama_client.generate(prompt, system=ORI_PERSONA, temperature=0.7, fmt=_TINDER_SCHEMA)
            obj = _extract_json(resp)
            if isinstance(obj, dict) and obj.get("suggestions"):
                return obj
            if isinstance(obj, list) and obj:
                return {"suggestions": obj}
        except ollama_client.OllamaError as e:
            last_error = e
            time.sleep(1)

    if last_error is not None:
        return {"error": str(last_error), "suggestions": []}
    return {"suggestions": [
        {"title": "Data Analyst", "emoji": "", "keywords": ["Données", "Statistiques", "Insights"]},
        {"title": "Designer", "emoji": "", "keywords": ["Créativité", "Design", "Art"]},
    ]}


# ── Préchargement en arrière-plan des cartes Tinder ──────────────────────────
user_tinder_queues = {}


def background_fetch_cards(username, user_profile, seen, liked, disliked, count=30):
    queue = user_tinder_queues.setdefault(username, {"cards": [], "is_fetching": False})
    queue["is_fetching"] = True
    try:
        new_cards = get_tinder_suggestions_ai(user_profile, seen, liked, disliked, batch_size=count)
        if new_cards and "suggestions" in new_cards:
            queue["cards"].extend(new_cards["suggestions"])
    finally:
        queue["is_fetching"] = False


def start_background_tinder_fetch(username, user_profile, seen_metiers, liked_metiers, disliked_metiers, count=30):
    """Démarre un thread de préchargement des cartes Tinder."""
    queue = user_tinder_queues.setdefault(username, {"cards": [], "is_fetching": False})
    if not queue["is_fetching"]:
        threading.Thread(
            target=background_fetch_cards,
            args=(username, user_profile, seen_metiers, liked_metiers, disliked_metiers, count),
            daemon=True,
        ).start()


def get_prefetched_tinder_cards(username):
    """Récupère et vide les cartes préchargées pour un utilisateur."""
    queue = user_tinder_queues.get(username)
    if queue and queue["cards"]:
        cards = queue["cards"]
        queue["cards"] = []
        return cards
    return []


def is_tinder_fetching(username):
    """Indique si un préchargement est en cours pour cet utilisateur."""
    return user_tinder_queues.get(username, {}).get("is_fetching", False)


# ═══════════════════════════════════════════════════════════════════════════════
#  Couche d'orchestration conversationnelle (ORI agentique)
#  Compose les primitives ci-dessus pour la nouvelle UX "tout dans le chat".
# ═══════════════════════════════════════════════════════════════════════════════

# Emoji par secteur (cartes fiches métier).
_SECTOR_EMOJI = [
    (("intelligence-artificielle", "data", " ia "), ""),
    (("sante", "medecine", "medical", "soin", "infirm"), ""),
    (("informatique", "web", "telecom", "developp", "numerique", "cyber"), ""),
    (("marketing", "publicite", "communication", "media"), ""),
    (("batiment", "travaux", "architecte", "construction"), ""),
    (("art", "culture", "mode", "creation", "design", "graph"), ""),
    (("droit", "justice", "avocat", "juridique"), ""),
    (("environnement", "ecolo", "energie", "nature"), ""),
    (("agriculture", "agroalimentaire", "animal", "vivant"), ""),
    (("armee", "defense", "militaire", "securite"), ""),
    (("commerce", "vente", "distribution"), ""),
    (("finance", "banque", "comptab", "gestion", "assurance"), ""),
    (("enseignement", "education", "formation", "professeur"), ""),
    (("ingenieur", "industrie", "mecanique", "production"), ""),
    (("transport", "ferroviaire", "logistique", "aerien"), ""),
    (("tourisme", "hotellerie", "restauration", "cuisine"), ""),
    (("sport", "animation"), ""),
    (("immobilier",), ""),
]

_FICHE_RE = re.compile(r"/metiers/secteur/[^/]+/[^/]+\.html")
_SECTOR_RE = re.compile(r"/metiers/secteur/([^/]+)/")

# Mots génériques qui « polluent » l'embedding (toutes les fiches partagent ce gabarit).
_STOP = set(
    "le la les un une des du de d l a au aux et ou que qui quoi quel quelle quels quelles "
    "comment pourquoi pour est ce c sur dans avec mon ma mes ton ta tes son sa ses en au "
    "je tu il elle on nous vous ils metier metiers fiche fiches mission missions salaire "
    "salaires etude etudes formation formations debouche debouches devenir travailler faire "
    "fait consiste secteur domaine apres bac veux aimerais".split()
)


def _deacc(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def _focus_query(text):
    """Garde les mots porteurs de sens (le terme métier) pour une recherche RAG ciblée."""
    toks = re.findall(r"[a-zà-ÿ]+", (text or "").lower())
    kept = [t for t in toks if len(t) > 1 and _deacc(t) not in _STOP]
    return " ".join(kept)


def _search_url(label):
    return "https://www.letudiant.fr/recherche.html?query=" + urllib.parse.quote_plus(label)


def _emoji_for(blob):
    blob = (blob or "").lower()
    for keys, emo in _SECTOR_EMOJI:
        if any(k in blob for k in keys):
            return emo
    return ""


def _sector_from_url(url):
    m = _SECTOR_RE.search(url or "")
    if not m:
        return ""
    raw = m.group(1).replace("--", "-").replace("-", " ").strip()
    return raw[:1].upper() + raw[1:] if raw else ""


def _clean_title(title):
    t = (title or "").split(" - Découvrez")[0]
    t = t.split(" | ")[0]
    for junk in (" - L'Etudiant", " - L’Etudiant", " - Letudiant.fr"):
        t = t.replace(junk, "")
    return t.strip(" \"'’")


# Boilerplate de navigation/partage scrapé sur letudiant.fr (pollue les extraits).
_BOILER = re.compile(
    r"(Partager sur \w+|Partager|Publicité|Copié|Chargement|Toujours un nouveau test|©\s*[\w./\-]+)",
    re.I,
)


def _short(text, n=190):
    t = re.sub(r"\s+", " ", text or "").strip()
    t = _BOILER.sub("", t)
    t = re.sub(r"\s{2,}", " ", t).strip(" ·-—|>")
    # Un chunk peut démarrer au milieu d'un mot : on retire le fragment initial.
    if t[:1].islower() and " " in t:
        t = t.split(" ", 1)[1]
    if t:
        t = t[0].upper() + t[1:]
    if len(t) <= n:
        return t
    return t[:n].rsplit(" ", 1)[0].rstrip(",.;: ") + "…"


def retrieve_metier_fiches(query, k=3):
    """Renvoie des fiches métier réelles (issues du corpus letudiant.fr) prêtes à afficher.

    Chaque fiche : {title, sector, emoji, extract, url}. Dédupliquées par URL,
    fiches individuelles priorisées sur les pages d'index.
    """
    focus = _focus_query(query) or query
    hits = _retrieve(focus, k=30)
    
    focus_toks = [t for t in re.findall(r"[a-z]+", _deacc(focus.lower())) if len(t) >= 4]
    filtered_hits = []
    
    if hits and focus_toks:
        filtered_hits = [h for h in hits
                         if any(t in _deacc((h.get("title", "") + " " + h.get("text", "")).lower())
                                for t in focus_toks)]
                                
    # Fallback classique si aucun résultat n'a passé le filtre lexical vectoriel
    if not filtered_hits and focus_toks:
        retriever = get_retriever()
        if retriever.ready:
            for chunk in retriever.chunks:
                title_text_lower = _deacc((chunk.get("title", "") + " " + chunk.get("text", "")).lower())
                if any(t in title_text_lower for t in focus_toks):
                    filtered_hits.append(chunk)
                    if len(filtered_hits) >= 30:
                        break

    if not filtered_hits:
        return []

    def _rank(h):
        u = h.get("url", "")
        if _FICHE_RE.search(u):
            return 0                      # vraie fiche métier → priorité
        if "/test/" in u:
            return 3                      # quiz d'orientation → en dernier
        if u.rstrip("/").endswith(("metiers.html", "etudes.html")):
            return 4                      # pages d'index → exclues si possible
        return 1
    ordered = sorted(filtered_hits, key=_rank)     # tri stable : conserve l'ordre par score

    fiches, seen = [], set()
    for h in ordered:
        url = h.get("url", "")
        if not url or url in seen:
            continue
        seen.add(url)
        fiches.append({
            "title": _clean_title(h.get("title", "")) or "Fiche métier",
            "sector": _sector_from_url(url),
            "emoji": _emoji_for(url + " " + h.get("title", "")),
            "extract": _short(h.get("text", "")),
            "url": url,
        })
        if len(fiches) >= k:
            break
    return fiches


def resolve_fiche_url(metier):
    """URL de la vraie fiche métier L'Étudiant correspondant à un intitulé.

    Réutilise le retrieval RAG (comme le chat) et n'accepte qu'une vraie fiche
    individuelle (`_FICHE_RE`) dont le titre/slug recoupe l'intitulé — garde-fou
    anti-faux-positif, surtout quand le repli lexical hors-ligne (Ollama éteint)
    est imprécis. Repli sur la page de recherche si rien de fiable.
    """
    stems = [t[:5] for t in re.findall(r"[a-z]+", _deacc(metier.lower())) if len(t) >= 4]
    for fiche in retrieve_metier_fiches(metier, k=3):
        url = fiche.get("url", "")
        if not _FICHE_RE.search(url):
            continue
        # Titre + nom de fichier seulement (pas le segment secteur du chemin, qui
        # créerait de faux positifs : « Commercial » ⊂ « commerce-distribution »).
        slug = _deacc((fiche.get("title", "") + " " + url.rsplit("/", 1)[-1]).lower())
        if not stems or any(s in slug for s in stems):
            return url
    return _search_url(metier)


def suggest_metier_cards(user_profile, k=3):
    """3 métiers personnalisés (get_ai_suggestions) enrichis pour l'affichage en cartes."""
    data = get_ai_suggestions(user_profile)
    out = []
    for s in (data.get("suggestions") or [])[:k]:
        metier = s.get("metier", "").strip()
        if not metier:
            continue
        out.append({
            "title": metier,
            "sector": "Suggéré pour toi",
            "emoji": _emoji_for(metier),
            "extract": s.get("description", ""),
            "url": resolve_fiche_url(metier),
        })
    return {"cards": out, "error": data.get("error")}


def build_swipe_deck(user_profile, seen=None, liked=None, disliked=None, n=8):
    """Construit un paquet de cartes à swiper. Tente l'IA, retombe sur un paquet statique."""
    seen, liked, disliked = seen or [], liked or [], disliked or []
    resp = get_tinder_suggestions_ai(user_profile, seen, liked, disliked, batch_size=n)
    cards = resp.get("suggestions") if isinstance(resp, dict) else None
    if cards:
        return cards
    # Fallback robuste : jamais d'écran vide même si Ollama est lent/indisponible.
    pool = [c for c in TINDER_CAREERS if c["title"] not in seen]
    random.shuffle(pool)
    return pool[:n] if pool else random.sample(TINDER_CAREERS, min(n, len(TINDER_CAREERS)))


def clusters_from_liked(liked_cards):
    """Déduit les 'clusters' d'intérêt à partir des mots-clés des cartes aimées."""
    freq = {}
    for c in liked_cards:
        for kw in c.get("keywords", []):
            freq[kw] = freq.get(kw, 0) + 1
    return [kw for kw, _ in sorted(freq.items(), key=lambda x: -x[1])[:4]]
