from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class NoteBase(BaseModel):
    title: str
    content: str

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class NoteResponse(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    sources: Optional[List[str]] = None
