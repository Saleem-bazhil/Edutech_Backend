from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.chat_schema import ChatRequest, ChatResponse, ChatMeta, ChatMessage
from models.chat import Chat, Message
from core.database import get_db
from ai_logic.ai_model import chat_completion
from ai_logic.memory_storage import query_memory
from uuid import uuid4
from datetime import datetime
from typing import List

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest, db: Session = Depends(get_db)):
    print("Backend received provider:", req.provider)

    if not req.chat_id:
        raise HTTPException(status_code=400, detail="chat_id is required")

    chat = db.query(Chat).filter(Chat.id == req.chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # USER QUESTION
    user_question = req.messages[-1].content

    snippets = query_memory(user_question, n_results=3) or []
    context_blob = "\n\n".join(snippets) if snippets else ""

    llm_messages = [
        {"role": "system", "content": f"Use this context:\n{context_blob}"}
    ]

    llm_messages.extend(
        {"role": m.role, "content": m.content} for m in req.messages
    )

    # call llm
    reply = await chat_completion(llm_messages, provider=req.provider)

    now = datetime.utcnow()
    
    if chat.title == "New Chat":
        first_user_msg = next(
            (m.content for m in req.messages if m.role == "user"),
            None,
        )
        if first_user_msg:
            title = first_user_msg.strip().split("\n")[0]  
            if len(title) > 40:
                title = title[:37] + "..."
            chat.title = title

    # save message
    for m in req.messages:
        msg = Message(
            id=str(uuid4()),
            chat_id=req.chat_id,
            role=m.role,
            content=m.content,
            created_at=now,
        )
        db.add(msg)

    # save ai reply
    bot_msg = Message(
        id=str(uuid4()),
        chat_id=req.chat_id,
        role="assistant",
        content=reply,
        created_at=now,
    )
    db.add(bot_msg)

    db.commit()

    return ChatResponse(content=reply)


# create chat
@router.post("/new", response_model=ChatMeta)
def create_new_chat(title: str | None = None, db: Session = Depends(get_db)):
    chat = Chat(
        id=str(uuid4()),
        title=title or "New Chat",
        created_at=datetime.utcnow(),
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


# chat history
@router.get("/history", response_model=List[ChatMeta])
def get_chat_history(db: Session = Depends(get_db)):
    chats = db.query(Chat).order_by(Chat.created_at.desc()).all()
    return chats


#chat delete
@router.delete("/{chat_id}")
def delete_chat(chat_id: str, db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    db.delete(chat)
    db.commit()

    return {"deleted": True}


#chat message
@router.get("/{chat_id}/messages", response_model=List[ChatMessage])
def get_chat_messages(chat_id: str, db: Session = Depends(get_db)):
    msgs = db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at.asc()).all()
    return msgs
