import json
import hashlib
from datetime import datetime
from pathlib import Path

DB_PATH = Path("data/users.json")
DB_PATH.parent.mkdir(exist_ok=True)

def load_db():
    if DB_PATH.exists():
        with open(DB_PATH) as f:
            return json.load(f)
    return {"users": {}}

def save_db(db):
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def register_user(username, password, email=""):
    db = load_db()
    if username in db["users"]:
        return False, "Ce nom d'utilisateur existe déjà."
    db["users"][username] = {
        "password": hash_pw(password),
        "email": email,
        "created": datetime.now().isoformat(),
        "profile": {},
        "conversations": [],
        "all_conversations": [],
        "tinder_profile": {}
    }
    save_db(db)
    return True, "Compte créé avec succès !"

def login_user(username, password):
    db = load_db()
    user = db["users"].get(username)
    if not user:
        return False, "Utilisateur introuvable."
    if user["password"] != hash_pw(password):
        return False, "Mot de passe incorrect."
    return True, user

def save_user_data(username, profile=None, conversations=None, all_conversations=None, tinder_profile=None):
    db = load_db()
    if username not in db["users"]:
        return
    if profile is not None:
        db["users"][username]["profile"] = profile
    if conversations is not None:
        db["users"][username]["conversations"] = conversations
    if all_conversations is not None:
        db["users"][username]["all_conversations"] = all_conversations
    if tinder_profile is not None:
        db["users"][username]["tinder_profile"] = tinder_profile
    save_db(db)
