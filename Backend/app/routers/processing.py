import time
import asyncio
import secrets
import os
from typing import List, Dict
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.dependencies.database import get_db
from app.models.user import User
from app.models.processing import ProcessingJob
from app.models.processing_status import ProcessingFileStatus
from app.providers.auth import get_current_user
from app.schemas.processing_schemas import ProcessingSettings
from app.utils.file_utils import (
    handle_error,
    get_uploaded_files,
    load_uploaded_file_content,
    save_processed_result
)
from app.utils.email_utils import send_email
from app.utils.text_processing import process_text_stream

router = APIRouter(
    prefix="/processing",
    tags=["Text Processing"],
    responses={404: {"description": "Not found"}},
)

# (Optional) In-memory dictionary if you still want high-level job status per user
user_task_status: Dict[str, Dict[str, str]] = {}  # user_id -> {task_id -> "status"}

@router.post("/start", summary="Start Text Processing")
async def start_processing(
    settings: ProcessingSettings,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start processing in a background task, returning a `task_id`.
    We'll also create a ProcessingJob DB entry and link files to that job.
    """
    try:
        # 1) Create a new job row in DB so we can track overall progress
        new_job = ProcessingJob(
            user_id=current_user.id,
            provider_choice=settings.provider_choice,
            prompt=settings.prompt,
            chunk_size=settings.chunk_size or 1024,
            chunk_by=settings.chunk_by or "word",
            selected_model=settings.selected_model,
            email=settings.email,
            status="in_progress"
        )
        db.add(new_job)
        db.commit()
        db.refresh(new_job)

        # 2) Create a unique background "task_id" as before (optional)
        task_id = f"task_{int(time.time())}_{secrets.token_hex(4)}"
        if current_user.id not in user_task_status:
            user_task_status[current_user.id] = {}
        user_task_status[current_user.id][task_id] = "Processing"

        # 3) Launch background task
        background_tasks.add_task(
            process_texts_task,
            task_id,
            new_job.id,        # <-- pass job_id to link DB updates
            settings,
            current_user.id
        )

        return {
            "task_id": task_id,
            "job_id": new_job.id,
            "message": "Processing started."
        }

    except Exception as e:
        handle_error("ProcessingError", f"Failed to start processing: {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


async def process_texts_task(task_id: str, job_id: str, settings: ProcessingSettings, user_id: str):
    """
    Background task that:
    1) Loads user files (filtered if needed),
    2) For each file, creates a ProcessingFileStatus row,
    3) Processes chunks via process_text_stream,
    4) Updates chunk-level progress in the DB,
    5) Optionally emails results,
    6) Marks job as completed when done.
    """
    from app.config.database import SessionLocal
    db: Session = SessionLocal()

    try:
        # A) Validate we have a valid job
        job = db.query(ProcessingJob).filter_by(id=job_id, user_id=user_id).first()
        if not job:
            handle_error("ProcessingError", "Job not found in DB.", user_id=user_id)
            user_task_status[user_id][task_id] = "Failed: No such job."
            db.close()
            return

        # B) Get list of uploaded files
        uploaded_files = get_uploaded_files(db, user_id)
        if not uploaded_files:
            handle_error("ProcessingError", "No uploaded files found.", user_id=user_id)
            user_task_status[user_id][task_id] = "Failed: No uploaded files."
            job.status = "failed"
            db.commit()
            db.close()
            return

        # C) Filter by `settings.files` if user selected specific ones
        if settings.files:
            # Remove ".txt" extension and compare ignoring case
            selected_lower = {f.lower().replace(".txt", "") for f in settings.files}
            filtered = []
            for f in uploaded_files:
                normalized = f.lower().replace(".txt", "")
                if normalized in selected_lower:
                    filtered.append(f)
            uploaded_files = filtered
            if not uploaded_files:
                handle_error("ProcessingError", "Selected files not found or empty list.", user_id=user_id)
                user_task_status[user_id][task_id] = "Failed: Selected files not found."
                job.status = "failed"
                db.commit()
                db.close()
                return

        # D) Merge environment or user-provided keys
        db_env_vars = os.environ
        api_keys = {
            "OPENAI_API_KEY": settings.openai_api_key or db_env_vars.get("OPENAI_API_KEY"),
            "ANTHROPIC_API_KEY": settings.anthropic_api_key or db_env_vars.get("ANTHROPIC_API_KEY"),
            "GEMINI_API_KEY": settings.gemini_api_key or db_env_vars.get("GEMINI_API_KEY"),
        }

        # E) Validate provider key
        provider = settings.provider_choice.lower()
        if provider == "openai" and not api_keys["OPENAI_API_KEY"]:
            handle_error("ConfigurationError", "OpenAI API key not provided.", user_id=user_id)
            user_task_status[user_id][task_id] = "Failed: Missing OpenAI key."
            job.status = "failed"
            db.commit()
            db.close()
            return
        elif provider == "anthropic" and not api_keys["ANTHROPIC_API_KEY"]:
            handle_error("ConfigurationError", "Anthropic API key not provided.", user_id=user_id)
            user_task_status[user_id][task_id] = "Failed: Missing Anthropic key."
            job.status = "failed"
            db.commit()
            db.close()
            return
        elif provider == "gemini" and not api_keys["GEMINI_API_KEY"]:
            handle_error("ConfigurationError", "Gemini API key not provided.", user_id=user_id)
            user_task_status[user_id][task_id] = "Failed: Missing Gemini key."
            job.status = "failed"
            db.commit()
            db.close()
            return

        # F) Prepare concurrency
        semaphore = asyncio.Semaphore(5)

        # G) For each file, create a ProcessingFileStatus row, then process
        tasks = []
        for filename in uploaded_files:
            # Let’s do a quick check if we can load content
            content = load_uploaded_file_content(db, filename, user_id)
            if not content:
                handle_error("ProcessingError", f"File '{filename}' is empty or missing.", user_id=user_id)
                continue

            # We want to figure out how many chunks the text will produce
            # We'll do a "dry run" of chunking by reusing the same logic from process_text_stream
            # or we can do it ourselves. For simplicity, let's do a small helper:
            total_chunks = estimate_chunk_count(content, settings.chunk_size, settings.chunk_by)

            # Create a status row in DB
            file_status = ProcessingFileStatus(
                job_id=job_id,
                user_id=user_id,
                filename=filename,
                total_chunks=total_chunks,
                processed_chunks=0,
                progress_percentage=0.0,
                status="in_progress",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(file_status)
            db.commit()
            db.refresh(file_status)

            tasks.append(
                process_single_file(
                    db, file_status, content, settings, api_keys
                )
            )

        # H) Run all file tasks concurrently
        await asyncio.gather(*tasks)

        # I) If we got here, mark job completed (or partially completed)
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        db.commit()

        # J) Update in-memory dictionary as well (optional)
        user_task_status[user_id][task_id] = "Completed"
        db.close()

    except Exception as e:
        handle_error("ProcessingError", f"Background task {task_id} failed: {e}", user_id=user_id)
        user_task_status[user_id][task_id] = f"Failed: {e}"
        db.close()


async def process_single_file(
    db: Session,
    file_status: ProcessingFileStatus,
    content: str,
    settings: ProcessingSettings,
    api_keys: Dict[str, str]
):
    """
    Processes one file chunk-by-chunk via process_text_stream.
    Updates chunk progress in ProcessingFileStatus.
    Optionally sends an email with results.
    """
    try:
        # We can pass a callback to process_text_stream that updates the DB
        def on_chunk_processed():
            # This callback is called after each chunk is done
            file_status.processed_chunks += 1
            file_status.progress_percentage = (
                file_status.processed_chunks / file_status.total_chunks * 100.0
            )
            file_status.updated_at = datetime.utcnow()
            db.commit()

        responses = await process_text_stream(
            text=content,
            provider_choice=settings.provider_choice,
            prompt=settings.prompt,
            chunk_size=settings.chunk_size,
            chunk_by=settings.chunk_by,
            model_choice=settings.selected_model,
            api_keys=api_keys,
            user_id=file_status.user_id,
            db=db,
            progress_callback=on_chunk_processed  # <-- pass callback
        )
        merged_text = "\n".join(responses)
        save_processed_result(db, file_status.filename, merged_text, file_status.user_id)

        # If user wants an email:
        if settings.email:
            email_subject = f"Your Processed File: {file_status.filename}"
            email_body = f"""
            <p>Hello,</p>
            <p>Your file <strong>{file_status.filename}</strong> has been processed successfully.</p>
            <p>Best regards,<br/>Text Processor Team</p>
            """
            try:
                await send_email(
                    subject=email_subject,
                    recipients=[settings.email],
                    body=email_body
                )
            except Exception as ex:
                handle_error("EmailError", f"Failed sending email for '{file_status.filename}': {ex}",
                             user_id=file_status.user_id)

        # Mark file status as completed
        file_status.status = "completed"
        file_status.progress_percentage = 100.0
        file_status.updated_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        file_status.status = "failed"
        file_status.updated_at = datetime.utcnow()
        db.commit()
        handle_error("ProcessingError", f"Failed to process file '{file_status.filename}': {e}",
                     user_id=file_status.user_id)


@router.get("/status/{task_id}", summary="Get Task Status")
def get_task_status_endpoint(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Returns the high-level status from the in-memory dictionary (e.g. "Processing", "Completed").
    For detailed per-file progress, see GET /processing/progress/{job_id}.
    """
    tasks_for_user = user_task_status.get(current_user.id, {})
    status = tasks_for_user.get(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task ID not found.")
    return {"task_id": task_id, "status": status}


@router.get("/progress/{job_id}", summary="Get detailed progress for each file in a job")
def get_processing_progress(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns a list of ProcessingFileStatus rows for the given job_id,
    so the frontend can display per-file progress bars, charts, etc.
    """
    # Check the main job
    job = db.query(ProcessingJob).filter_by(id=job_id, user_id=current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    # Get each file's status
    file_statuses = db.query(ProcessingFileStatus).filter_by(job_id=job_id, user_id=current_user.id).all()
    data = []
    for fs in file_statuses:
        data.append({
            "filename": fs.filename,
            "status": fs.status,
            "processed_chunks": fs.processed_chunks,
            "total_chunks": fs.total_chunks,
            "progress_percentage": fs.progress_percentage
        })

    return {
        "job_id": job.id,
        "job_status": job.status,
        "files": data
    }


def estimate_chunk_count(text: str, chunk_size: int, chunk_by: str) -> int:
    """Quick helper to figure out how many chunks process_text_stream would create."""
    if chunk_by == "word":
        words = text.split()
        return max(1, (len(words) + chunk_size - 1) // chunk_size)
    elif chunk_by == "character":
        return max(1, (len(text) + chunk_size - 1) // chunk_size)
    else:
        return 1  # fallback
