"""Client léger pour l'API REST d'Ollama (embeddings + génération), sans dépendance lourde."""
import requests

from . import settings


class OllamaError(RuntimeError):
    """Levée quand Ollama est injoignable ou renvoie une réponse invalide."""


def _post(path, payload, timeout=180):
    url = settings.OLLAMA_HOST.rstrip("/") + path
    try:
        r = requests.post(url, json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        raise OllamaError(f"Requête Ollama échouée ({url}): {e}") from e


def embed(texts, model=None):
    """Renvoie la liste des vecteurs d'embedding pour une chaîne ou une liste de chaînes."""
    if isinstance(texts, str):
        texts = [texts]
    model = model or settings.EMBED_MODEL
    data = _post("/api/embed", {"model": model, "input": texts})
    embs = data.get("embeddings")
    if not embs:
        raise OllamaError(f"Aucun embedding renvoyé par Ollama: {data}")
    return embs


def generate(prompt, system=None, model=None, temperature=0.4, fmt=None, timeout=240):
    """Génère une réponse texte avec le modèle de chat (gemma3:1b par défaut).

    fmt : passe "json" ou un schéma JSON pour forcer une sortie structurée valide
    (décodage contraint par grammaire côté Ollama).
    """
    model = model or settings.GEN_MODEL
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature},
    }
    if system:
        payload["system"] = system
    if fmt is not None:
        payload["format"] = fmt
    data = _post("/api/generate", payload, timeout=timeout)
    return (data.get("response") or "").strip()


def is_available():
    """True si le serveur Ollama répond."""
    try:
        url = settings.OLLAMA_HOST.rstrip("/") + "/api/tags"
        return requests.get(url, timeout=3).status_code == 200
    except requests.RequestException:
        return False
