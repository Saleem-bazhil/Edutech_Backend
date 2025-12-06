# ai_logic/ai_service.py

from core.ai_client import chat_completion
from ai_logic.memory_storage import query_memory


async def run_ai_pipeline(messages: list[dict]) -> str:
    """Full AI logic including memory + Groq"""

    user_question = ""
    for m in reversed(messages):
        if m["role"] == "user":
            user_question = m["content"]
            break

    # memory
    snippets = query_memory(user_question, n_results=3) or []
    context_blob = "\n\n".join(snippets)

    # system + messages
    final_messages = [
        {"role": "system", "content": f"Use this context:\n{context_blob}"}
    ] + messages

    # Groq call
    reply = await chat_completion(final_messages)
    return reply.strip()
