import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

from main import app
from database import Base, get_db
from database import Note

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_notes.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def sample_note():
    return {
        "title": "Test Note",
        "content": "This is a test note for unit testing."
    }

def test_create_note(client, sample_note):
    """Test creating a new note"""
    with patch('main.rag_service.add_note') as mock_add_note:
        response = client.post("/api/notes", json=sample_note)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == sample_note["title"]
        assert data["content"] == sample_note["content"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        
        # Verify RAG service was called
        mock_add_note.assert_called_once()

def test_get_notes(client, sample_note):
    """Test retrieving all notes"""
    # Create a note first
    with patch('main.rag_service.add_note'):
        client.post("/api/notes", json=sample_note)
    
    response = client.get("/api/notes")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == sample_note["title"]

def test_get_note_by_id(client, sample_note):
    """Test retrieving a specific note by ID"""
    # Create a note first
    with patch('main.rag_service.add_note'):
        create_response = client.post("/api/notes", json=sample_note)
        note_id = create_response.json()["id"]
    
    response = client.get(f"/api/notes/{note_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == sample_note["title"]
    assert data["id"] == note_id

def test_get_nonexistent_note(client):
    """Test retrieving a note that doesn't exist"""
    response = client.get("/api/notes/999")
    assert response.status_code == 404
    assert "Note not found" in response.json()["detail"]

def test_update_note(client, sample_note):
    """Test updating an existing note"""
    # Create a note first
    with patch('main.rag_service.add_note'):
        create_response = client.post("/api/notes", json=sample_note)
        note_id = create_response.json()["id"]
    
    # Update the note
    update_data = {
        "title": "Updated Test Note",
        "content": "This is an updated test note."
    }
    
    with patch('main.rag_service.update_note') as mock_update_note:
        response = client.put(f"/api/notes/{note_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["content"] == update_data["content"]
        assert data["id"] == note_id
        
        # Verify RAG service was called
        mock_update_note.assert_called_once()

def test_delete_note(client, sample_note):
    """Test deleting a note"""
    # Create a note first
    with patch('main.rag_service.add_note'):
        create_response = client.post("/api/notes", json=sample_note)
        note_id = create_response.json()["id"]
    
    # Delete the note
    with patch('main.rag_service.remove_note') as mock_remove_note:
        response = client.delete(f"/api/notes/{note_id}")
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        
        # Verify RAG service was called
        mock_remove_note.assert_called_once_with(note_id)
    
    # Verify note is actually deleted
    response = client.get(f"/api/notes/{note_id}")
    assert response.status_code == 404

def test_ask_question_success(client, sample_note):
    """Test asking a question with successful RAG response"""
    # Create a note first
    with patch('main.rag_service.add_note'):
        client.post("/api/notes", json=sample_note)
    
    # Mock RAG service response
    mock_response = {
        "answer": "This is a test answer based on your notes.",
        "sources": ["Note 1: Test Note"]
    }
    
    with patch('main.rag_service.ask_question', return_value=mock_response):
        response = client.post("/api/ask", json={"question": "What is this about?"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["answer"] == mock_response["answer"]
        assert data["sources"] == mock_response["sources"]

def test_ask_question_error(client):
    """Test asking a question when RAG service fails"""
    with patch('main.rag_service.ask_question', side_effect=Exception("RAG service error")):
        response = client.post("/api/ask", json={"question": "What is this about?"})
        assert response.status_code == 500
        assert "Error processing question" in response.json()["detail"]

def test_ask_question_no_notes(client):
    """Test asking a question when no notes exist"""
    mock_response = {
        "answer": "I don't have any notes to search through. Please add some notes first.",
        "sources": []
    }
    
    with patch('main.rag_service.ask_question', return_value=mock_response):
        response = client.post("/api/ask", json={"question": "What is this about?"})
        assert response.status_code == 200
        
        data = response.json()
        assert "don't have any notes" in data["answer"]
        assert data["sources"] == []
