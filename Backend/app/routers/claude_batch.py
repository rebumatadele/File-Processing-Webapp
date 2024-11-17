# app/routers/claude_batch.py

import json
import re
import time
import secrets
import aiohttp
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Optional
from app.models.claude_batch import (
    StartBatchProcessingRequest,
    StartBatchProcessingResponse,
    BatchStatusResponse,
    BatchRequestItem
)
from app.utils.claude_batch_utils import create_batch, get_batch_status, list_batches, cancel_batch
from app.utils.file_utils import (
    PROCESSED_DIR,
    handle_error,
    get_uploaded_files,
    load_uploaded_file_content,
    save_processed_result,
    save_uploaded_file
)
from app.utils.text_processing import process_text_stream
from app.utils.email_utils import send_email
import asyncio
import os
from app.settings import settings

router = APIRouter(
    prefix="/processing/claude",
    tags=["Claude Batch Processing"],
    responses={404: {"description": "Not found"}},
)

# In-memory storage for batch statuses (Consider using persistent storage for production)
batch_status_store: Dict[str, Dict] = {}

@router.post("/batch_start", response_model=StartBatchProcessingResponse, summary="Start Claude Batch Processing")
async def start_batch_processing(
    request: StartBatchProcessingRequest,
    background_tasks: BackgroundTasks,
):
    """
    Start a batch processing task with Claude using pre-uploaded files.
    """
    try:
        # Retrieve the list of uploaded files
        uploaded_files = get_uploaded_files()

        if not uploaded_files:
            handle_error("BatchProcessingError", "No files found in storage/uploads for batch processing.")
            raise HTTPException(status_code=400, detail="No files available for batch processing.")

        # Prepare batch requests
        batch_requests = []
        for file_name in uploaded_files:
            content = load_uploaded_file_content(file_name)
            if not content:
                handle_error("BatchProcessingError", f"File '{file_name}' is empty or could not be loaded.")
                continue

            # Chunk the content based on request parameters
            if request.chunk_by.lower() == "word":
                words = content.split()
                chunks = [
                    ' '.join(words[i:i + request.chunk_size])
                    for i in range(0, len(words), request.chunk_size)
                ]
            elif request.chunk_by.lower() == "character":
                chunks = [
                    content[i:i + request.chunk_size]
                    for i in range(0, len(content), request.chunk_size)
                ]
            else:
                handle_error("InvalidChunkBy", "chunk_by must be 'word' or 'character'.")
                raise HTTPException(status_code=400, detail="chunk_by must be 'word' or 'character'.")

            # Function to sanitize the file name (replace invalid characters)
            def sanitize_file_name(file_name):
                # Replace all invalid characters (anything not a-z, A-Z, 0-9, _, or -)
                sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', file_name)
                return sanitized

            # Create batch request items
            for idx, chunk in enumerate(chunks):
                # Sanitize file name (replace spaces and other invalid characters)
                valid_file_name = sanitize_file_name(file_name)

                # Truncate file name to fit within 64 characters limit (taking index into account)
                max_file_name_length = 64 - len(f"_{idx}")  # Only leave space for the index at the end
                truncated_file_name = valid_file_name[:max_file_name_length]

                # Generate custom_id as file_name with index
                custom_id = f"{truncated_file_name}_{idx}"

                # Validate custom_id length and ensure it follows the pattern
                if len(custom_id) > 64:
                    raise ValueError(f"Generated custom_id '{custom_id}' exceeds the length limit.")
                elif not re.match(r'^[a-zA-Z0-9_-]{1,64}$', custom_id):
                    raise ValueError(f"Generated custom_id '{custom_id}' does not match the required pattern.")

                # Define params
                params = {
                    "model": request.selected_model,
                    "max_tokens": 1024,
                    "messages": [
                        {"role": "user", "content": request.prompt + chunk}
                    ],
                }

                # Create batch request item
                batch_request_item = BatchRequestItem(custom_id=custom_id, params=params)
                batch_requests.append(batch_request_item)



        if not batch_requests:
            handle_error("BatchProcessingError", "No valid chunks to process.")
            raise HTTPException(status_code=400, detail="No valid chunks to process.")

        # Retrieve Anthropic API key from user input or settings
        anthropic_api_key = request.anthropic_api_key or settings.anthropic_api_key
        if not anthropic_api_key:
            handle_error("ConfigurationError", "Anthropic API key not provided.")
            raise HTTPException(status_code=400, detail="Anthropic API key not provided.")

        # Create the batch with Anthropic
        batch_response = await create_batch(batch_requests, anthropic_api_key=anthropic_api_key)
        batch_id = batch_response.get("id")

        if not batch_id:
            handle_error("BatchCreationError", "No batch ID returned from Anthropic.")
            raise HTTPException(status_code=500, detail="Failed to create batch.")

        # Store initial batch status
        batch_status_store[batch_id] = {
            "processing_status": "in_progress",
            "request_counts": batch_response.get("request_counts", {}),
            "created_at": batch_response.get("created_at"),
            "ended_at": batch_response.get("ended_at"),
            "expires_at": batch_response.get("expires_at"),
            "results_url": batch_response.get("results_url"),
        }

        # Add a background task to poll for batch completion
        background_tasks.add_task(handle_batch_completion, batch_id, request.email, anthropic_api_key)

        return StartBatchProcessingResponse(batch_id=batch_id, message="Batch processing started successfully.")

    except Exception as e:
        handle_error("BatchStartError", f"Failed to start batch processing: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start batch processing: {e}")


async def handle_batch_completion(batch_id: str, email: Optional[str], anthropic_api_key: str):
    """
    Background task to poll the batch status and handle results once completed.
    """
    try:
        while True:
            status_response = await get_batch_status(batch_id, anthropic_api_key=anthropic_api_key)
            processing_status = status_response.get("processing_status")

            # Update the in-memory store
            batch_status_store[batch_id].update({
                "processing_status": processing_status,
                "request_counts": status_response.get("request_counts", {}),
                "ended_at": status_response.get("ended_at"),
                "expires_at": status_response.get("expires_at"),
                "results_url": status_response.get("results_url")
            })

            if processing_status == "ended":
                break
            elif processing_status in ["failed", "canceled", "expired"]:
                break

            # Wait before polling again
            await asyncio.sleep(10)  # Poll every 10 seconds

        if processing_status == "ended" and status_response.get("results_url"):
            results_url = status_response["results_url"]
            await process_batch_results(batch_id, results_url, email, anthropic_api_key)

    except Exception as e:
        handle_error("BatchCompletionError", f"Error handling batch completion for {batch_id}: {e}")

async def process_batch_results(batch_id: str, results_url: str, email: Optional[str], anthropic_api_key: str):
    """
    Fetch and process the batch results. Optionally send results via email.
    """
    try:
        headers = {
            "anthropic-version": "2023-06-01",
            "anthropic-beta": "message-batches-2024-09-24",
            "Content-Type": "application/json",
            "x-api-key": anthropic_api_key
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(results_url, headers=headers) as resp:
                if resp.status == 200:
                    results = await resp.text()
                    # Each line is a JSON object
                    for line in results.splitlines():
                        result = json.loads(line)
                        custom_id = result.get("custom_id")
                        result_type = result.get("result", {}).get("type")
                        message_content = result.get("result", {}).get("message", {}).get("content")
                        if result_type == "succeeded" and message_content:
                            # Save the processed result
                            processed_file_name = f"{custom_id}_processed.txt"
                            save_processed_result(processed_file_name, message_content)
                        elif result_type == "errored":
                            error_message = result.get("result", {}).get("error", {}).get("message", "Unknown error")
                            handle_error("BatchResultError", f"Request {custom_id} failed: {error_message}")
                        # Handle other result types if necessary

                    if email:
                        # Send an email notification with the processed results
                        email_subject = f"Batch {batch_id} Processing Completed"
                        email_body = f"Your batch processing with ID {batch_id} has been completed. Please find the processed results attached."
                        attachments = [PROCESSED_DIR / f for f in os.listdir(PROCESSED_DIR) if f.startswith(batch_id)]
                        await send_email(
                            subject=email_subject,
                            recipients=[email],
                            body=email_body,
                            attachments=attachments
                        )
                else:
                    error_detail = await resp.text()
                    handle_error("BatchResultsFetchError", f"Failed to fetch results: {error_detail}")

    except Exception as e:
        handle_error("BatchResultsProcessingError", f"Error processing batch results for {batch_id}: {e}")

@router.get("/batch_status/{batch_id}", response_model=BatchStatusResponse, summary="Get Batch Status")
async def get_batch_status_endpoint(batch_id: str):
    """
    Retrieve the status of a specific batch processing task.
    """
    try:
        if batch_id not in batch_status_store:
            raise HTTPException(status_code=404, detail="Batch ID not found.")

        return BatchStatusResponse(
            batch_id=batch_id,
            processing_status=batch_status_store[batch_id].get("processing_status"),
            request_counts=batch_status_store[batch_id].get("request_counts"),
            created_at=batch_status_store[batch_id].get("created_at"),
            ended_at=batch_status_store[batch_id].get("ended_at"),
            expires_at=batch_status_store[batch_id].get("expires_at"),
            results_url=batch_status_store[batch_id].get("results_url")
        )
    except Exception as e:
        handle_error("BatchStatusRetrievalError", f"Failed to retrieve status for batch {batch_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve batch status: {e}")

@router.get("/batch_list", summary="List All Batches")
async def list_batches_endpoint():
    """
    List all batch processing tasks.
    """
    try:
        # Optionally, fetch latest batch statuses from Anthropic
        # For simplicity, returning the in-memory store
        return batch_status_store
    except Exception as e:
        handle_error("BatchListRetrievalError", f"Failed to list batches: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list batches: {e}")

@router.post("/batch_cancel/{batch_id}", summary="Cancel a Batch Processing Task")
async def cancel_batch_endpoint(batch_id: str):
    """
    Cancel an ongoing batch processing task.
    """
    try:
        if batch_id not in batch_status_store:
            raise HTTPException(status_code=404, detail="Batch ID not found.")

        # Determine the Anthropic API key: user-provided or environment variable
        anthropic_api_key = settings.anthropic_api_key  # Assuming it's stored in settings

        if not anthropic_api_key:
            handle_error("ConfigurationError", "Anthropic API key not provided.")
            raise HTTPException(status_code=400, detail="Anthropic API key not provided.")

        cancel_response = await cancel_batch(batch_id, anthropic_api_key=anthropic_api_key)
        # Update the in-memory store
        batch_status_store[batch_id].update(cancel_response)

        return {"batch_id": batch_id, "message": "Batch cancellation initiated."}
    except Exception as e:
        handle_error("BatchCancellationError", f"Failed to cancel batch {batch_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel batch: {e}")
