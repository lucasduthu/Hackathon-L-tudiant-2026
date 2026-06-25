"""Construit le RAG letudiant.fr : crawl puis indexation.

Usage :
    python -m rag.build
"""
from . import crawler, index, ollama_client, settings


def main():
    if not ollama_client.is_available():
        print(f"Ollama injoignable sur {settings.OLLAMA_HOST}. Lance `ollama serve` puis réessaie.")
        return

    print("1/2 · Crawl de letudiant.fr (sections métiers & études)…")
    pages = crawler.crawl()
    crawler.save_corpus(pages)
    print(f"     {len(pages)} pages -> {settings.CORPUS_PATH}")

    if not pages:
        print("Aucune page récupérée, indexation annulée.")
        return

    print(f"2/2 · Indexation avec {settings.EMBED_MODEL}…")
    index.build_index()
    print("RAG prêt.")


if __name__ == "__main__":
    main()
