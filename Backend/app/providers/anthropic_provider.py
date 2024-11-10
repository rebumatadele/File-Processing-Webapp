# app/providers/anthropic_provider.py

import os
import errno
import asyncio
from curl_cffi.requests import post
from curl_cffi.requests.exceptions import (
    CurlError,
    HTTPError,
    ConnectionError,
    Timeout
)
from app.utils.retry_decorator import retry
from app.utils.file_utils import handle_error
import json

# Define the exceptions to catch
ANTHROPIC_EXCEPTIONS = (CurlError, HTTPError, ConnectionError, Timeout)

@retry(max_retries=10, initial_wait=2, backoff_factor=2, exceptions=ANTHROPIC_EXCEPTIONS)
async def generate_with_anthropic(prompt: str, api_key: str) -> str:
    """
    Asynchronously generates content using the Anthropic API by running the synchronous
    `generate_with_anthropic_sync` function in a separate thread.

    Args:
        prompt (str): The input prompt for content generation.
        api_key (str): Your Anthropic API key.

    Returns:
        str: The generated content or an error message.
    """
    try:
        # Run the synchronous function in a separate thread to avoid blocking
        response = await asyncio.to_thread(generate_with_anthropic_sync, prompt, api_key)

        return response

    except ANTHROPIC_EXCEPTIONS as e:
        handle_error("APIError", f"Anthropic API Error: {e}")
        raise e  # Re-raise to trigger retry

    except OSError as e:
        if e.errno == errno.ENOSPC:
            handle_error("StorageError", "No space left on device.")
        else:
            handle_error("APIError", f"An OS error occurred with Anthropic: {e}")
        raise e  # Re-raise to trigger retry

    except Exception as e:
        handle_error("APIError", f"Failed to generate response from Anthropic: {e}")
        raise e  # Re-raise to trigger retry

def generate_with_anthropic_sync(prompt: str, api_key: str) -> str:
    """
    Synchronously generates content using the Anthropic API.

    Args:
        prompt (str): The input prompt for content generation.
        api_key (str): Your Anthropic API key.

    Returns:
        str: The generated content or raises an exception.
    """
    headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json',
        'anthropic-version': '2023-06-01',
    }

    data = {
        "model": "claude-3-5-sonnet-20240620",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024,
    }

    try:
        response = post('https://api.anthropic.com/v1/messages', headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            response_json = response.json()
            content = response_json.get("content")
            print(content)
            if content:
                if isinstance(content, list):
                    return "".join([item.get("text", "") for item in content if "text" in item])
                return content
            else:
                handle_error("ProcessingError", "No content field in Anthropic response.")
                raise ValueError("No content field in response.")
        elif response.status_code == 429:
            handle_error("APIError", "Anthropic rate limit exceeded. Please wait before retrying.")
            raise HTTPError("Anthropic rate limit exceeded. Please wait before retrying.")
        else:
            error_message = response.json().get('error', {}).get('message', 'Unknown error')
            handle_error("APIError", f"Anthropic Error: {response.status_code} - {error_message}")
            raise HTTPError(f"Anthropic API error: {error_message}")
    except ANTHROPIC_EXCEPTIONS as e:
        handle_error("APIError", f"Failed to connect to Anthropic service: {e}")
        raise e  # Re-raise to trigger retry
    except OSError as e:
        if e.errno == errno.ENOSPC:
            handle_error("StorageError", "No space left on device.")
            raise e  # Re-raise as it's a critical error
        else:
            handle_error("APIError", f"An OS error occurred with Anthropic: {e}")
            raise e  # Re-raise to trigger retry
    except Exception as e:
        handle_error("APIError", f"An unexpected error occurred with Anthropic: {e}")
        raise e  # Re-raise to trigger retry
