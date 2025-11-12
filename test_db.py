from pymongo import MongoClient
from auth import get_password_hash

def init_database():
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["chatbot_faculte"]
        users = db.users
        
        # Vérifier si l'admin existe déjà
        existing_admin = users.find_one({"username": "admin"})
        if existing_admin:
            print("✅ L'utilisateur admin existe déjà")
            return
        
        # Créer l'utilisateur admin
        admin_user = {
            "username": "admin",
            "password_hash": get_password_hash("admin123"),
            "role": "admin",
            "email": "admin@faculte.com"
        }
        
        users.insert_one(admin_user)
        print("✅ Base de données initialisée avec l'utilisateur admin")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")

if __name__ == "__main__":
    init_database()