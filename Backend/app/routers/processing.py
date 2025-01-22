# app/routers/processing.py

import time
import asyncio
import secrets
import os
from typing import List, Dict
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.models.user import User
from app.providers.auth import get_current_user
from app.schemas.processing_schemas import ProcessingSettings
from app.utils.file_utils import (
    handle_error,
    get_uploaded_files,
    load_uploaded_file_content,
    save_processed_result
)
from app.utils.text_processing import process_text_stream
from app.utils.email_utils import send_email

router = APIRouter(
    prefix="/processing",
    tags=["Text Processing"],
    responses={404: {"description": "Not found"}},
)

# In-memory task status storage
user_task_status: Dict[str, Dict[str, str]] = {}  # user_id -> {task_id -> status}

@router.post("/start", summary="Start Text Processing")
async def start_processing(
    settings: ProcessingSettings,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Start processing in a background task, returning a task_id.
    """
    try:
        task_id = f"task_{int(time.time())}_{secrets.token_hex(4)}"
        if current_user.id not in user_task_status:
            user_task_status[current_user.id] = {}
        user_task_status[current_user.id][task_id] = "Processing"

        # Kick off background task
        background_tasks.add_task(process_texts_task, task_id, settings, current_user.id)
        return {"task_id": task_id, "message": "Processing started."}

    except Exception as e:
        handle_error("ProcessingError", f"Failed to start processing: {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=str(e))

async def process_texts_task(task_id: str, settings: ProcessingSettings, user_id: str):
    """
    Background task to process user’s text files, chunk them, call AI provider, email results, etc.
    """
    try:
        db_env_vars = os.environ  # if you need environment-based keys
        # Acquire a DB session here:
        from app.config.database import SessionLocal
        db: Session = SessionLocal()

        uploaded_files = get_uploaded_files(db, user_id)
        if not uploaded_files:
            handle_error("ProcessingError", "No uploaded files found.", user_id=user_id)
            user_task_status[user_id][task_id] = "Failed: No uploaded files."
            db.close()
            return

        # Filter files if user selected some
        if settings.files:
            selected_lower = set(f.lower().replace(".txt", "") for f in settings.files)
            filtered = []
            for f in uploaded_files:
                normalized = f.lower().replace(".txt", "")
                if normalized in selected_lower:
                    filtered.append(f)
            uploaded_files = filtered
            if not uploaded_files:
                handle_error("ProcessingError", "Selected files not found or empty list.", user_id=user_id)
                user_task_status[user_id][task_id] = "Failed: Selected files not found."
                db.close()
                return

        # Merge user-provided or env-based API keys
        api_keys = {
            "OPENAI_API_KEY": settings.openai_api_key or db_env_vars.get("OPENAI_API_KEY"),
            "ANTHROPIC_API_KEY": settings.anthropic_api_key or db_env_vars.get("ANTHROPIC_API_KEY"),
            "GEMINI_API_KEY": settings.gemini_api_key or db_env_vars.get("GEMINI_API_KEY"),
        }

        # Check required provider key
        provider = settings.provider_choice.lower()
        if provider == "openai" and not api_keys["OPENAI_API_KEY"]:
            handle_error("ConfigurationError", "OpenAI API key not provided.", user_id=user_id)
            user_task_status[user_id][task_id] = "Failed: Missing OpenAI key."
            db.close()
            return
        elif provider == "anthropic" and not api_keys["ANTHROPIC_API_KEY"]:
            handle_error("ConfigurationError", "Anthropic API key not provided.", user_id=user_id)
            user_task_status[user_id][task_id] = "Failed: Missing Anthropic key."
            db.close()
            return
        elif provider == "gemini" and not api_keys["GEMINI_API_KEY"]:
            handle_error("ConfigurationError", "Gemini API key not provided.", user_id=user_id)
            user_task_status[user_id][task_id] = "Failed: Missing Gemini key."
            db.close()
            return

        # Concurrency
        semaphore = asyncio.Semaphore(5)

        async def process_and_email_file(filename: str):
            async with semaphore:
                try:
                    content = load_uploaded_file_content(db, filename, user_id)
                    if not content:
                        handle_error("ProcessingError", f"File '{filename}' is empty/couldn't be loaded.", user_id=user_id)
                        return
                    # Call process_text_stream with a DB session
                    responses = await process_text_stream(
                        text=content,
                        provider_choice=settings.provider_choice,
                        prompt=settings.prompt,
                        chunk_size=settings.chunk_size,
                        chunk_by=settings.chunk_by,
                        model_choice=settings.selected_model,
                        api_keys=api_keys,
                        user_id=user_id,
                        db=db
                    )
                    merged_text = "\n".join(responses)
                    save_processed_result(db, filename, merged_text, user_id)

                    # Possibly send email with results
                    if settings.email:
                        email_subject = f"Your Processed File: {filename}"
                        email_body = f"""
                        <p>Dear User,</p>
                        <p>Your file <strong>{filename}</strong> has been processed successfully.</p>
                        <p>Best regards,<br/>Text Processor Team</p>
                        """
                        try:
                            # If you want to attach the processed text as a file, do so
                            await send_email(
                                subject=email_subject,
                                recipients=[settings.email],
                                body=email_body
                                # attachments=[?] 
                            )
                        except Exception as e:
                            handle_error("EmailError", f"Failed sending email for '{filename}': {e}", user_id=user_id)

                except Exception as e:
                    handle_error("ProcessingError", f"Failed to process file '{filename}': {e}", user_id=user_id)

        # Create tasks for each uploaded file
        tasks = [process_and_email_file(f) for f in uploaded_files]
        await asyncio.gather(*tasks)

        user_task_status[user_id][task_id] = "Completed"
        db.close()

    except Exception as e:
        handle_error("ProcessingError", f"Background task {task_id} failed: {e}", user_id=user_id)
        user_task_status[user_id][task_id] = f"Failed: {e}"

@router.get("/status/{task_id}", summary="Get Task Status")
def get_task_status_endpoint(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    tasks_for_user = user_task_status.get(current_user.id, {})
    status = tasks_for_user.get(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task ID not found.")
    return {"task_id": task_id, "status": status}
