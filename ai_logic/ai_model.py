# core/ai_client.py
import httpx
from fastapi import HTTPException
from core.config import settings

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


async def chat_completion(messages: list[dict]) -> str:
    """
    messages: list of {"role": "...", "content": "..."}
    returns: AI reply as plain string
    """

    # 1) Ensure API key is configured
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY.startswith("change_me"):
        raise HTTPException(
            status_code=503,
            detail="GROQ_API_KEY is not configured on the server",
        )

    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.GROQ_MODEL,
        "messages": messages,
        "temperature": 0.2,
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(GROQ_URL, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()

            # Try to get the AI message text
            try:
                return data["choices"][0]["message"]["content"].strip()
            except Exception as e:
                # Response format is not what we expected
                raise HTTPException(
                    status_code=502,
                    detail=f"Unexpected response from AI provider: {e}",
                )

    except httpx.HTTPStatusError as e:
        # Groq returned non-2xx status
        try:
            body = e.response.json()
            err = body.get("error") or {}
            code = err.get("code")
            message = err.get("message") or e.response.text

            if code == "model_decommissioned":
                raise HTTPException(
                    status_code=503,
                    detail=(
                        f"AI provider model decommissioned: {message}.\n"
                        "Update `GROQ_MODEL` in your .env to a supported model and restart the server."
                    ),
                )

            raise HTTPException(
                status_code=502,
                detail=f"AI provider returned error: {e.response.status_code} {message}",
            )

        except ValueError:
            # response body is not JSON
            raise HTTPException(
                status_code=502,
                detail=f"AI provider returned error: {e.response.status_code} {e.response.text}",
            )

    except httpx.RequestError as e:
        # Network / connection issue
        raise HTTPException(
            status_code=502,
            detail=f"Error connecting to AI provider: {e}",
        )
