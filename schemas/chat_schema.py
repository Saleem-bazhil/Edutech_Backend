# schemas/chat_schema.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    chat_id: Optional[str] = None  
    messages: List[Message]

class ChatResponse(BaseModel):
    content: str

class ChatMeta(BaseModel):
    id: str
    title: str
    created_at: datetime

class ChatMessage(BaseModel):
    id: str
    chat_id: str
    role: str
    content: str
    created_at: datetime
