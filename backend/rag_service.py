import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
import os
from database import Note, NoteEmbedding
from models import AskResponse
from services.llm_service import LLMService
from prompts.templates import get_prompt
from memory.manager import ConversationManager

class RAGService:
    def __init__(self):
        self.llm_service = LLMService()
        self.conversation_manager = ConversationManager(self.llm_service.llm)
        self.embedding_dimension = self.llm_service.embedding_dimension
    
    async def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using Ollama"""
        return await self.llm_service.get_embedding(text)
    
    async def add_note(self, note: Note, db: Session):
        """Add a note to the RAG index with vector embedding"""
        # Get embedding for the note content
        text_content = f"{note.title} {note.content}"
        embedding = await self._get_embedding(text_content)
        
        if embedding:
            # Store embedding in database
            note_embedding = NoteEmbedding(
                note_id=note.id,
                embedding=embedding
            )
            db.add(note_embedding)
            db.commit()
    
    async def update_note(self, note: Note, db: Session):
        """Update a note in the RAG index"""
        # Remove old embeddings
        db.query(NoteEmbedding).filter(NoteEmbedding.note_id == note.id).delete()
        
        # Add new embedding
        await self.add_note(note, db)
    
    async def remove_note(self, note_id: int, db: Session):
        """Remove a note from the RAG index"""
        # Embeddings will be automatically deleted due to CASCADE
        db.query(NoteEmbedding).filter(NoteEmbedding.note_id == note_id).delete()
        db.commit()
    
    async def _get_relevant_notes(self, query: str, db: Session, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve most relevant notes using vector similarity search"""
        # Get query embedding
        query_embedding = await self._get_embedding(query)
        if not query_embedding:
            return []
        
        # Perform vector similarity search using pgvector
        # Convert the embedding to a string format that PostgreSQL can understand
        embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
        
        query_sql = text(f"""
            SELECT n.id, n.title, n.content, n.created_at, n.updated_at,
                   1 - (ne.embedding <=> '{embedding_str}'::vector) as similarity
            FROM notes n
            JOIN note_embeddings ne ON n.id = ne.note_id
            ORDER BY ne.embedding <=> '{embedding_str}'::vector
            LIMIT :top_k
        """)
        
        result = db.execute(query_sql, {
            "top_k": top_k
        }).fetchall()
        
        return [
            {
                "id": row.id,
                "title": row.title,
                "content": row.content,
                "similarity": float(row.similarity),
                "created_at": row.created_at,
                "updated_at": row.updated_at
            }
            for row in result
        ]
    
    async def ask_question(self, question: str, db: Session, user_id: str = "default") -> AskResponse:
        """Process a question using RAG with conversation context"""
        # Get relevant notes
        relevant_notes = await self._get_relevant_notes(question, db)
        
        if not relevant_notes:
            return AskResponse(
                answer="I don't have any notes to search through. Please add some notes first.",
                sources=[]
            )
        
        # Prepare context from relevant notes
        context_parts = []
        sources = []
        
        for note_data in relevant_notes:
            context_parts.append(f"Note '{note_data['title']}': {note_data['content']}")
            sources.append(f"Note {note_data['id']}: {note_data['title']} (similarity: {note_data['similarity']:.2f})")
        
        context = "\n\n".join(context_parts)
        
        # Get conversation context
        recent_context = self.conversation_manager.get_recent_context(user_id)
        
        # Prepare messages for LLM
        messages = [
            {"role": "system", "content": "You are a helpful assistant that answers questions based on provided notes. Be concise and accurate."}
        ]
        
        # Add recent conversation context
        for msg in recent_context[-4:]:  # Last 4 messages for context
            if hasattr(msg, 'content'):
                role = "user" if msg.__class__.__name__ == "HumanMessage" else "assistant"
                messages.append({"role": role, "content": msg.content})
        
        # Add current question with context
        messages.append({
            "role": "user", 
            "content": f"Based on the following notes, please answer the question: '{question}'\n\nNotes:\n{context}\n\nPlease provide a helpful answer based on the information in the notes. If the answer cannot be found in the notes, please say so clearly."
        })
        
        try:
            # Call Ollama API
            answer = await self.llm_service.generate_response(messages, max_tokens=500, temperature=0.7)
            
            if answer:
                # Store conversation history
                self.conversation_manager.add_message(user_id, question, is_user=True)
                self.conversation_manager.add_message(user_id, answer, is_user=False)
                
                return AskResponse(
                    answer=answer,
                    sources=sources
                )
            else:
                return AskResponse(
                    answer="Sorry, I encountered an error while processing your question.",
                    sources=[]
                )
            
        except Exception as e:
            return AskResponse(
                answer=f"Sorry, I encountered an error while processing your question: {str(e)}",
                sources=[]
            )
