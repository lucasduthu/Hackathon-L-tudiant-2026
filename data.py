"""Données statiques partagées : taxonomies de profil, decks « Tinder » et événements.

Tout est local (aucune API). Les événements sont des EXEMPLES illustratifs (titres et
dates fictifs), mais chaque lien pointe vers la vraie page/section L'Étudiant
correspondante (salon, secteur, alternance…). Les `themes`/`sectors` des
événements réutilisent EXACTEMENT les libellés de INTERESTS / SECTEURS pour que le
matching avec le profil (engine.match_events) fonctionne par simple intersection.
"""

# ── Taxonomies de profil (partagées par Explorer / Profil / Événements) ───────
PERSONA_LABELS = {
    "collegien": "Collégien·ne",
    "lyceen": "Lycéen·ne",
    "etudiant": "Étudiant·e",
    "parent": "Parent",
}

NIVEAUX = ["—", "Collège", "Lycée", "Bac+1", "Bac+2", "Bac+3", "Bac+4", "Bac+5"]

INTERESTS = ["Technique", "Créativité", "Innovation", "Humain", "Données", "Management",
             "International", "Terrain", "Recherche", "Communication", "Art", "Business"]

SECTEURS = ["Informatique/Tech", "Santé", "Commerce", "Ingénierie", "Art/Design",
            "Sciences humaines", "Droit", "Environnement", "Enseignement", "Finance", "Communication"]

CITIES = ["Paris", "Lyon", "Marseille", "Toulouse", "Bordeaux", "Lille",
          "Nantes", "Strasbourg", "Rennes", "Montpellier"]

TIMELINES = {
    "exploring": "J'explore tranquillement",
    "next_year": "Pour l'an prochain",
    "this_year": "Cette année (urgent)",
}


# ── Decks « mode Tinder » ─────────────────────────────────────────────────────
TINDER_CAREERS = [
    {"emoji": "", "title": "Manager Commercial", "keywords": ["Leadership", "Négociation", "Résultats"]},
    {"emoji": "", "title": "Ingénieur R&D", "keywords": ["Innovation", "Technique", "Laboratoire"]},
    {"emoji": "", "title": "Directeur Artistique", "keywords": ["Créativité", "Design", "Culture"]},
    {"emoji": "", "title": "Data Analyst", "keywords": ["Données", "Statistiques", "Insights"]},
    {"emoji": "", "title": "Infirmier·ère", "keywords": ["Humain", "Soin", "Urgence"]},
    {"emoji": "", "title": "Avocat·e", "keywords": ["Argumentation", "Justice", "Droit"]},
    {"emoji": "", "title": "Chef de Projet ONG", "keywords": ["Impact", "Terrain", "International"]},
    {"emoji": "", "title": "Développeur IA", "keywords": ["Algorithmique", "Python", "Futur"]},
    {"emoji": "", "title": "Architecte", "keywords": ["Espace", "Construction", "Créativité"]},
    {"emoji": "", "title": "Journaliste", "keywords": ["Écriture", "Enquête", "Médias"]},
]

# Thématiques « Environnement de travail » et « Valeurs » : paires de choix (this-or-that).
TINDER_ENVIRONMENTS = [
    {"emoji": "", "a": "Open space dynamique", "b": "Bureau calme et privé"},
    {"emoji": "", "a": "Terrain, déplacements", "b": "Siège, télétravail possible"},
    {"emoji": "", "a": "Grande entreprise", "b": "Startup agile"},
    {"emoji": "", "a": "Ancré en France", "b": "Profil international"},
    {"emoji": "", "a": "Résultats immédiats", "b": "Vision long terme"},
]

VALUES_PAIRS = [
    {"emoji": "", "a": "Stabilité", "b": "Prise de risque"},
    {"emoji": "", "a": "Créer", "b": "Optimiser"},
    {"emoji": "", "a": "Travailler seul", "b": "Travailler en équipe"},
    {"emoji": "", "a": "Impact social", "b": "Performance business"},
    {"emoji": "", "a": "Se spécialiser", "b": "Varier les missions"},
    {"emoji": "", "a": "Environnement structuré", "b": "Autonomie totale"},
]


# ── Événements d'orientation (EXEMPLES illustratifs, saison 2026-2027) ─────────
# Titres/dates fictifs mais réalistes ; chaque `url` pointe vers la vraie page/section
# L'Étudiant correspondante (vérifiée 200), pas vers un faux événement ni l'accueil.
# date : ISO ; themes ⊂ INTERESTS ; sectors ⊂ SECTEURS ; online : webinaire/visio.
EVENTS = [
    {
        "title": "Salon de l'Étudiant de Paris",
        "type": "Salon", "date": "2026-09-12", "city": "Paris", "online": False,
        "themes": ["Innovation", "Business", "International"],
        "sectors": ["Informatique/Tech", "Commerce", "Ingénierie", "Finance"],
        "org": "L'Étudiant", "url": "https://www.letudiant.fr/etudes/salons.html",
        "blurb": "300 formations et écoles réunies : prépas, BTS, BUT, licences, écoles d'ingé et de commerce.",
    },
    {
        "title": "Salon des Grandes Écoles (SaGE)",
        "type": "Salon", "date": "2026-11-28", "city": "Paris", "online": False,
        "themes": ["Management", "Business", "International"],
        "sectors": ["Commerce", "Ingénierie", "Finance"],
        "org": "L'Étudiant", "url": "https://www.letudiant.fr/etudes/salons.html",
        "blurb": "Écoles de commerce et d'ingénieurs post-prépa : programmes, admissions parallèles, doubles diplômes.",
    },
    {
        "title": "JPO — École 42",
        "type": "JPO", "date": "2026-10-04", "city": "Paris", "online": False,
        "themes": ["Technique", "Innovation", "Données"],
        "sectors": ["Informatique/Tech"],
        "org": "42", "url": "https://www.letudiant.fr/metiers/secteur/informatique-telecom-web.html",
        "blurb": "Découvre la pédagogie sans prof ni cours de l'école d'informatique : code, peer-learning, projets.",
    },
    {
        "title": "Forum Santé & Métiers du Soin",
        "type": "Forum", "date": "2026-10-18", "city": "Marseille", "online": False,
        "themes": ["Humain", "Terrain", "Recherche"],
        "sectors": ["Santé", "Sciences humaines"],
        "org": "CRIJ PACA", "url": "https://www.letudiant.fr/metiers/secteur/medical.html",
        "blurb": "Infirmier, médecine, kiné, aide-soignant, sage-femme : échanges avec des pros et des étudiants.",
    },
    {
        "title": "Webinaire — Parcoursup mode d'emploi",
        "type": "Webinaire", "date": "2026-12-09", "city": "En ligne", "online": True,
        "themes": ["Communication"],
        "sectors": [],
        "org": "L'Étudiant", "url": "https://www.parcoursup.gouv.fr",
        "blurb": "Calendrier, vœux, lettre de motivation et phase d'admission : tout pour ne rien rater.",
    },
    {
        "title": "Salon de l'Étudiant de Toulouse",
        "type": "Salon", "date": "2027-01-16", "city": "Toulouse", "online": False,
        "themes": ["Technique", "Innovation", "International"],
        "sectors": ["Ingénierie", "Informatique/Tech", "Commerce"],
        "org": "L'Étudiant", "url": "https://www.letudiant.fr/etudes/salons.html",
        "blurb": "Aéronautique, numérique, commerce : les formations du Sud-Ouest sous un même toit.",
    },
    {
        "title": "JPO — INSA Lyon",
        "type": "JPO", "date": "2027-02-07", "city": "Lyon", "online": False,
        "themes": ["Technique", "Recherche", "Innovation"],
        "sectors": ["Ingénierie", "Informatique/Tech"],
        "org": "INSA Lyon", "url": "https://www.letudiant.fr/etudes/ecole-ingenieur.html",
        "blurb": "Visite des labos, rencontres avec les élèves-ingénieurs et présentation des spécialités.",
    },
    {
        "title": "Nuit de l'Orientation",
        "type": "Forum", "date": "2027-01-23", "city": "Bordeaux", "online": False,
        "themes": ["Humain", "Terrain", "Management"],
        "sectors": ["Commerce", "Sciences humaines", "Santé"],
        "org": "CCI Bordeaux", "url": "https://www.letudiant.fr/etudes/secteurs.html",
        "blurb": "Speed-dating métiers, tests d'orientation et conseils perso, en soirée et sans pression.",
    },
    {
        "title": "Salon de l'Alternance & du Numérique",
        "type": "Salon", "date": "2026-11-14", "city": "Lille", "online": False,
        "themes": ["Données", "Technique", "Business"],
        "sectors": ["Informatique/Tech", "Commerce", "Communication"],
        "org": "Studyrama", "url": "https://www.letudiant.fr/etudes/alternance.html",
        "blurb": "Contrats d'apprentissage et formations tech : rencontre des entreprises qui recrutent.",
    },
    {
        "title": "Forum des Métiers de l'Art & du Design",
        "type": "Forum", "date": "2026-12-05", "city": "Nantes", "online": False,
        "themes": ["Art", "Créativité", "Communication"],
        "sectors": ["Art/Design", "Communication"],
        "org": "Écoles d'art des Pays de la Loire", "url": "https://www.letudiant.fr/metiers/secteur/creation.html",
        "blurb": "Design graphique, illustration, jeu vidéo, mode : portfolios commentés par des pros.",
    },
    {
        "title": "Webinaire — Étudier à l'international",
        "type": "Webinaire", "date": "2026-10-22", "city": "En ligne", "online": True,
        "themes": ["International", "Communication"],
        "sectors": ["Commerce", "Sciences humaines"],
        "org": "L'Étudiant", "url": "https://www.letudiant.fr/etudes/international.html",
        "blurb": "Erasmus, échanges, doubles diplômes et financements : comment partir étudier ailleurs.",
    },
    {
        "title": "Salon des Métiers du Droit & de la Justice",
        "type": "Salon", "date": "2027-02-14", "city": "Paris", "online": False,
        "themes": ["Humain", "Communication"],
        "sectors": ["Droit", "Sciences humaines"],
        "org": "Le Village de la Justice", "url": "https://www.letudiant.fr/metiers/secteur/droit.html",
        "blurb": "Avocat, magistrat, juriste d'entreprise, notaire : parcours et débouchés du droit.",
    },
    {
        "title": "JPO — Sciences Po",
        "type": "JPO", "date": "2026-11-21", "city": "Paris", "online": False,
        "themes": ["International", "Humain", "Communication"],
        "sectors": ["Sciences humaines", "Droit", "Communication"],
        "org": "Sciences Po", "url": "https://www.letudiant.fr/etudes/secteurs/sciences-politiques.html",
        "blurb": "Procédure d'admission, collège universitaire et campus en région : rencontre des étudiants.",
    },
    {
        "title": "Salon de l'Environnement & des Métiers Verts",
        "type": "Salon", "date": "2027-01-30", "city": "Strasbourg", "online": False,
        "themes": ["Terrain", "Recherche", "Innovation"],
        "sectors": ["Environnement", "Ingénierie"],
        "org": "ADEME", "url": "https://www.letudiant.fr/metiers/secteur/environnement.html",
        "blurb": "Transition écologique, énergies, biodiversité : les formations et métiers qui ont du sens.",
    },
    {
        "title": "Forum Finance, Banque & Assurance",
        "type": "Forum", "date": "2026-12-12", "city": "Paris", "online": False,
        "themes": ["Données", "Business", "Management"],
        "sectors": ["Finance", "Commerce"],
        "org": "L'Étudiant", "url": "https://www.letudiant.fr/metiers/secteur/banque-assurance.html",
        "blurb": "Trading, audit, gestion de patrimoine, fintech : rencontre les recruteurs du secteur.",
    },
    {
        "title": "Webinaire — Les métiers de la Data & de l'IA",
        "type": "Webinaire", "date": "2026-09-26", "city": "En ligne", "online": True,
        "themes": ["Données", "Innovation", "Technique"],
        "sectors": ["Informatique/Tech"],
        "org": "L'Étudiant", "url": "https://www.letudiant.fr/metiers/secteur/intelligence-artificielle.html",
        "blurb": "Data analyst, data scientist, ML engineer : compétences, formations et salaires décryptés.",
    },
]
