from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
from datetime import datetime

from chatbot import ChatbotRAG
from document_processor import DocumentProcessor
from auth import get_current_user, create_access_token, verify_password, get_password_hash
from database import Database

app = FastAPI(title="Chatbot Faculté API")

# Configuration CORS pour Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # URL Angular
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation
UPLOAD_DIR = "uploads/documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)

db = Database()
chatbot = ChatbotRAG()
doc_processor = DocumentProcessor()

# Modèles Pydantic
class Question(BaseModel):
    question: str
    conversation_id: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class DocumentInfo(BaseModel):
    id: int
    filename: str
    file_type: str
    upload_date: str
    status: str

# Routes d'authentification
@app.post("/api/auth/login")
async def login(request: LoginRequest):
    user = db.get_user(request.username)
    if not user or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Identifiants incorrects")
    
    access_token = create_access_token(data={"sub": user["username"], "role": user["role"]})
    return {"access_token": access_token, "token_type": "bearer", "role": user["role"]}

# Routes publiques (Étudiant/Parent)
@app.post("/api/chat")
async def chat(question: Question):
    """Endpoint pour poser une question au chatbot"""
    try:
        response = chatbot.get_response(question.question, question.conversation_id)
        return {
            "response": response["answer"],
            "sources": response.get("sources", []),
            "conversation_id": response.get("conversation_id")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/history/{conversation_id}")
async def get_chat_history(conversation_id: str):
    """Récupérer l'historique d'une conversation"""
    history = db.get_conversation_history(conversation_id)
    return {"history": history}

# Routes Admin (protégées)
@app.post("/api/admin/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload et traitement d'un document"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    try:
        # Sauvegarder le fichier
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Traiter le document
        chunks = doc_processor.process_document(file_path, file.filename)
        
        # Ajouter au vector store
        chatbot.add_documents(chunks)
        
        # Enregistrer dans la BD
        doc_id = db.add_document(
            filename=file.filename,
            file_type=file.content_type,
            file_path=file_path,
            status="processed"
        )
        
        return {
            "message": "Document uploadé et traité avec succès",
            "document_id": doc_id,
            "chunks_count": len(chunks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@app.get("/api/admin/documents")
async def list_documents(current_user: dict = Depends(get_current_user)):
    """Liste tous les documents"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    documents = db.get_all_documents()
    return {"documents": documents}

@app.delete("/api/admin/documents/{document_id}")
async def delete_document(
    document_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Supprimer un document"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    doc = db.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    # Supprimer le fichier physique
    if os.path.exists(doc["file_path"]):
        os.remove(doc["file_path"])
    
    # Supprimer de la BD
    db.delete_document(document_id)
    
    # Recharger le chatbot
    chatbot.reload_vector_store()
    
    return {"message": "Document supprimé avec succès"}

@app.put("/api/admin/documents/{document_id}/reprocess")
async def reprocess_document(
    document_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Retraiter un document"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    doc = db.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    try:
        chunks = doc_processor.process_document(doc["file_path"], doc["filename"])
        chatbot.add_documents(chunks)
        db.update_document_status(document_id, "processed")
        
        return {
            "message": "Document retraité avec succès",
            "chunks_count": len(chunks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/stats")
async def get_stats(current_user: dict = Depends(get_current_user)):
    """Statistiques du système"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    stats = {
        "total_documents": db.count_documents(),
        "total_questions": db.count_questions(),
        "active_conversations": db.count_active_conversations()
    }
    return stats

@app.get("/")
async def root():
    return {"message": "Chatbot Faculté API - Opérationnelle"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)