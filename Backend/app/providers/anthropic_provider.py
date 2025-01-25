# app/providers/anthropic_provider.py

import asyncio
from curl_cffi.requests import post
from curl_cffi.requests.exceptions import CurlError, HTTPError, ConnectionError, Timeout
from app.utils.retry_decorator import retry
from app.utils.error_utils import handle_error
from app.utils.rate_limiter import rate_limiter_instance
from typing import Tuple, Dict, Any

ANTHROPIC_EXCEPTIONS = (CurlError, HTTPError, ConnectionError, Timeout)

@retry(max_retries=3, initial_wait=2, backoff_factor=2, exceptions=ANTHROPIC_EXCEPTIONS)
async def generate_with_anthropic(prompt: str, api_key: str, model_choice: str) -> str:
    """
    High-level asynchronous function to call Anthropic API with rate limiting.
    Returns the concatenated text from the response.
    """
    await rate_limiter_instance.acquire()

    print("[Anthropic] Starting request with prompt length:", len(prompt))

    try:
        # Synchronous call in a thread returns content, headers, and status
        content, headers, status = await asyncio.to_thread(
            generate_with_anthropic_sync, prompt, api_key, model_choice
        )

        print(f"[Anthropic] Response status={status}  len(content)={len(content)}")

        # If rate limited, check for Retry-After and wait
        if status == 429:
            retry_after = headers.get("retry-after")
            if retry_after:
                try:
                    wait_seconds = float(retry_after)
                except ValueError:
                    wait_seconds = 10.0  # fallback
                handle_error("RateLimit", f"Received 429. Waiting {wait_seconds} seconds before retry.")
                print(f"[Anthropic] 429 Too Many Requests. Sleeping {wait_seconds}s, then retry once more.")
                await asyncio.sleep(wait_seconds)
                # Retry the request once more after waiting
                content, headers, status = await asyncio.to_thread(
                    generate_with_anthropic_sync, prompt, api_key, model_choice
                )
                print(f"[Anthropic] Retried. New status={status}, len(content)={len(content)}")

        # Specific handling for 403 Forbidden
        if status == 403:
            handle_error("AnthropicAuthError", "403 Forbidden: Invalid or unauthorized Anthropic API key.")
            print("[Anthropic] 403 Forbidden: Invalid or unauthorized Anthropic API key.")
            raise HTTPError(f"Anthropic returned unexpected status: {status}")

        # Update rate limiter with new header info
        await rate_limiter_instance.update_from_anthropic_headers(headers)

        if status != 200:
            handle_error("APIError", f"Anthropic returned unexpected status: {status}")
            raise HTTPError(f"Anthropic returned unexpected status: {status}")

        print("[Anthropic] Done. Returning content of length", len(content))
        return content

    except Exception as e:
        print(f"[Anthropic] Exception: {e}")
        handle_error("APIError", f"Failed in generate_with_anthropic: {e}")
        raise

def generate_with_anthropic_sync(prompt: str, api_key: str, model_choice: str) -> Tuple[str, Dict[str, Any], int]:
    """
    Synchronously makes a request to Anthropic and returns (content, headers, status).
    Extracts and concatenates 'text' fields from the 'content' list.
    """
    headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json',
        'anthropic-version': '2023-06-01',
    }
    data = {
        "model": model_choice,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024,
    }

    print("[AnthropicSync] POSTing to Anthropic with data size ~", len(str(data)))

    try:
        response = post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data,
            timeout=60  # 60-second timeout
        )
    except Exception as ex:
        print("[AnthropicSync] Hard exception from post():", ex)
        raise

    status = response.status_code
    if status == 200:
        try:
            resp_json = response.json()
            # Extract 'text' from each item in 'content' list
            content_list = resp_json.get("content", [])
            if isinstance(content_list, list):
                texts = [
                    item.get("text", "") 
                    for item in content_list 
                    if isinstance(item, dict) and 'text' in item
                ]
                content = "\n".join(texts)  # Concatenate texts with newline separators
            elif isinstance(content_list, str):
                # In case 'content' is a single string
                content = content_list
            else:
                # Unexpected format
                content = ""
                handle_error("APIError", f"Unexpected 'content' format: {content_list}")
                print(f"[AnthropicSync] Unexpected 'content' format: {content_list}")
            return content, response.headers, status
        except Exception as e:
            handle_error("APIError", f"JSON parse error: {e}")
            print(f"[AnthropicSync] JSON parse error: {e}")
            return "", response.headers, status
    else:
        # For non-200, return empty content but still pass headers/status
        handle_error("APIError", f"Anthropic returned status: {status}")
        print(f"[AnthropicSync] Non-200 status received: {status}")
        return "", response.headers, status

def validate_anthropic_api_key(api_key: str) -> bool:
    """
    Test a minimal request to see if Anthropic responds with success
    or an auth error. Returns True if the key appears valid, else False.
    """
    headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json',
        'anthropic-version': '2023-06-01',
    }
    data = {
        "model": "claude-2",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 2,
    }

    try:
        resp = post("https://api.anthropic.com/v1/messages", headers=headers, json=data, timeout=15)
        if resp.status_code == 200:
            return True
        # 401 or 403 => invalid key
        print("Invalid API Key")
        return False
    except Exception as e:
        print(f"[AnthropicSync] Exception during API key validation: {e}")
        return False
