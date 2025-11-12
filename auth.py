from passlib.context import CryptContext
from fastapi import Header, HTTPException
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any

# Charger les variables d'environnement
load_dotenv()

# Configuration du hachage de mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Connexion à MongoDB
client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/"))
db = client[os.getenv("DB_NAME", "chatbot_faculte")]
users_collection = db.users

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si le mot de passe correspond au hash"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Erreur lors de la vérification du mot de passe: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Crée un hash du mot de passe"""
    return pwd_context.hash(password)

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Récupère un utilisateur par son nom d'utilisateur"""
    try:
        user = users_collection.find_one({"username": username})
        return user
    except Exception as e:
        print(f"Erreur lors de la récupération de l'utilisateur: {e}")
        return None

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authentifie un utilisateur avec son nom d'utilisateur et mot de passe"""
    user = get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user

def get_current_user(x_username: str = Header(None, alias="X-Username")) -> Dict[str, Any]:
    """
    Récupère l'utilisateur courant basé sur le header X-Username.
    Version simple sans système de tokens JWT.
    """
    print(f"=== get_current_user appelé ===")
    print(f"x_username reçu: {x_username}")
    
    if not x_username:
        print("❌ Header X-Username manquant")
        raise HTTPException(
            status_code=401,
            detail="Header X-Username manquant"
        )
    
    try:
        user = get_user_by_username(x_username)
        print(f"Utilisateur trouvé: {user is not None}")
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Utilisateur non trouvé"
            )
        
        # Retourner les informations utilisateur sans le mot de passe
        user_info = {
            "username": user.get("username"),
            "email": user.get("email"),
            "role": user.get("role"),
            "_id": str(user.get("_id"))
        }
        print(f"✅ Utilisateur authentifié: {user_info['username']} (role: {user_info['role']})")
        return user_info
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur lors de la récupération de l'utilisateur courant: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur serveur lors de l'authentification"
        )

def create_admin_user():
    """Crée l'utilisateur admin s'il n'existe pas"""
    try:
        admin_user = users_collection.find_one({"username": "admin"})
        
        if not admin_user:
            hashed_password = get_password_hash("admin123")
            users_collection.insert_one({
                "username": "admin",
                "password_hash": hashed_password,
                "role": "admin",
                "email": "admin@faculte.com"
            })
            print("✅ Utilisateur admin créé avec succès")
        else:
            print("✅ Utilisateur admin existe déjà")
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'admin: {e}")

# Exemple d'utilisation
if __name__ == "__main__":
    create_admin_user()