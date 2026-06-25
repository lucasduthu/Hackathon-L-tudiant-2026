# ORI — L'ÉTUDIANT

Assistant d'orientation **100 % local**, pensé comme un **espace personnel** qui apprend à te
connaître. Plusieurs pages — **dashboard**, **chat**, **mode découverte (swipe)**, **événements**,
**profil** — toutes nourries par **ton profil**. Les réponses et fiches métier viennent de
**letudiant.fr** via un RAG local + le modèle **gemma3:1b** servi par **Ollama**. Aucune API cloud,
aucune clé secrète.

## Le concept

**Tout gravite autour de la connaissance de l'utilisateur** : chaque page lit et enrichit ton profil.
Navigation par **barre d'onglets** en haut ; un résumé « Ce qu'ORI sait de toi » reste visible en sidebar.

1. **Dashboard** — recommandations personnalisées + **suivi de ta démarche** (5 étapes) + événements près de toi.
2. **Chat ORI** — questions Parcoursup, débouchés, formations… réponses sourcées (RAG) et fiches métier letudiant.fr.
3. **Explorer (mode Tinder)** — swipe sur plusieurs thématiques (métiers, environnement, valeurs, secteurs) ; chaque choix affine ton profil.
4. **Événements** — salons, JPO, forums et webinaires classés par affinité avec tes intérêts, filtrables par ville / thème / format.
5. **Profil** — « ce qu'ORI sait de toi », éditable ; ORI y montre aussi ce qu'il a déduit de tes swipes.

Le RAG et la génération restent fiables même avec `gemma3:1b` (sorties structurées), et **chaque page
reste utilisable sans Ollama** grâce à des fallbacks (decks statiques, recommandations locales).

## Prérequis

- Python 3.10+
- [Ollama](https://ollama.com) installé et lancé (`ollama serve`)

## Installation

```sh
# 1. Dépendances Python
pip install -r requirements.txt

# 2. Modèles Ollama (génération + embeddings)
ollama pull gemma3:1b
ollama pull nomic-embed-text
```

## Construire le RAG

Crawle letudiant.fr (sections métiers & études, `robots.txt` respecté) puis construit
l'index d'embeddings :

```sh
python -m rag.build
```

Les fichiers générés (`corpus.jsonl`, `index.npz`, `chunks.json`) sont écrits dans `data/rag/`.

## Lancement

```sh
streamlit run app.py
```

## Architecture

| Fichier / dossier | Rôle |
|---|---|
| `app.py` | Point d'entrée et routeur (pages : accueil, auth, dashboard, chat, explorer, événements, profil) |
| `config.py` | Configuration Streamlit et CSS (charte L'Étudiant) |
| `components.py` | Shell : barre d'onglets, sidebar profil + composants (anneau, frise, cartes) |
| `engine.py` | Logique pure : complétion du profil, suivi de la démarche, matching d'événements |
| `utils.py` | État de session, navigation, persistance du profil |
| `db.py` | Persistance des utilisateurs (`data/users.json`) |
| `ai.py` | Couche IA : RAG + génération (réponses, suggestions, deck de swipe, fiches) |
| `data.py` | Taxonomies de profil, decks de swipe et **événements** (mock local) |
| `views/dashboard.py` | Accueil : recommandations + suivi de la démarche + événements proches |
| `views/chat.py` | Conversation ORI (onboarding, Q&A, fiches métier) |
| `views/explore.py` | Mode Tinder multi-thématique (métiers, environnement, valeurs, secteurs) |
| `views/events.py` | Événements filtrables, classés par affinité + agenda |
| `views/profile.py` | Profil éditable — « ce qu'ORI sait de toi » |
| `views/home.py` | Landing : présentation + entrée invité ou connexion |
| `views/auth.py` | Connexion / inscription (optionnelles — mode invité possible) |
| `rag/` | RAG local : `crawler`, `index`, `ollama_client`, `build`, `settings` |

### Comment fonctionne le RAG

1. **Crawl** — `rag/crawler.py` récupère des pages de letudiant.fr → `data/rag/corpus.jsonl`
2. **Index** — `rag/index.py` découpe en chunks et calcule les embeddings avec `nomic-embed-text` → `data/rag/index.npz`
3. **Réponse** — `ai.py` récupère les chunks pertinents (similarité cosinus) et les injecte dans le prompt envoyé à `gemma3:1b`.

Pour les **cartes fiches métier**, `ai.py` cible la recherche (retire les mots génériques du gabarit
des fiches) et vérifie lexicalement que le métier demandé apparaît vraiment dans la fiche, afin de
ne jamais afficher de carte hors-sujet.

### Configuration

Variables d'environnement optionnelles (voir `rag/settings.py`) :
`OLLAMA_HOST`, `RAG_GEN_MODEL`, `RAG_EMBED_MODEL`.
