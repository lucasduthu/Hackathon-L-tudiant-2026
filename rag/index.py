"""Indexation (chunk + embeddings) et retrieval par similarité cosinus (numpy)."""
import json
import os

import numpy as np

from . import ollama_client, settings

# nomic-embed-text recommande des préfixes de tâche pour de meilleurs résultats.
_DOC_PREFIX = "search_document: "
_QUERY_PREFIX = "search_query: "


def _chunk(text, size, overlap):
    text = text.strip()
    if not text:
        return []
    if len(text) <= size:
        return [text]
    chunks, start = [], 0
    step = max(size - overlap, 1)
    while start < len(text):
        piece = text[start:start + size].strip()
        if piece:
            chunks.append(piece)
        start += step
    return chunks


def load_corpus(path=None):
    path = path or settings.CORPUS_PATH
    docs = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                docs.append(json.loads(line))
    return docs


def build_index(corpus_path=None, batch_size=32, verbose=True):
    """Découpe le corpus, calcule les embeddings et sauvegarde index.npz + chunks.json."""
    docs = load_corpus(corpus_path)
    chunks = []
    for d in docs:
        for piece in _chunk(d["text"], settings.CHUNK_SIZE, settings.CHUNK_OVERLAP):
            chunks.append({"text": piece, "url": d["url"], "title": d["title"]})
    if verbose:
        print(f"{len(docs)} pages -> {len(chunks)} chunks")

    vectors = []
    for i in range(0, len(chunks), batch_size):
        batch = [_DOC_PREFIX + c["text"] for c in chunks[i:i + batch_size]]
        vectors.extend(ollama_client.embed(batch))
        if verbose:
            print(f"  embeddings {min(i + batch_size, len(chunks))}/{len(chunks)}")

    mat = np.asarray(vectors, dtype=np.float32)
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    mat /= norms  # normalisé -> le produit scalaire donne le cosinus

    os.makedirs(settings.DATA_DIR, exist_ok=True)
    np.savez_compressed(settings.INDEX_PATH, embeddings=mat)
    with open(settings.CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False)
    if verbose:
        print(f"index sauvegardé: {settings.INDEX_PATH} {mat.shape}")
    return mat.shape


class Retriever:
    """Charge l'index une fois et répond aux requêtes par similarité cosinus."""

    def __init__(self):
        self.embeddings = None
        self.chunks = []
        if os.path.exists(settings.INDEX_PATH) and os.path.exists(settings.CHUNKS_PATH):
            self.embeddings = np.load(settings.INDEX_PATH)["embeddings"]
            with open(settings.CHUNKS_PATH, encoding="utf-8") as f:
                self.chunks = json.load(f)

    @property
    def ready(self):
        return self.embeddings is not None and len(self.chunks) > 0

    def search(self, query, k=None):
        k = k or settings.TOP_K
        if not self.ready or not query:
            return []
        try:
            q = np.asarray(ollama_client.embed([_QUERY_PREFIX + query])[0], dtype=np.float32)
        except ollama_client.OllamaError:
            return []
        norm = np.linalg.norm(q)
        if norm == 0:
            return []
        sims = self.embeddings @ (q / norm)
        top = np.argsort(-sims)[:k]
        return [{"score": float(sims[i]), **self.chunks[i]} for i in top]


_retriever = None


def get_retriever():
    """Singleton paresseux: l'index n'est chargé qu'au premier appel."""
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever
