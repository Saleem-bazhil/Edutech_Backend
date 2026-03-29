# ai_logic/ai_service.py
from ai_logic.ai_model import chat_completion
from ai_logic.memory_storage import query_memory


async def run_ai_pipeline(messages: list[dict], provider: str | None = None) -> str:
    """Full AI logic including memory + provider call."""

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
    reply = await chat_completion(final_messages, provider=provider)
    return reply.strip()
