import httpx
from fastapi import HTTPException
from core.config import settings

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def _resolve_provider(provider: str | None) -> str:
    selected = (provider or settings.AI_PROVIDER or "grok").strip().lower()
    aliases = {
        "grok": "groq",
        "frok": "groq",
        "groq": "groq",
        "gemini": "gemini",
    }

    normalized = aliases.get(selected)
    if not normalized:
        raise HTTPException(
            status_code=400,
            detail="Unsupported AI provider. Use 'grok', 'frok', 'groq', or 'gemini'.",
        )
    return normalized


async def _chat_completion_groq(messages: list[dict]) -> str:
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


async def _chat_completion_openrouter(messages: list[dict]) -> str:
    if not settings.OPENROUTER_API_KEY or settings.OPENROUTER_API_KEY.startswith("change_me"):
        raise HTTPException(
            status_code=503,
            detail="OPENROUTER_API_KEY is not configured on the server",
        )

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.OPENROUTER_MODEL,
        "messages": messages,
        "temperature": 0.2,
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(OPENROUTER_URL, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            try:
                return data["choices"][0]["message"]["content"].strip()
            except Exception as e:
                raise HTTPException(
                    status_code=502,
                    detail=f"Unexpected response from OpenRouter: {e}",
                )

    except httpx.HTTPStatusError as e:
        try:
            body = e.response.json()
            error = body.get("error") or {}
            message = error.get("message") or e.response.text
            raise HTTPException(
                status_code=502,
                detail=f"OpenRouter returned error: {e.response.status_code} {message}",
            )
        except ValueError:
            raise HTTPException(
                status_code=502,
                detail=f"OpenRouter returned error: {e.response.status_code} {e.response.text}",
            )

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Error connecting to OpenRouter: {e}",
        )


async def chat_completion(messages: list[dict], provider: str | None = None) -> str:
    selected_provider = _resolve_provider(provider)
    print("Resolved provider:", selected_provider)
    if selected_provider == "gemini":
        return await _chat_completion_openrouter(messages)
    return await _chat_completion_groq(messages)
