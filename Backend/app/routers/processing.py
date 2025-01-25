# app/routers/processing.py

import time
import asyncio
import secrets
import os
from typing import List, Dict
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.file import UploadedFile
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
    save_processed_result,
    get_processed_results,
    sanitize_file_name
)
from app.utils.email_utils import send_email
from app.utils.text_processing import process_text_stream

router = APIRouter(
    prefix="/processing",
    tags=["Text Processing"],
    responses={404: {"description": "Not found"}},
)

# In-memory dictionary: user_id -> {task_id -> "status_string"}
user_task_status: Dict[str, Dict[str, str]] = {}

# Optional: keep track of the active asyncio tasks themselves
active_tasks: Dict[str, "asyncio.Task"] = {}


@router.post("/start", summary="Start Text Processing")
async def start_processing(
    settings: ProcessingSettings,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    POST endpoint to start an async background job. 
    Returns a `task_id` so the frontend can poll /processing/status/{task_id}.
    """
    try:
        # 1) Create a new job row in DB to track overall progress
        new_job = ProcessingJob(
            user_id=current_user.id,
            provider_choice=settings.provider_choice,
            prompt=settings.prompt,
            chunk_size=settings.chunk_size or 1024,
            chunk_by=settings.chunk_by or "word",
            selected_model=settings.selected_model,
            email=settings.email,
            status="in_progress",
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        db.add(new_job)
        db.commit()
        db.refresh(new_job)

        # 2) Generate a unique task_id
        task_id = f"task_{int(time.time())}_{secrets.token_hex(4)}"

        # 3) Track high-level status in memory
        if current_user.id not in user_task_status:
            user_task_status[current_user.id] = {}
        user_task_status[current_user.id][task_id] = "Processing"

        # 4) Launch an actual async task using asyncio.create_task
        task = asyncio.create_task(
            process_texts_task(
                task_id=task_id,
                job_id=new_job.id,
                settings=settings,
                user_id=current_user.id
            )
        )
        active_tasks[task_id] = task

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
    **Async** background routine:
      1) Looks up the job & files in DB
      2) Creates a ProcessingFileStatus entry per file
      3) Splits text into chunks and calls `process_text_stream` 
      4) Updates DB after each chunk
      5) Marks job as completed or failed
      6) Creates a final results file
      7) Sends the final results file via email
    """
    from app.config.database import SessionLocal
    db: Session = SessionLocal()

    print("Inside the process_task, Line One")

    try:
        # A) Validate we have a valid job
        job = db.query(ProcessingJob).filter_by(id=job_id, user_id=user_id).first()
        if not job:
            handle_error("ProcessingError", "Job not found in DB.", user_id=user_id)
            user_task_status[user_id][task_id] = "Failed: No such job."
            db.close()
            return

        # B) Get user-uploaded files
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
            selected_lower = {f.lower().replace(".txt", "") for f in settings.files}
            filtered = []
            for f in uploaded_files:
                normalized = f.lower().replace(".txt", "")
                if normalized in selected_lower:
                    filtered.append(f)
            uploaded_files = filtered
            if not uploaded_files:
                handle_error("ProcessingError", "Selected files not found or empty list.", user_id=user_id)
                user_task_status[user_id][task_id] = "Failed: No matching files."
                job.status = "failed"
                db.commit()
                db.close()
                return

        # D) Get or merge API keys
        env_vars = os.environ
        api_keys = {
            "OPENAI_API_KEY": settings.openai_api_key or env_vars.get("OPENAI_API_KEY"),
            "ANTHROPIC_API_KEY": settings.anthropic_api_key or env_vars.get("ANTHROPIC_API_KEY"),
            "GEMINI_API_KEY": settings.gemini_api_key or env_vars.get("GEMINI_API_KEY"),
        }

        # E) Validate provider key
        provider = settings.provider_choice.lower()
        if provider == "openai" and not api_keys["OPENAI_API_KEY"]:
            handle_error("ConfigError", "OpenAI key missing", user_id=user_id)
            user_task_status[user_id][task_id] = "Failed: Missing OpenAI key."
            job.status = "failed"
            db.commit()
            db.close()
            return
        elif provider == "anthropic" and not api_keys["ANTHROPIC_API_KEY"]:
            handle_error("ConfigError", "Anthropic key missing", user_id=user_id)
            user_task_status[user_id][task_id] = "Failed: Missing Anthropic key."
            job.status = "failed"
            db.commit()
            db.close()
            return
        elif provider == "gemini" and not api_keys["GEMINI_API_KEY"]:
            handle_error("ConfigError", "Gemini key missing", user_id=user_id)
            user_task_status[user_id][task_id] = "Failed: Missing Gemini key."
            job.status = "failed"
            db.commit()
            db.close()
            return

        print("Inside the process_task, Line Two")

        # F) Process each file concurrently, but limit concurrency 
        concurrency_limit = asyncio.Semaphore(5)
        tasks = []

        for filename in uploaded_files:
            content = load_uploaded_file_content(db, filename, user_id)
            if not content:
                handle_error("ProcessingError", f"File '{filename}' is empty or missing.", user_id=user_id)
                continue

            total_chunks = estimate_chunk_count(content, settings.chunk_size, settings.chunk_by)
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
                    db=db,
                    file_status=file_status,
                    content=content,
                    settings=settings,
                    api_keys=api_keys,
                    concurrency_limit=concurrency_limit
                )
            )

        # G) Use return_exceptions=True to catch all exceptions (instead of raising immediately).
        print("About to gather tasks...")
        results = await asyncio.gather(*tasks, return_exceptions=True)

        print("Inside the process_task, Line three")
        print("Gather results:", results)

        # Check if any of the results were exceptions
        for i, res in enumerate(results):
            if isinstance(res, Exception):
                print(f"Task {i} had an exception: {res}")

        # H) Create a final results file by aggregating all processed results
        try:
            processed_results = get_processed_results(db, user_id)
            if not processed_results:
                raise Exception("No processed results found to create final results file.")

            final_content = ""
            for fname, content in processed_results.items():
                final_content += f"===== {fname} =====\n{content}\n\n"

            # Define temporary directory and file path
            tmp_dir = f"tmp_downloads/{user_id}"
            os.makedirs(tmp_dir, exist_ok=True)
            final_filename = f"final_results_{job_id}.txt"
            final_file_path = os.path.join(tmp_dir, sanitize_file_name(final_filename))

            # Write the final content to the file
            with open(final_file_path, "w", encoding="utf-8") as f:
                f.write(final_content)

            print(f"Final results file created at {final_file_path}")

        except Exception as e:
            handle_error("FinalFileError", f"Failed to create final results file: {e}", user_id=user_id)
            user_task_status[user_id][task_id] = "Failed: Final results file creation."
            job.status = "failed"
            db.commit()
            db.close()
            return

        # I) Send the final results file via email if email is provided
        if settings.email:
            subject = "Your Final Processed Results"
            body = f"""
            <p>Hello,</p>
            <p>Your text processing job <strong>{job_id}</strong> has been completed successfully.</p>
            <p>Please find the attached final results file.</p>
            <p>Regards,<br/>Text Processor Team</p>
            """
            try:
                await send_email(
                    subject=subject,
                    recipients=[settings.email],
                    body=body,
                    attachments=[final_file_path]
                )
                print("Final results email sent successfully.")
            except Exception as ex:
                handle_error("EmailError", f"Failed to send final results email: {ex}", user_id=user_id)

        # J) Update job status to completed
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        db.commit()

        user_task_status[user_id][task_id] = "Completed"
        db.close()

    except Exception as e:
            # If *any* unhandled exception occurs, mark job as failed in DB + in-memory
            user_task_status[user_id][task_id] = f"Failed: {e}"
            handle_error("ProcessingError", f"Job {job_id} background task failed: {e}", user_id=user_id)
            db.close()

async def process_single_file(
    db: Session,
    file_status: ProcessingFileStatus,
    content: str,
    settings: ProcessingSettings,
    api_keys: Dict[str, str],
    concurrency_limit: asyncio.Semaphore
):
    try:
        def on_chunk_processed():
            file_status.processed_chunks += 1
            file_status.progress_percentage = (
                file_status.processed_chunks / file_status.total_chunks * 100.0
            )
            file_status.updated_at = datetime.utcnow()
            db.commit()

        # Retrieve uploaded_file_id based on filename and user_id
        uploaded_file = db.query(UploadedFile).filter_by(filename=file_status.filename, user_id=file_status.user_id).first()
        if not uploaded_file:
            handle_error("ProcessingError", f"Uploaded file '{file_status.filename}' not found.", user_id=file_status.user_id)
            print(f"[ClaudeDEBUG] Uploaded file '{file_status.filename}' not found in DB.")
            return Exception(f"Uploaded file '{file_status.filename}' not found.")

        uploaded_file_id = uploaded_file.id

        async with concurrency_limit:
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
                progress_callback=on_chunk_processed
            )

        print(f"[ClaudeDEBUG] Done processing chunks for {file_status.filename}, # responses={len(responses)}")

         # Extract text from each response dictionary
        extracted_texts = []
        for resp in responses:
            if isinstance(resp, dict) and 'text' in resp:
                extracted_texts.append(resp['text'])
            elif isinstance(resp, str):
                extracted_texts.append(resp)
            else:
                # Handle unexpected response format
                handle_error("ProcessingError", f"Unexpected response format: {resp}", user_id=file_status.user_id)
                print(f"[ClaudeDEBUG] Unexpected response format: {resp}")

        # Join the extracted texts
        merged_text = "\n".join(extracted_texts)

        # Save the processed result
        save_processed_result(db, file_status.filename, merged_text, uploaded_file_id)  # Pass uploaded_file_id

        file_status.status = "completed"
        file_status.progress_percentage = 100.0
        file_status.updated_at = datetime.utcnow()
        db.commit()

        print(f"[ClaudeDEBUG] Completed {file_status.filename}")
        return f"Success: {file_status.filename}"


    except Exception as e:
        file_status.status = "failed"
        file_status.updated_at = datetime.utcnow()
        db.commit()
        print(f"[ClaudeDEBUG] Exception in process_single_file({file_status.filename}): {e}")
        handle_error("ProcessingError", f"File '{file_status.filename}' failed: {e}", user_id=file_status.user_id)
        return e


@router.get("/status/{task_id}", summary="Get Task Status")
def get_task_status_endpoint(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Returns the high-level status from the in-memory dictionary (e.g. 
    "Processing", "Completed", or "Failed: ...").
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
    so the frontend can display per-file progress bars, etc.
    """
    job = db.query(ProcessingJob).filter_by(id=job_id, user_id=current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

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
    """
    Quick helper that calculates how many chunks `process_text_stream` 
    will generate for a given chunk_size/chunk_by.
    """
    if chunk_by == "word":
        words = text.split()
        return max(1, (len(words) + chunk_size - 1) // chunk_size)
    elif chunk_by == "character":
        return max(1, (len(text) + chunk_size - 1) // chunk_size)
    else:
        return 1  # fallback
