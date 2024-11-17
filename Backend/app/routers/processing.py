# app/routers/processing.py

import time
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from app.models.user import User
from app.providers.auth import get_current_user
from app.schemas.processing_schemas import ProcessingSettings
from app.utils.file_utils import (
    PROCESSED_DIR,
    handle_error,
    get_uploaded_files,
    load_uploaded_file_content,
    save_processed_result,
    get_user_processed_dir
)
from app.utils.text_processing import process_text_stream
from app.utils.email_utils import send_email
import os
from typing import List, Dict
import asyncio
import secrets

router = APIRouter(
    prefix="/processing",
    tags=["Text Processing"],
    responses={404: {"description": "Not found"}},
)

# In-memory task status storage per user
user_task_status: Dict[str, Dict[str, str]] = {}  # user_id -> task_id -> status

@router.post("/start", summary="Start Text Processing")
async def start_processing(
    settings: ProcessingSettings,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Start processing uploaded text files with the specified settings.
    This operation runs in the background.
    """
    try:
        task_id = f"task_{int(time.time())}_{secrets.token_hex(4)}"

        # Initialize user's task status if not exists
        if current_user.id not in user_task_status:
            user_task_status[current_user.id] = {}

        user_task_status[current_user.id][task_id] = "Processing"
        background_tasks.add_task(process_texts_task, task_id, settings, current_user.id)
        return {"task_id": task_id, "message": "Processing started."}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to start processing: {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=f"Failed to start processing: {e}")

async def process_texts_task(task_id: str, settings: ProcessingSettings, user_id: str):
    """
    Asynchronous background task to process text files and send emails after processing each file.
    """
    try:
        # Load environment variables (already loaded in main.py via load_environment_variables)
        env_vars = os.environ
        uploaded_files = get_uploaded_files(user_id=user_id)
        if not uploaded_files:
            handle_error("ProcessingError", "No uploaded files found.", user_id=user_id)
            user_task_status[user_id][task_id] = "Failed: No uploaded files."
            return

        # Prepare API keys: prioritize user-provided keys over environment variables
        api_keys = {
            "OPENAI_API_KEY": settings.openai_api_key or env_vars.get("OPENAI_API_KEY"),
            "ANTHROPIC_API_KEY": settings.anthropic_api_key or env_vars.get("ANTHROPIC_API_KEY"),
            "GEMINI_API_KEY": settings.gemini_api_key or env_vars.get("GEMINI_API_KEY"),
        }

        # Verify that required API keys are available based on provider_choice
        provider = settings.provider_choice.lower()
        if provider == "openai" and not api_keys.get("OPENAI_API_KEY"):
            handle_error("ConfigurationError", "OpenAI API key not provided.", user_id=user_id)
            user_task_status[user_id][task_id] = "Failed: OpenAI API key not provided."
            return
        elif provider == "anthropic" and not api_keys.get("ANTHROPIC_API_KEY"):
            handle_error("ConfigurationError", "Anthropic API key not provided.", user_id=user_id)
            user_task_status[user_id][task_id] = "Failed: Anthropic API key not provided."
            return
        elif provider == "gemini" and not api_keys.get("GEMINI_API_KEY"):
            handle_error("ConfigurationError", "Gemini API key not provided.", user_id=user_id)
            user_task_status[user_id][task_id] = "Failed: Gemini API key not provided."
            return

        # Define a semaphore to limit concurrency (e.g., max 5 concurrent tasks)
        semaphore = asyncio.Semaphore(5)

        async def process_and_email_file(file: str):
            async with semaphore:
                try:
                    content = load_uploaded_file_content(file, user_id=user_id)
                    if not content:
                        handle_error("ProcessingError", f"File '{file}' is empty or could not be loaded.", user_id=user_id)
                        return

                    responses = await process_text_stream(
                        text=content,
                        provider_choice=settings.provider_choice,
                        prompt=settings.prompt,
                        chunk_size=settings.chunk_size,
                        chunk_by=settings.chunk_by,
                        model_choice=settings.selected_model,  # Updated reference
                        api_keys=api_keys,
                        user_id=user_id
                    )
                    merged_text = "\n".join(responses)
                    save_processed_result(file, merged_text, user_id=user_id)

                    # Path to the processed file
                    processed_file_path = get_user_processed_dir(user_id) / file  # Ensure 'file' includes '.txt'

                    if not os.path.exists(processed_file_path):
                        handle_error("FileNotFound", f"Processed file not found: {processed_file_path}", user_id=user_id)
                        return

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
                        handle_error("EmailError", f"Failed to send email for file '{file}': {e}", user_id=user_id)
                        # Continue processing other files even if email fails
                except Exception as e:
                    handle_error("ProcessingError", f"Failed to process file '{file}': {e}", user_id=user_id)

        # Create a list of tasks for concurrent processing
        tasks = [process_and_email_file(file) for file in uploaded_files]

        # Run all tasks concurrently
        await asyncio.gather(*tasks)

        user_task_status[user_id][task_id] = "Completed"
    except Exception as e:
        handle_error("ProcessingError", f"Task {task_id} failed: {e}", user_id=user_id)
        user_task_status[user_id][task_id] = f"Failed: {e}"

@router.get("/status/{task_id}", summary="Get Task Status")
async def get_task_status_endpoint(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    user_tasks = user_task_status.get(current_user.id, {})
    status = user_tasks.get(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task ID not found.")
    return {"task_id": task_id, "status": status}
