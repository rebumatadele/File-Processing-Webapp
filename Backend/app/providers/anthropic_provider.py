# app/providers/anthropic_provider.py

import asyncio
from curl_cffi.requests import post
from curl_cffi.requests.exceptions import CurlError, HTTPError, ConnectionError, Timeout
from app.utils.retry_decorator import retry
from app.utils.error_utils import handle_error
from app.utils.rate_limiter import rate_limiter_instance
from jose import JWTError
from typing import Tuple, Dict, Any

ANTHROPIC_EXCEPTIONS = (CurlError, HTTPError, ConnectionError, Timeout)

@retry(max_retries=10, initial_wait=2, backoff_factor=2, exceptions=ANTHROPIC_EXCEPTIONS)
async def generate_with_anthropic(prompt: str, api_key: str) -> str:
    """
    High-level asynchronous function to call Anthropic API with rate limiting.
    """
    await rate_limiter_instance.acquire()

    try:
        # Synchronous call in a thread returns content, headers, and status
        content, headers, status = await asyncio.to_thread(
            generate_with_anthropic_sync, prompt, api_key
        )

        # If rate limited, check for Retry-After and wait accordingly
        if status == 429:
            retry_after = headers.get("retry-after")
            if retry_after:
                try:
                    wait_seconds = float(retry_after)
                except ValueError:
                    wait_seconds = 10.0  # default fallback
                handle_error("RateLimit", f"Received 429. Waiting {wait_seconds} seconds before retry.")
                await asyncio.sleep(wait_seconds)
                # Optionally, retry the request once more after waiting
                content, headers, status = await asyncio.to_thread(
                    generate_with_anthropic_sync, prompt, api_key
                )

        # Update rate limiter with new header info
        await rate_limiter_instance.update_from_anthropic_headers(headers)

        if status != 200:
            raise HTTPError(f"Anthropic returned unexpected status: {status}")

        return content

    except Exception as e:
        handle_error("APIError", f"Failed in generate_with_anthropic: {e}")
        raise

def generate_with_anthropic_sync(prompt: str, api_key: str) -> Tuple[str, Dict[str, Any], int]:
    """
    Synchronously makes a request to Anthropic and returns (content, headers, status).
    """
    headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json',
        'anthropic-version': '2023-06-01',
    }
    data = {
        "model": "claude-2",  # change as needed
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024,
    }

    response = post("https://api.anthropic.com/v1/messages", headers=headers, json=data, timeout=30)
    status = response.status_code

    if status == 200:
        try:
            resp_json = response.json()
            content = resp_json.get("content", "")
            return content, response.headers, status
        except Exception as e:
            handle_error("APIError", f"JSON parse error: {e}")
            return "", response.headers, status
    else:
        # For non-200, return empty content but still pass headers and status
        return "", response.headers, status

def validate_anthropic_api_key(api_key: str) -> bool:
    """
    Makes a minimal request to see if Anthropic responds with success
    or an auth error. Returns True if the key appears valid, else False.
    """
    headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json',
        'anthropic-version': '2023-06-01',
    }

    # We'll do a minimal request with a trivial prompt
    data = {
        "model": "claude-3-5-sonnet-20240620",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 2,  # just small usage
    }

    try:
        resp = post('https://api.anthropic.com/v1/messages', headers=headers, json=data, timeout=15)
        if resp.status_code == 200:
            return True
        # 401 or 403 => invalid key
        return False
    except Exception:
        return False