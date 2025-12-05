from fastapi import APIRouter
from fastapi import APIRouter
from schemas.chat_schema import ChatRequest, ChatResponse
from ai_logic.ai_model import chat_completion
from ai_logic.memory_storage import query_memory

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest):
    print("/chat called")
    print("Incoming messages:", req.messages)

    user_question = req.messages[-1].content if req.messages else ""
    print("User question:", user_question)

    # Safely query memory
    try:
        snippets = query_memory(user_question, n_results=3) or []
        print("Memory snippets:", snippets)
    except Exception as e:
        print("Memory query error:", e)
        raise e

    # Safely join context
    try:
        context_blob = "\n\n".join(snippets) if snippets else ""
    except Exception as e:
        print("Context join error:", e)
        raise e

    messages = [
        {
            "role": "system",
            "content": f"Use this context if relevant:\n{context_blob}"
        }
    ]

    # Extend messages safely
    try:
        messages.extend(
            {"role": m.role, "content": m.content}
            for m in req.messages
        )
        print("Final messages to Groq:", messages)
    except Exception as e:
        print("Message formatting error:", e)
        raise e

    # Call Groq safely
    try:
        reply = await chat_completion(messages)
        print("Groq reply:", reply)
    except Exception as e:
        print("GROQ API error:", e)
        raise e

    return ChatResponse(content=reply)
