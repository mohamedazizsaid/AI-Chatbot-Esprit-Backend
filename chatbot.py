import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from typing import List, Dict
import uuid

class ChatbotRAG:
    def __init__(self):
        """Initialise le chatbot avec RAG (Retrieval Augmented Generation)"""
        
        # Modèle d'embedding (gratuit, local)
        print("Chargement du modèle d'embedding...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Base de données vectorielle ChromaDB
        self.chroma_client = chromadb.Client(Settings(
            persist_directory="./data/vector_db",
            anonymized_telemetry=False
        ))
        
        # Collection pour stocker les documents
        try:
            self.collection = self.chroma_client.get_collection("faculty_docs")
        except:
            self.collection = self.chroma_client.create_collection(
                name="faculty_docs",
                metadata={"description": "Documents de la faculté"}
            )
        
        # Modèle de génération (utilisation d'un modèle léger gratuit)
        # Alternative: utiliser GPT4All ou LLaMA via Ollama pour plus de performance
        print("Chargement du modèle de génération...")
        self.tokenizer = None
        self.model = None
        self.use_simple_generation = True  # Mode simple sans modèle lourd
        
    def add_documents(self, chunks: List[Dict]):
        """Ajoute des documents au vector store"""
        if not chunks:
            return
        
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        ids = [str(uuid.uuid4()) for _ in chunks]
        
        # Générer les embeddings
        embeddings = self.embedding_model.encode(texts).tolist()
        
        # Ajouter à ChromaDB
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"{len(chunks)} chunks ajoutés au vector store")
    
    def search_relevant_docs(self, query: str, n_results: int = 3):
        """Recherche les documents pertinents"""
        query_embedding = self.embedding_model.encode(query).tolist()
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        return results
    
    def get_response(self, question: str, conversation_id: str = None):
        """Génère une réponse à la question"""
        
        # Rechercher les documents pertinents
        search_results = self.search_relevant_docs(question)
        
        if not search_results["documents"] or not search_results["documents"][0]:
            return {
                "answer": "Désolé, je n'ai pas trouvé d'information pertinente dans mes documents. Pourriez-vous reformuler votre question ou contacter l'administration ?",
                "sources": [],
                "conversation_id": conversation_id or str(uuid.uuid4())
            }
        
        # Contexte des documents trouvés
        context = "\n\n".join(search_results["documents"][0])
        sources = []
        
        for i, metadata in enumerate(search_results["metadatas"][0]):
            sources.append({
                "filename": metadata.get("filename", "Unknown"),
                "page": metadata.get("page", "N/A"),
                "distance": search_results["distances"][0][i]
            })
        
        # Génération de la réponse (mode simple)
        if self.use_simple_generation:
            answer = self._generate_simple_response(question, context)
        else:
            answer = self._generate_llm_response(question, context)
        
        return {
            "answer": answer,
            "sources": sources,
            "conversation_id": conversation_id or str(uuid.uuid4())
        }
    
    def _generate_simple_response(self, question: str, context: str):
        """Génération simple basée sur le contexte"""
        
        # Template de réponse
        response = f"""Basé sur les documents de la faculté, voici la réponse à votre question:

Question: {question}

Informations pertinentes trouvées:
{context[:1000]}...

Pour plus de détails, je vous recommande de consulter les documents sources mentionnés ci-dessus ou de contacter directement l'administration."""
        
        return response
    
    def _generate_llm_response(self, question: str, context: str):
        """Génération avec un modèle LLM (optionnel)"""
        
        prompt = f"""Tu es un assistant de la faculté. Réponds à la question en utilisant uniquement le contexte fourni.

Contexte:
{context}

Question: {question}

Réponse (en français, claire et concise):"""
        
        # Ici, vous pouvez intégrer un modèle comme GPT4All ou Ollama
        # Pour l'instant, retour simple
        return self._generate_simple_response(question, context)
    
    def reload_vector_store(self):
        """Recharge le vector store depuis la base de données"""
        try:
            self.collection = self.chroma_client.get_collection("faculty_docs")
            print("Vector store rechargé")
        except Exception as e:
            print(f"Erreur lors du rechargement: {e}")
    
    def clear_vector_store(self):
        """Vide complètement le vector store"""
        try:
            self.chroma_client.delete_collection("faculty_docs")
            self.collection = self.chroma_client.create_collection(
                name="faculty_docs",
                metadata={"description": "Documents de la faculté"}
            )
            print("Vector store vidé")
        except Exception as e:
            print(f"Erreur: {e}")