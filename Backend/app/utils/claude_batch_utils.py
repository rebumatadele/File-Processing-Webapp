# app/utils/claude_batch_utils.py

import os
import json
import aiohttp
from typing import List, Dict, Optional
from app.models.claude_batch import BatchRequestItem
from app.utils.file_utils import handle_error

async def create_batch(
    requests: List[BatchRequestItem],
    anthropic_api_key: Optional[str] = None
) -> Dict:
    ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages/batches"
    headers = {
        "anthropic-version": "2023-06-01",
        "anthropic-beta": "message-batches-2024-09-24",
        "Content-Type": "application/json"
    }
    
    # Use user-provided API key or fallback to environment variable
    if anthropic_api_key:
        headers["x-api-key"] = anthropic_api_key
    else:
        headers["x-api-key"] = os.getenv("ANTHROPIC_API_KEY")
    
    payload = {
        "requests": [item.dict() for item in requests]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(ANTHROPIC_API_URL, headers=headers, json=payload) as resp:
            if resp.status in (200, 201):
                return await resp.json()
            else:
                error_detail = await resp.text()
                handle_error("BatchCreationError", f"Failed to create batch: {error_detail}")
                raise Exception(f"Failed to create batch: {error_detail}")

async def get_batch_status(
    batch_id: str,
    anthropic_api_key: Optional[str] = None
) -> Dict:
    ANTHROPIC_API_URL = f"https://api.anthropic.com/v1/messages/batches/{batch_id}"
    headers = {
        "anthropic-version": "2023-06-01",
        "anthropic-beta": "message-batches-2024-09-24",
        "Content-Type": "application/json"
    }
    
    if anthropic_api_key:
        headers["x-api-key"] = anthropic_api_key
    else:
        headers["x-api-key"] = os.getenv("ANTHROPIC_API_KEY")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(ANTHROPIC_API_URL, headers=headers) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                error_detail = await resp.text()
                handle_error("BatchStatusError", f"Failed to get batch status: {error_detail}")
                raise Exception(f"Failed to get batch status: {error_detail}")

async def list_batches(
    anthropic_api_key: Optional[str] = None
) -> Dict:
    ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages/batches"
    headers = {
        "anthropic-version": "2023-06-01",
        "anthropic-beta": "message-batches-2024-09-24",
        "Content-Type": "application/json"
    }
    
    if anthropic_api_key:
        headers["x-api-key"] = anthropic_api_key
    else:
        headers["x-api-key"] = os.getenv("ANTHROPIC_API_KEY")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(ANTHROPIC_API_URL, headers=headers) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                error_detail = await resp.text()
                handle_error("BatchListError", f"Failed to list batches: {error_detail}")
                raise Exception(f"Failed to list batches: {error_detail}")

async def cancel_batch(
    batch_id: str,
    anthropic_api_key: Optional[str] = None
) -> Dict:
    ANTHROPIC_API_URL = f"https://api.anthropic.com/v1/messages/batches/{batch_id}/cancel"
    headers = {
        "anthropic-version": "2023-06-01",
        "anthropic-beta": "message-batches-2024-09-24",
        "Content-Type": "application/json"
    }
    
    if anthropic_api_key:
        headers["x-api-key"] = anthropic_api_key
    else:
        headers["x-api-key"] = os.getenv("ANTHROPIC_API_KEY")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(ANTHROPIC_API_URL, headers=headers) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                error_detail = await resp.text()
                handle_error("BatchCancelError", f"Failed to cancel batch: {error_detail}")
                raise Exception(f"Failed to cancel batch: {error_detail}")
