"""Configuration centrale du RAG (modèles Ollama, chemins, crawl, chunking)."""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Ollama ───────────────────────────────────────────────────────────────────
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
GEN_MODEL = os.environ.get("RAG_GEN_MODEL", "gemma3:1b")
EMBED_MODEL = os.environ.get("RAG_EMBED_MODEL", "nomic-embed-text")

# ── Fichiers générés ─────────────────────────────────────────────────────────
DATA_DIR = os.path.join(BASE_DIR, "data", "rag")
CORPUS_PATH = os.path.join(DATA_DIR, "corpus.jsonl")
INDEX_PATH = os.path.join(DATA_DIR, "index.npz")
CHUNKS_PATH = os.path.join(DATA_DIR, "chunks.json")

# ── Crawl ────────────────────────────────────────────────────────────────────
CRAWL_SEEDS = [
    "https://www.letudiant.fr/metiers.html",
    "https://www.letudiant.fr/etudes.html",
]
CRAWL_SITEMAPS = [
    "https://www.letudiant.fr/sitemaps/letudiant/sitemap-general-1.xml.gz",
    "https://www.letudiant.fr/sitemaps/letudiant/sitemap-general-2.xml.gz",
    "https://www.letudiant.fr/sitemaps/letudiant/sitemap-general-3.xml.gz"
]
CRAWL_ALLOWED_DOMAIN = "www.letudiant.fr"
CRAWL_URL_INCLUDE = ("/metiers", "/etudes")  # on ne suit que ces thématiques
CRAWL_MAX_PAGES = 6000
CRAWL_CONCURRENCY = 8  # nombre de threads de téléchargement en parallèle
CRAWL_DELAY = 0.05  # secondes entre deux requêtes par thread (politesse)
CRAWL_MIN_TEXT = 400  # on ignore les pages trop pauvres en texte
CRAWL_USER_AGENT = "letudiant-orientation-rag/1.0 (hackathon local; respecte robots.txt)"

# ── Chunking / retrieval ─────────────────────────────────────────────────────
CHUNK_SIZE = 900       # caractères par chunk
CHUNK_OVERLAP = 150
TOP_K = 4              # nombre de chunks renvoyés par défaut

