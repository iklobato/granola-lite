from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from dotenv import load_dotenv

from database import get_db, create_tables, Note
from models import NoteCreate, NoteUpdate, NoteResponse
from rag_service import RAGService
from models import AskRequest, AskResponse

load_dotenv()

app = FastAPI(title="Notes App API", version="1.0.0")

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG service
rag_service = RAGService()

@app.on_event("startup")
async def startup_event():
    create_tables()

@app.get("/api/notes", response_model=List[NoteResponse])
async def get_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all notes with pagination"""
    notes = db.query(Note).offset(skip).limit(limit).all()
    return notes

@app.get("/api/notes/{note_id}", response_model=NoteResponse)
async def get_note(note_id: int, db: Session = Depends(get_db)):
    """Get a specific note by ID"""
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.post("/api/notes", response_model=NoteResponse)
async def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    """Create a new note"""
    db_note = Note(title=note.title, content=note.content)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    
    # Update embeddings for RAG
    await rag_service.add_note(db_note, db)
    
    return db_note

@app.put("/api/notes/{note_id}", response_model=NoteResponse)
async def update_note(note_id: int, note: NoteUpdate, db: Session = Depends(get_db)):
    """Update an existing note"""
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    if note.title is not None:
        db_note.title = note.title
    if note.content is not None:
        db_note.content = note.content
    
    db.commit()
    db.refresh(db_note)
    
    # Update embeddings for RAG
    await rag_service.update_note(db_note, db)
    
    return db_note

@app.delete("/api/notes/{note_id}")
async def delete_note(note_id: int, db: Session = Depends(get_db)):
    """Delete a note"""
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(db_note)
    db.commit()
    
    # Remove from RAG index
    await rag_service.remove_note(note_id, db)
    
    return {"message": "Note deleted successfully"}

@app.post("/api/ask", response_model=AskResponse)
async def ask_question(request: AskRequest, user_id: str = "default", db: Session = Depends(get_db)):
    """Ask a question across all notes using RAG"""
    try:
        response = await rag_service.ask_question(request.question, db, user_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

# Conversation Management Endpoints
@app.get("/api/conversations/{user_id}")
async def get_user_conversations(user_id: str, limit: int = 10):
    """Get recent conversations for a user"""
    try:
        conversations = rag_service.conversation_manager.get_conversation_history(user_id, limit=limit)
        stats = rag_service.conversation_manager.get_conversation_stats(user_id)
        return {
            "conversations": conversations,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting conversations: {str(e)}")

@app.get("/api/conversations/{user_id}/{conversation_id}")
async def get_conversation_history(user_id: str, conversation_id: str, limit: int = 20):
    """Get conversation history for a specific conversation"""
    try:
        conversations = rag_service.conversation_manager.get_conversation_history(
            user_id, conversation_id, limit
        )
        return {"conversations": conversations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting conversation history: {str(e)}")

@app.post("/api/conversations/{user_id}/clear")
async def clear_user_conversations(user_id: str):
    """Clear all conversations for a user"""
    try:
        rag_service.conversation_manager.clear_user_memory(user_id)
        return {"message": "Conversations cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing conversations: {str(e)}")

@app.get("/api/llm/status")
async def get_llm_status():
    """Get LLM service status and model information"""
    try:
        health = await rag_service.llm_service.health_check()
        model_info = rag_service.llm_service.get_model_info()
        return {
            "healthy": health,
            "model_info": model_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting LLM status: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
