# app/routers/claude_batch.py

import json
import re
import time
import secrets
import aiohttp
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Dict, Optional
from app.models.user import User
from app.providers.auth import get_current_user, get_db
from sqlalchemy.orm import Session
from app.schemas.batch_schemas import (
    StartBatchProcessingRequest,
    StartBatchProcessingResponse,
    BatchStatusResponse,
    BatchRequestItemSchema
)
from app.models.claude_batch import Batch, BatchRequestItem
from app.utils.claude_batch_utils import create_batch, get_batch_status, cancel_batch
from app.utils.file_utils import (
    PROCESSED_DIR,
    handle_error,
    get_uploaded_files,
    load_uploaded_file_content,
    save_processed_result,
    get_user_processed_dir,
)
from app.utils.email_utils import send_email
import asyncio
import os
from app.settings import settings

router = APIRouter(
    prefix="/processing/claude",
    tags=["Claude Batch Processing"],
    responses={404: {"description": "Not found"}},
)

@router.post("/batch_start", response_model=StartBatchProcessingResponse, summary="Start Claude Batch Processing")
async def start_batch_processing(
    request: StartBatchProcessingRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Start a batch processing task with Claude using pre-uploaded files.
    """
    try:
        # Retrieve the list of uploaded files for the current user
        uploaded_files = get_uploaded_files(user_id=current_user.id)

        if not uploaded_files:
            handle_error("BatchProcessingError", "No files found for batch processing.", user_id=current_user.id)
            raise HTTPException(status_code=400, detail="No files available for batch processing.")

        # Create a new Batch object
        batch = Batch(
            user_id=current_user.id,
            prompt=request.prompt,
            chunk_size=request.chunk_size,
            chunk_by=request.chunk_by,
            selected_model=request.selected_model,
            email=request.email,
            status="pending"
        )
        db.add(batch)
        db.commit()
        db.refresh(batch)

        # Prepare batch requests
        batch_requests = []
        for file_name in uploaded_files:
            content = load_uploaded_file_content(file_name, user_id=current_user.id)
            if not content:
                handle_error("BatchProcessingError", f"File '{file_name}' is empty or could not be loaded.", user_id=current_user.id)
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
                handle_error("InvalidChunkBy", "chunk_by must be 'word' or 'character'.", user_id=current_user.id)
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

                # Create BatchRequestItem object
                batch_request_item = BatchRequestItem(
                    custom_id=custom_id,
                    params=params,
                    batch_id=batch.id
                )
                db.add(batch_request_item)
                batch_requests.append(batch_request_item)

        if not batch_requests:
            handle_error("BatchProcessingError", "No valid chunks to process.", user_id=current_user.id)
            raise HTTPException(status_code=400, detail="No valid chunks to process.")

        db.commit()

        # Retrieve Anthropic API key from user input or settings
        anthropic_api_key = request.anthropic_api_key or settings.anthropic_api_key
        if not anthropic_api_key:
            handle_error("ConfigurationError", "Anthropic API key not provided.", user_id=current_user.id)
            raise HTTPException(status_code=400, detail="Anthropic API key not provided.")

        # Create the batch with Anthropic
        batch_response = await create_batch(batch_requests, anthropic_api_key=anthropic_api_key)
        batch_id = batch_response.get("id")

        if not batch_id:
            handle_error("BatchCreationError", "No batch ID returned from Anthropic.", user_id=current_user.id)
            raise HTTPException(status_code=500, detail="Failed to create batch.")

        # Update batch with information from Anthropic
        batch.external_batch_id = batch_id
        batch.status = "in_progress"
        batch.created_at = batch_response.get("created_at")
        batch.expires_at = batch_response.get("expires_at")
        db.commit()
        db.refresh(batch)

        # Add a background task to poll for batch completion
        background_tasks.add_task(
            handle_batch_completion, batch_id, request.email, anthropic_api_key, current_user.id, db
        )

        return StartBatchProcessingResponse(batch_id=batch_id, message="Batch processing started successfully.")

    except Exception as e:
        handle_error("BatchStartError", f"Failed to start batch processing: {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=f"Failed to start batch processing: {e}")

async def handle_batch_completion(batch_id: str, email: Optional[str], anthropic_api_key: str, user_id: str, db: Session):
    """
    Background task to poll the batch status and handle results once completed.
    """
    try:
        # Retrieve the Batch object from the database
        batch = db.query(Batch).filter_by(external_batch_id=batch_id, user_id=user_id).first()
        if not batch:
            handle_error("BatchNotFound", f"Batch {batch_id} not found in database.", user_id=user_id)
            return

        while True:
            status_response = await get_batch_status(batch_id, anthropic_api_key=anthropic_api_key)
            processing_status = status_response.get("processing_status")

            # Update the Batch object
            batch.status = processing_status
            batch.request_counts = status_response.get("request_counts", {})
            batch.ended_at = status_response.get("ended_at")
            batch.expires_at = status_response.get("expires_at")
            batch.results_url = status_response.get("results_url")
            db.commit()

            if processing_status == "ended":
                break
            elif processing_status in ["failed", "canceled", "expired"]:
                break

            # Wait before polling again
            await asyncio.sleep(10)  # Poll every 10 seconds

        if processing_status == "ended" and status_response.get("results_url"):
            results_url = status_response["results_url"]
            await process_batch_results(batch_id, results_url, email, anthropic_api_key, user_id, db)

    except Exception as e:
        handle_error("BatchCompletionError", f"Error handling batch completion for {batch_id}: {e}", user_id=user_id)

async def process_batch_results(batch_id: str, results_url: str, email: Optional[str], anthropic_api_key: str, user_id: str, db: Session):
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
                    results_text = await resp.text()
                    # Each line is a JSON object
                    for line in results_text.splitlines():
                        result = json.loads(line)
                        custom_id = result.get("custom_id")
                        result_type = result.get("result", {}).get("type")
                        message_content = result.get("result", {}).get("message", {}).get("content")
                        if result_type == "succeeded" and message_content:
                            # Find the corresponding BatchRequestItem
                            batch_request_item = db.query(BatchRequestItem).filter_by(
                                custom_id=custom_id, batch_id=batch_id
                            ).first()
                            if batch_request_item:
                                batch_request_item.result = message_content
                                db.commit()
                            # Save the processed result to file
                            processed_file_name = f"{custom_id}_processed.txt"
                            save_processed_result(processed_file_name, message_content, user_id=user_id)
                        elif result_type == "errored":
                            error_message = result.get("result", {}).get("error", {}).get("message", "Unknown error")
                            handle_error("BatchResultError", f"Request {custom_id} failed: {error_message}", user_id=user_id)
                        # Handle other result types if necessary

                    if email:
                        # Send an email notification with the processed results
                        email_subject = f"Batch {batch_id} Processing Completed"
                        email_body = f"Your batch processing with ID {batch_id} has been completed. Please find the processed results attached."
                        processed_dir = get_user_processed_dir(user_id)
                        attachments = [processed_dir / f for f in os.listdir(processed_dir) if f.startswith(batch_id)]
                        await send_email(
                            subject=email_subject,
                            recipients=[email],
                            body=email_body,
                            attachments=attachments
                        )
                else:
                    error_detail = await resp.text()
                    handle_error("BatchResultsFetchError", f"Failed to fetch results: {error_detail}", user_id=user_id)

    except Exception as e:
        handle_error("BatchResultsProcessingError", f"Error processing batch results for {batch_id}: {e}", user_id=user_id)

@router.get("/batch_status/{batch_id}", response_model=BatchStatusResponse, summary="Get Batch Status")
async def get_batch_status_endpoint(
    batch_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve the status of a specific batch processing task.
    """
    try:
        batch = db.query(Batch).filter_by(external_batch_id=batch_id, user_id=current_user.id).first()
        if not batch:
            raise HTTPException(status_code=404, detail="Batch ID not found.")

        return BatchStatusResponse(
            batch_id=batch.external_batch_id,
            processing_status=batch.status,
            request_counts=batch.request_counts,
            created_at=batch.created_at,
            ended_at=batch.ended_at,
            expires_at=batch.expires_at,
            results_url=batch.results_url
        )
    except Exception as e:
        handle_error("BatchStatusRetrievalError", f"Failed to retrieve status for batch {batch_id}: {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve batch status: {e}")

@router.get("/batch_list", summary="List All Batches")
async def list_batches_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all batch processing tasks for the current user.
    """
    try:
        batches = db.query(Batch).filter_by(user_id=current_user.id).all()
        return [BatchStatusResponse(
            batch_id=batch.external_batch_id,
            processing_status=batch.status,
            request_counts=batch.request_counts,
            created_at=batch.created_at,
            ended_at=batch.ended_at,
            expires_at=batch.expires_at,
            results_url=batch.results_url
        ) for batch in batches]
    except Exception as e:
        handle_error("BatchListRetrievalError", f"Failed to list batches: {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=f"Failed to list batches: {e}")

@router.post("/batch_cancel/{batch_id}", summary="Cancel a Batch Processing Task")
async def cancel_batch_endpoint(
    batch_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel an ongoing batch processing task.
    """
    try:
        batch = db.query(Batch).filter_by(external_batch_id=batch_id, user_id=current_user.id).first()
        if not batch:
            raise HTTPException(status_code=404, detail="Batch ID not found.")

        # Determine the Anthropic API key: user-provided or environment variable
        anthropic_api_key = settings.anthropic_api_key  # Assuming it's stored in settings

        if not anthropic_api_key:
            handle_error("ConfigurationError", "Anthropic API key not provided.", user_id=current_user.id)
            raise HTTPException(status_code=400, detail="Anthropic API key not provided.")

        cancel_response = await cancel_batch(batch_id, anthropic_api_key=anthropic_api_key)
        # Update the Batch object
        batch.status = "canceled"
        db.commit()

        return {"batch_id": batch_id, "message": "Batch cancellation initiated."}
    except Exception as e:
        handle_error("BatchCancellationError", f"Failed to cancel batch {batch_id}: {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=f"Failed to cancel batch: {e}")
