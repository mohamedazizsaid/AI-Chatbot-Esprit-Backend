from pymongo import MongoClient
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from passlib.context import CryptContext
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Database:
    def __init__(self, connection_string: str = None):
        """
        Initialise la connexion MongoDB
        Par défaut: mongodb://localhost:27017/
        """
        if connection_string is None:
            connection_string = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        
        self.client = MongoClient(connection_string)
        self.db = self.client["chatbot_faculte"]
        
        # Collections
        self.users = self.db["users"]
        self.documents = self.db["documents"]
        self.conversations = self.db["conversations"]
        self.messages = self.db["messages"]
        
        self.init_database()
        self.create_default_admin()
    
    def init_database(self):
        """Initialise les indexes MongoDB"""
        try:
            # Index pour les utilisateurs
            self.users.create_index("username", unique=True)
            
            # Index pour les conversations
            self.conversations.create_index("conversation_id", unique=True)
            self.conversations.create_index("last_activity")
            
            # Index pour les messages
            self.messages.create_index("conversation_id")
            self.messages.create_index("created_at")
            
            print("✅ Indexes MongoDB créés")
        except Exception as e:
            print(f"Info indexes: {e}")
    
    def create_default_admin(self):
        """Crée un utilisateur admin par défaut"""
        try:
            # Vérifier si un admin existe
            existing_admin = self.users.find_one({"role": "admin"})
            
            if existing_admin is None:
                password_hash = pwd_context.hash("admin123")
                self.users.insert_one({
                    "username": "admin",
                    "password_hash": password_hash,
                    "role": "admin",
                    "created_at": datetime.utcnow()
                })
                print("✅ Utilisateur admin créé: username='admin', password='admin123'")
        except Exception as e:
            print(f"Erreur création admin: {e}")
    
    # Gestion des utilisateurs
    def get_user(self, username: str) -> Optional[Dict]:
        """Récupère un utilisateur par son username"""
        user = self.users.find_one({"username": username})
        if user:
            user["id"] = str(user["_id"])
            return user
        return None
    
    def create_user(self, username: str, password: str, role: str = "user"):
        """Crée un nouvel utilisateur"""
        password_hash = pwd_context.hash(password)
        
        result = self.users.insert_one({
            "username": username,
            "password_hash": password_hash,
            "role": role,
            "created_at": datetime.utcnow()
        })
        
        return str(result.inserted_id)
    
    # Gestion des documents
    def add_document(self, filename: str, file_type: str, file_path: str, status: str = "pending"):
        """Ajoute un document"""
        result = self.documents.insert_one({
            "filename": filename,
            "file_type": file_type,
            "file_path": file_path,
            "status": status,
            "upload_date": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        
        return str(result.inserted_id)
    
    def get_document(self, doc_id: str) -> Optional[Dict]:
        """Récupère un document par son ID"""
        from bson.objectid import ObjectId
        
        try:
            doc = self.documents.find_one({"_id": ObjectId(doc_id)})
            if doc:
                doc["id"] = str(doc["_id"])
                return doc
        except:
            pass
        return None
    
    def get_all_documents(self) -> List[Dict]:
        """Récupère tous les documents"""
        docs = list(self.documents.find().sort("upload_date", -1))
        
        for doc in docs:
            doc["id"] = str(doc["_id"])
            doc["upload_date"] = doc["upload_date"].isoformat()
            doc["updated_at"] = doc["updated_at"].isoformat()
        
        return docs
    
    def delete_document(self, doc_id: str):
        """Supprime un document"""
        from bson.objectid import ObjectId
        
        try:
            self.documents.delete_one({"_id": ObjectId(doc_id)})
        except Exception as e:
            print(f"Erreur suppression document: {e}")
    
    def update_document_status(self, doc_id: str, status: str):
        """Met à jour le statut d'un document"""
        from bson.objectid import ObjectId
        
        try:
            self.documents.update_one(
                {"_id": ObjectId(doc_id)},
                {
                    "$set": {
                        "status": status,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        except Exception as e:
            print(f"Erreur mise à jour document: {e}")
    
    # Gestion des conversations
    def create_conversation(self, conversation_id: str, user_type: str = "student"):
        """Crée une nouvelle conversation"""
        try:
            self.conversations.insert_one({
                "conversation_id": conversation_id,
                "user_type": user_type,
                "created_at": datetime.utcnow(),
                "last_activity": datetime.utcnow()
            })
        except Exception as e:
            print(f"Info conversation: {e}")
    
    def add_message(self, conversation_id: str, role: str, content: str):
        """Ajoute un message à une conversation"""
        # Vérifier si la conversation existe
        conversation = self.conversations.find_one({"conversation_id": conversation_id})
        if conversation is None:
            self.create_conversation(conversation_id)
        
        # Ajouter le message
        self.messages.insert_one({
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "created_at": datetime.utcnow()
        })
        
        # Mettre à jour last_activity
        self.conversations.update_one(
            {"conversation_id": conversation_id},
            {"$set": {"last_activity": datetime.utcnow()}}
        )
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """Récupère l'historique d'une conversation"""
        messages = list(
            self.messages.find({"conversation_id": conversation_id})
            .sort("created_at", 1)
        )
        
        for msg in messages:
            msg["id"] = str(msg["_id"])
            msg["created_at"] = msg["created_at"].isoformat()
        
        return messages
    
    # Statistiques
    def count_documents(self) -> int:
        """Compte le nombre de documents"""
        return self.documents.count_documents({})
    
    def count_questions(self) -> int:
        """Compte le nombre de questions posées"""
        return self.messages.count_documents({"role": "user"})
    
    def count_active_conversations(self) -> int:
        """Compte le nombre de conversations actives (dernières 24h)"""
        yesterday = datetime.utcnow() - timedelta(days=1)
        return self.conversations.count_documents({
            "last_activity": {"$gt": yesterday}
        })
    
    def close(self):
        """Ferme la connexion MongoDB"""
        self.client.close()