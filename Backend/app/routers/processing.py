# app/routers/processing.py

import time
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.processing import ProcessingSettings
from app.config.load_env import load_environment_variables
from app.utils.file_utils import handle_error, get_uploaded_files, load_uploaded_file_content, save_processed_result
from app.utils.text_processing import process_text_stream
from app.utils.email_utils import send_email
import os
import asyncio
from typing import List

router = APIRouter(
    prefix="/processing",
    tags=["Text Processing"],
    responses={404: {"description": "Not found"}},
)
@router.post("/start", summary="Start Text Processing")
def start_processing(
    settings: ProcessingSettings,
    background_tasks: BackgroundTasks
):
    """
    Start processing uploaded text files with the specified settings.
    This operation runs in the background.
    """
    try:
        task_id = f"task_{int(time.time())}"
        background_tasks.add_task(run_async_task, task_id, settings)
        return {"task_id": task_id, "message": "Processing started."}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to start processing: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start processing: {e}")

def run_async_task(task_id: str, settings: ProcessingSettings):
    """
    Runs the asynchronous processing task in the event loop.
    """
    loop = asyncio.get_event_loop()
    loop.create_task(process_texts_task(task_id, settings))

async def process_texts_task(task_id: str, settings: ProcessingSettings):
    """
    Asynchronous background task to process text files and send emails after processing each file.
    """
    try:
        env_vars = load_environment_variables()
        uploaded_files = get_uploaded_files()
        if not uploaded_files:
            handle_error("ProcessingError", "No uploaded files found.")
            return

        # Define a semaphore to limit concurrency (e.g., max 5 concurrent tasks)
        semaphore = asyncio.Semaphore(5)

        # Create a list of tasks for concurrent processing
        tasks = [
            process_and_email_file(semaphore, file, settings, env_vars)
            for file in uploaded_files
        ]

        # Run all tasks concurrently
        await asyncio.gather(*tasks)
    except Exception as e:
        handle_error("ProcessingError", f"Task {task_id} failed: {e}")

async def process_and_email_file(semaphore: asyncio.Semaphore, file: str, settings: ProcessingSettings, env_vars: dict):
    """
    Processes a single file and sends an email after processing.
    """
    async with semaphore:
        try:
            content = load_uploaded_file_content(file)
            responses = process_text_stream(
                text=content,
                provider_choice=settings.provider_choice,
                prompt=settings.prompt,
                chunk_size=settings.chunk_size,
                chunk_by=settings.chunk_by,
                selected_model=settings.selected_model,  # Updated reference
                api_keys=env_vars
            )
            merged_text = "\n".join(responses)
            save_processed_result(file, merged_text)

            # Path to the processed file
            processed_file_path = os.path.join("storage", "processed", file)

            # Email details
            email_subject = f"Your Processed File: {file}"
            email_body = f"""
            <p>Dear User,</p>
            <p>Your file <strong>{file}</strong> has been processed successfully. Please find the processed file attached.</p>
            <p>Best regards,<br/>Text Processor Team</p>
            """
            try:
                await send_email(
                    subject=email_subject,
                    recipients=[settings.email],
                    body=email_body,
                    attachments=[processed_file_path]
                )
            except Exception as e:
                handle_error("EmailError", f"Failed to send email for file '{file}': {e}")
                # Continue processing other files even if email fails
        except Exception as e:
            handle_error("ProcessingError", f"Failed to process file '{file}': {e}")
