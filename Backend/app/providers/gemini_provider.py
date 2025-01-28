# app/providers/gemini_provider.py

import os
import errno
import asyncio
import google.generativeai as genai
from app.utils.retry_decorator import retry
from app.utils.error_utils import handle_error
from app.utils.rate_limiter import RateLimiter
from typing import Tuple, Dict, Any

# Attempt to import specific exceptions; fallback to generic Exception if not available
try:
    from google.generativeai.error import RateLimitError, APIConnectionError, Timeout, GenerativeAIError
    GEMINI_EXCEPTIONS = (RateLimitError, APIConnectionError, Timeout, GenerativeAIError)
except ImportError:
    # If specific exceptions are not available, use generic Exception
    GEMINI_EXCEPTIONS = (Exception,)

@retry(max_retries=10, initial_wait=2, backoff_factor=2, exceptions=GEMINI_EXCEPTIONS)
async def generate_with_gemini(prompt: str, model: str = "gemini-1.5-flash", api_key: str = None, rate_limiter: RateLimiter = None) -> str:
    """
    Asynchronously generates content using the Gemini API with rate limiting.

    Args:
        prompt (str): The input prompt for content generation.
        model (str, optional): The Gemini model to use. Defaults to "gemini-1.5-flash".
        api_key (str, optional): Your Gemini API key. If not provided, it will be fetched from environment variables.
        rate_limiter (RateLimiter, optional): The RateLimiter instance to manage rate limits.

    Returns:
        str: The generated content or an error message.
    """
    if rate_limiter:
        await rate_limiter.acquire()

    try:
        # Ensure the API is configured with the provided API key
        if api_key:
            genai.configure(api_key=api_key)
        else:
            # Fallback to environment variable
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

        model_instance = genai.GenerativeModel(model)

        # Run the synchronous generate_content in a separate thread to avoid blocking
        response = await asyncio.to_thread(model_instance.generate_content, prompt)

        # Log the raw response structure for debugging
        print("Gemini API raw response:", response)

        # Check if the response contains valid candidates
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]  # Get the first candidate

            # Check if the candidate has content with parts and retrieve the text
            if hasattr(candidate.content, 'parts') and candidate.content.parts:
                ret = ''.join([part.text for part in candidate.content.parts if hasattr(part, 'text')])

                # Check if the text is valid and not empty
                if ret and ret.strip():
                    return ret
                else:
                    # Log the safety ratings and finish reason for debugging purposes
                    if getattr(candidate, 'finish_reason', '') == "SAFETY":  # Indicates a content safety issue
                        safety_ratings = getattr(candidate, 'safety_ratings', [])
                        handle_error("ProcessingError", f"Gemini blocked content due to safety concerns. Safety ratings: {safety_ratings}")
                        return "[Content blocked due to safety concerns]"
                    else:
                        handle_error("ProcessingError", "Gemini returned no valid content.")
                        return "[Content blocked due to safety concerns]"
            else:
                handle_error("ProcessingError", "Gemini returned no content parts.")
                return "[No content parts available from Gemini due to SAFETY.]"
        else:
            # Log an error for no valid candidates or a blocked response
            handle_error("ProcessingError", "Gemini returned no valid candidates or the response was blocked.")
            return "[No candidates available or response was blocked.]"

    except GEMINI_EXCEPTIONS as e:
        handle_error("APIError", f"Gemini API Error: {e}")
        raise e  # Re-raise to trigger retry

    except OSError as e:
        if e.errno == errno.ENOSPC:
            handle_error("StorageError", "No space left on device.")
        else:
            handle_error("APIError", f"An OS error occurred with Gemini: {e}")
        raise e  # Re-raise to trigger retry

    except Exception as e:
        handle_error("APIError", f"Failed to generate response from Gemini: {e}")
        raise e  # Re-raise to trigger retry
