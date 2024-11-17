# app/utils/text_processing.py

from typing import List, Dict, Optional
from app.providers.openai_provider import generate_with_openai
from app.providers.anthropic_provider import generate_with_anthropic
from app.providers.gemini_provider import generate_with_gemini
import asyncio
from fastapi import HTTPException
from app.utils.file_utils import (
    get_cached_result,
    set_cached_result,
    handle_error
)

async def process_text_stream(
    text: str,
    provider_choice: str,
    prompt: str,
    chunk_size: int,
    chunk_by: str,
    model_choice: Optional[str],
    api_keys: Dict[str, str],
    user_id: str
) -> List[str]:
    """
    Processes the text by chunking and sending each chunk to the selected AI provider.
    Utilizes caching to avoid redundant processing.
    
    Args:
        text (str): The text to process.
        provider_choice (str): The chosen AI provider.
        prompt (str): The prompt to send to the AI model.
        chunk_size (int): The size of each text chunk.
        chunk_by (str): The method to chunk text ('word', 'character').
        model_choice (Optional[str]): The specific model to use.
        api_keys (Dict[str, str]): Dictionary containing API keys.
        user_id (str): The ID of the user.
    
    Returns:
        List[str]: List of responses from the AI provider or cache.
    """
    if chunk_by == "word":
        words = text.split()
        chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    elif chunk_by == "character":
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    else:
        raise ValueError("Invalid chunk_by value. Use 'word' or 'character'.")

    responses = []

    for chunk in chunks:
        # Check cache
        cached = get_cached_result(chunk, provider_choice, model_choice, user_id=user_id)
        if cached:
            responses.append(cached)
            continue  # Skip processing this chunk

        # Process chunk as it's not cached
        if provider_choice.lower() == "openai":
            api_key = api_keys.get("OPENAI_API_KEY")
            if not api_key:
                raise HTTPException(status_code=400, detail="OpenAI API key not provided.")
            response = await generate_with_openai(prompt + chunk, api_key)
        elif provider_choice.lower() == "anthropic":
            api_key = api_keys.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise HTTPException(status_code=400, detail="Anthropic API key not provided.")
            response = await generate_with_anthropic(prompt + chunk, api_key)
        elif provider_choice.lower() == "gemini":
            api_key = api_keys.get("GEMINI_API_KEY")
            if not api_key:
                raise HTTPException(status_code=400, detail="Gemini API key not provided.")
            response = await generate_with_gemini(prompt + chunk, model=model_choice, api_key=api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider_choice}")

        responses.append(response)

        # Cache the result
        try:
            set_cached_result(chunk, provider_choice, model_choice, response, user_id=user_id)
        except Exception as e:
            handle_error("CacheError", f"Failed to cache result for chunk: {e}", user_id=user_id)

    return responses
