import sqlite3
from datetime import datetime
from typing import Optional, List, Dict
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Database:
    def __init__(self, db_path: str = "chatbot_faculte.db"):
        self.db_path = db_path
        self.init_database()
        self.create_default_admin()
    
    def get_connection(self):
        """Crée une connexion à la base de données"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialise les tables de la base de données"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Table des utilisateurs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table des documents
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_type TEXT,
                file_path TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table des conversations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT UNIQUE NOT NULL,
                user_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table des messages
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_default_admin(self):
        """Crée un utilisateur admin par défaut"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Vérifier si un admin existe
            cursor.execute("SELECT * FROM users WHERE role = 'admin'")
            if cursor.fetchone() is None:
                password_hash = pwd_context.hash("admin123")
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    ("admin", password_hash, "admin")
                )
                conn.commit()
                print("Utilisateur admin créé: username='admin', password='admin123'")
            
            conn.close()
        except Exception as e:
            print(f"Erreur création admin: {e}")
    
    # Gestion des utilisateurs
    def get_user(self, username: str) -> Optional[Dict]:
        """Récupère un utilisateur par son username"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def create_user(self, username: str, password: str, role: str = "user"):
        """Crée un nouvel utilisateur"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        password_hash = pwd_context.hash(password)
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        return user_id
    
    # Gestion des documents
    def add_document(self, filename: str, file_type: str, file_path: str, status: str = "pending"):
        """Ajoute un document"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO documents (filename, file_type, file_path, status) 
               VALUES (?, ?, ?, ?)""",
            (filename, file_type, file_path, status)
        )
        conn.commit()
        doc_id = cursor.lastrowid
        conn.close()
        
        return doc_id
    
    def get_document(self, doc_id: int) -> Optional[Dict]:
        """Récupère un document par son ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_all_documents(self) -> List[Dict]:
        """Récupère tous les documents"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents ORDER BY upload_date DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def delete_document(self, doc_id: int):
        """Supprime un document"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        conn.commit()
        conn.close()
    
    def update_document_status(self, doc_id: int, status: str):
        """Met à jour le statut d'un document"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE documents SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, doc_id)
        )
        conn.commit()
        conn.close()
    
    # Gestion des conversations
    def create_conversation(self, conversation_id: str, user_type: str = "student"):
        """Crée une nouvelle conversation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO conversations (conversation_id, user_type) VALUES (?, ?)",
            (conversation_id, user_type)
        )
        conn.commit()
        conn.close()
    
    def add_message(self, conversation_id: str, role: str, content: str):
        """Ajoute un message à une conversation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Vérifier si la conversation existe
        cursor.execute("SELECT * FROM conversations WHERE conversation_id = ?", (conversation_id,))
        if cursor.fetchone() is None:
            self.create_conversation(conversation_id)
        
        cursor.execute(
            "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
            (conversation_id, role, content)
        )
        
        # Mettre à jour last_activity
        cursor.execute(
            "UPDATE conversations SET last_activity = CURRENT_TIMESTAMP WHERE conversation_id = ?",
            (conversation_id,)
        )
        
        conn.commit()
        conn.close()
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """Récupère l'historique d'une conversation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at",
            (conversation_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # Statistiques
    def count_documents(self) -> int:
        """Compte le nombre de documents"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM documents")
        count = cursor.fetchone()["count"]
        conn.close()
        return count
    
    def count_questions(self) -> int:
        """Compte le nombre de questions posées"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM messages WHERE role = 'user'")
        count = cursor.fetchone()["count"]
        conn.close()
        return count
    
    def count_active_conversations(self) -> int:
        """Compte le nombre de conversations actives (dernières 24h)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT COUNT(*) as count FROM conversations 
               WHERE last_activity > datetime('now', '-1 day')"""
        )
        count = cursor.fetchone()["count"]
        conn.close()
        return count