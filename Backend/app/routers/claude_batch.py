# app/routers/claude_batch.py

import re
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
import httpx

from app.models.user import User
from app.providers.auth import get_current_user, get_db
from app.models.claude_batch import Batch
from app.utils.file_utils import (
    handle_error,
    get_uploaded_files,
    load_uploaded_file_content,
)

router = APIRouter(
    prefix="/processing/claude",
    tags=["Claude Batch Processing (Integration Service)"],
    responses={404: {"description": "Not found"}},
)

# Point to your external Integration Service
INTEGRATION_BASE_URL = "https://claude-integration-service-1.onrender.com"


@router.post("/batch_start")
async def start_batch_processing(
    prompt: str,
    chunk_size: int,
    chunk_by: str,
    email: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Start a batch processing task using the external Claude Integration Service.
    Previously, this used claude_batch_utils to talk to Anthropic directly.
    Now it sends chunks to the Integration Service's queue.
    """
    try:
        # 1) Gather user's uploaded files
        uploaded_files = get_uploaded_files(user_id=current_user.id)
        if not uploaded_files:
            raise HTTPException(status_code=400, detail="No files found for batch processing.")

        # 2) Chunk the text from each file
        all_chunks = []
        for file_name in uploaded_files:
            content = load_uploaded_file_content(file_name, user_id=current_user.id)
            if not content:
                # If file is empty or not found, skip
                continue

            # Chunk by word or character
            if chunk_by.lower() == "word":
                words = content.split()
                chunked = [
                    ' '.join(words[i:i + chunk_size])
                    for i in range(0, len(words), chunk_size)
                ]
            elif chunk_by.lower() == "character":
                chunked = [
                    content[i:i + chunk_size]
                    for i in range(0, len(content), chunk_size)
                ]
            else:
                raise HTTPException(
                    status_code=400,
                    detail="chunk_by must be 'word' or 'character'."
                )

            # Prepend prompt
            for c in chunked:
                combined_text = f"{prompt}\n\n{c}"
                # Priority can be 1 (or dynamic)
                all_chunks.append({"text": combined_text, "priority": 1})

        if not all_chunks:
            raise HTTPException(status_code=400, detail="No valid chunks to process.")

        # 3) Build JSON payload with your callback URL
        # If you're testing locally and can't use a real domain, consider using ngrok or skipping callback
        callback_url = "https://file-processing-webapp.onrender.com/processing/claude/batch_callback/"

        payload = {
            "chunks": all_chunks,
            "callback_url": callback_url
        }

        # 4) Send to Integration Service
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(f"{INTEGRATION_BASE_URL}/queue/bulk", json=payload)
            response.raise_for_status()  # Raise exception if not 2xx
            data = response.json()

        job_id = data.get("job_id")
        if not job_id:
            raise HTTPException(status_code=500, detail="No job_id returned from Integration Service.")

        # 5) Store job_id in your local Batch table
        new_batch = Batch(
            user_id=current_user.id,
            external_batch_id=job_id,
            prompt=prompt,
            chunk_size=chunk_size,
            chunk_by=chunk_by,
            selected_model="claude-integration",
            email=email,
            status="in_progress",
        )
        db.add(new_batch)
        db.commit()
        db.refresh(new_batch)

        return {
            "batch_id": job_id,
            "message": "Batch processing started successfully via Integration Service."
        }

    except Exception as e:
        handle_error("BatchStartError", f"Failed to start batch processing: {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/batch_status/{batch_id}")
def get_batch_status(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Local endpoint for checking the batch status in the local DB.
    (We rely on the callback to update status to 'ended'.)
    """
    batch = db.query(Batch).filter(
        Batch.external_batch_id == batch_id,
        Batch.user_id == current_user.id
    ).first()

    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found.")

    return {
        "batch_id": batch_id,
        "status": batch.status,
        "ended_at": batch.ended_at,
        "results_url": batch.results_url,
    }


@router.get("/batch_final_result/{batch_id}")
async def get_batch_final_result(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    If the batch has ended, fetch the final result from the Integration Service
    OR (if using your local stored file) return from local storage.
    """
    # 1) Get batch from local DB
    batch = db.query(Batch).filter(
        Batch.external_batch_id == batch_id,
        Batch.user_id == current_user.id
    ).first()

    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found.")

    # 2) If status isn't 'ended', optionally you can try to retrieve partial results
    if batch.status != "ended":
        raise HTTPException(
            status_code=400,
            detail="Batch is not yet ended. Please try again later."
        )

    # OPTION B: Poll the Integration Service for the final result:
    job_id = batch.external_batch_id
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            result_resp = await client.get(f"{INTEGRATION_BASE_URL}/final_result/{job_id}")
            if result_resp.status_code == 200:
                data = result_resp.json()
                return {"final_result": data.get("final_result", "")}
            else:
                # e.g. 404 if job not found
                raise HTTPException(
                    status_code=result_resp.status_code,
                    detail=f"Could not get final result from Integration Service (status: {result_resp.status_code})"
                )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
