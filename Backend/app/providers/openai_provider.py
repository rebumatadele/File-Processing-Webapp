# app/providers/openai_provider.py

import os
import errno
import httpx
from typing import Optional
from app.utils.retry_decorator import retry
from app.utils.error_utils import handle_error
from app.utils.rate_limiter import RateLimiter

# Attempt to import specific exceptions; fallback to generic Exception if not available
try:
    from openai.error import RateLimitError, APIConnectionError, Timeout, ContentPolicyViolationError
    OPENAI_EXCEPTIONS = (RateLimitError, APIConnectionError, Timeout, ContentPolicyViolationError)
except ImportError:
    # If specific exceptions are not available, use generic Exception
    OPENAI_EXCEPTIONS = (httpx.HTTPError, )

@retry(max_retries=10, initial_wait=2, backoff_factor=2, exceptions=OPENAI_EXCEPTIONS)
async def generate_with_openai(prompt: str, model: str = "gpt-4", api_key: str = None, rate_limiter: RateLimiter = None) -> str:
    """
    Asynchronously generates content using OpenAI's API with rate limiting.

    Args:
        prompt (str): The input prompt for content generation.
        model (str, optional): The OpenAI model to use. Defaults to "gpt-4".
        api_key (str, optional): Your OpenAI API key. If not provided, it will be fetched from environment variables.
        rate_limiter (RateLimiter, optional): The RateLimiter instance to manage rate limits.

    Returns:
        str: The generated content or an error message.
    """
    if rate_limiter:
        await rate_limiter.acquire()

    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        handle_error("APIError", "OpenAI API key is not set.")
        return "[OpenAI API key not set.]"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)

        if response.status_code == 200:
            response_json = response.json()
            choices = response_json.get("choices", [])
            if choices:
                content = choices[0].get("message", {}).get("content", "")
                if content.strip():
                    return content.strip()
            handle_error("ProcessingError", "OpenAI returned no valid content.")
            raise ValueError("OpenAI returned no valid content.")
        elif response.status_code == 429:
            handle_error("APIError", "OpenAI rate limit exceeded. Please wait before retrying.")
            raise RateLimitError("OpenAI rate limit exceeded. Please wait before retrying.")
        else:
            error_message = response.json().get('error', {}).get('message', 'Unknown error')
            handle_error("APIError", f"OpenAI Error: {response.status_code} - {error_message}")
            raise httpx.HTTPError(f"OpenAI API error: {error_message}")
    except OPENAI_EXCEPTIONS as e:
        handle_error("APIError", f"Failed to connect to OpenAI service: {e}")
        raise e  # Re-raise to trigger retry
    except OSError as e:
        if e.errno == errno.ENOSPC:
            handle_error("StorageError", "No space left on device.")
        else:
            handle_error("APIError", f"An OS error occurred with OpenAI: {e}")
        raise e  # Re-raise to trigger retry
    except Exception as e:
        handle_error("APIError", f"An unexpected error occurred with OpenAI: {e}")
        raise e  # Re-raise to trigger retry
