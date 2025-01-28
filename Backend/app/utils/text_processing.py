# app/utils/text_processing.py

from typing import Any, Callable, List, Dict, Optional
import asyncio
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.providers.openai_provider import generate_with_openai
from app.providers.anthropic_provider import generate_with_anthropic
from app.providers.gemini_provider import generate_with_gemini
from app.utils.error_utils import handle_error
from app.utils.cache_utils import get_cached_result, set_cached_result
from app.utils.rate_limiter import RateLimiter

async def process_text_stream(
    text: str,
    provider_choice: str,
    prompt: str,
    chunk_size: int,
    chunk_by: str,
    model_choice: Optional[str],
    api_keys: Dict[str, str],
    user_id: str,
    db: Session,
    rate_limiters: Dict[str, RateLimiter],
    progress_callback: Optional[Callable[[], None]] = None
) -> List[Dict[str, Any]]:
    """
    Processes the text by chunking and sending each chunk to the selected AI provider.
    Utilizes caching (DB-based) to avoid redundant processing.
    If 'progress_callback' is provided, it is called after each chunk is processed.
    """
    # 1) Split or chunk text
    if chunk_by == "word":
        words = text.split()
        chunks = [
            " ".join(words[i:i + chunk_size])
            for i in range(0, len(words), chunk_size)
        ]
    elif chunk_by == "character":
        chunks = [
            text[i:i + chunk_size]
            for i in range(0, len(text), chunk_size)
        ]
    else:
        raise ValueError("Invalid chunk_by value. Use 'word' or 'character'.")

    # 2) Retrieve the appropriate RateLimiter for the selected provider
    rate_limiter = rate_limiters.get(provider_choice.lower())
    if not rate_limiter:
        raise ValueError(f"No RateLimiter configured for provider: {provider_choice}")

    # 3) For each chunk, check DB cache or call the AI provider
    responses = []
    for chunk in chunks:
        cached = get_cached_result(db, chunk, provider_choice, model_choice, user_id)
        if cached:
            # Use cached response
            responses.append(cached)
            # Optionally update chunk progress here if needed
            if progress_callback:
                progress_callback()
            continue

        # Not cached → call the provider’s generate function
        try:
            if provider_choice.lower() == "openai":
                api_key = api_keys.get("OPENAI_API_KEY")
                if not api_key:
                    raise HTTPException(status_code=400, detail="OpenAI API key not provided.")
                response_text = await generate_with_openai(prompt + chunk, model=model_choice, rate_limiter=rate_limiter, api_key=api_key)

            elif provider_choice.lower() == "anthropic":
                api_key = api_keys.get("ANTHROPIC_API_KEY")
                if not api_key:
                    raise HTTPException(status_code=400, detail="Anthropic API key not provided.")
                response_text = await generate_with_anthropic(prompt + chunk, api_key, model_choice, rate_limiter=rate_limiter)

            elif provider_choice.lower() == "gemini":
                api_key = api_keys.get("GEMINI_API_KEY")
                if not api_key:
                    raise HTTPException(status_code=400, detail="Gemini API key not provided.")
                response_text = await generate_with_gemini(prompt + chunk, model=model_choice, api_key=api_key, rate_limiter=rate_limiter)

            else:
                raise ValueError(f"Unsupported provider: {provider_choice}")

        except Exception as e:
            handle_error("ProviderError", f"Failed generating text via {provider_choice}: {e}", user_id=user_id)
            raise

        # 4) Append to responses & cache the new result
        response_entry = {
            "type": "text",
            "text": response_text
        }
        responses.append(response_entry)
        try:
            set_cached_result(db, chunk, provider_choice, model_choice, response_entry, user_id)
        except Exception as e:
            handle_error("CacheError", f"Failed to cache result: {e}", user_id=user_id)

        # Call the progress_callback after each chunk
        if progress_callback:
            progress_callback()

    return responses
