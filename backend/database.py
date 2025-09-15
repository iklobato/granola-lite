from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import ARRAY
from pgvector.sqlalchemy import Vector
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://notes_user:password@localhost:5432/notes_app")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to embeddings
    embeddings = relationship("NoteEmbedding", back_populates="note", cascade="all, delete-orphan")

class NoteEmbedding(Base):
    __tablename__ = "note_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("notes.id", ondelete="CASCADE"), nullable=False)
    embedding = Column(Vector(768), nullable=False)  # nomic-embed-text dimension
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to note
    note = relationship("Note", back_populates="embeddings")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)
