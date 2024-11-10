# app/routers/processing.py

import time
from fastapi import APIRouter, HTTPException, BackgroundTasks, File, UploadFile
from app.models.processing import ProcessingSettings
from app.utils.file_utils import PROCESSED_DIR, handle_error, get_uploaded_files, load_uploaded_file_content, save_processed_result, save_uploaded_file
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

# In-memory task status storage
task_status: Dict[str, str] = {}

@router.post("/upload", summary="Upload Text Files")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Upload one or multiple text files to the server.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    for file in files:
        try:
            if not file.filename.endswith(".txt"):
                raise HTTPException(status_code=400, detail=f"File '{file.filename}' is not a .txt file.")
            content = await file.read()
            content_str = content.decode('utf-8')  # Assuming text files are utf-8 encoded
            save_uploaded_file(file.filename, content_str)
        except HTTPException as he:
            raise he
        except Exception as e:
            handle_error("UploadError", f"Failed to upload file '{file.filename}': {e}")
            raise HTTPException(status_code=500, detail=f"Failed to upload file '{file.filename}': {e}")

    return {"message": "Files uploaded successfully."}

@router.post("/start", summary="Start Text Processing")
async def start_processing(
    settings: ProcessingSettings,
    background_tasks: BackgroundTasks
):
    """
    Start processing uploaded text files with the specified settings.
    This operation runs in the background.
    """
    try:
        task_id = f"task_{int(time.time())}_{secrets.token_hex(4)}"
        task_status[task_id] = "Processing"
        background_tasks.add_task(process_texts_task, task_id, settings)
        return {"task_id": task_id, "message": "Processing started."}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to start processing: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start processing: {e}")

async def process_texts_task(task_id: str, settings: ProcessingSettings):
    """
    Asynchronous background task to process text files and send emails after processing each file.
    """
    try:
        env_vars = os.environ  # Already loaded in main.py via load_environment_variables
        uploaded_files = get_uploaded_files()
        if not uploaded_files:
            handle_error("ProcessingError", "No uploaded files found.")
            task_status[task_id] = "Failed: No uploaded files."
            return

        # Define a semaphore to limit concurrency (e.g., max 5 concurrent tasks)
        semaphore = asyncio.Semaphore(5)

        async def process_and_email_file(file: str):
            async with semaphore:
                try:
                    content = load_uploaded_file_content(file)
                    if not content:
                        handle_error("ProcessingError", f"File '{file}' is empty or could not be loaded.")
                        return

                    responses = await process_text_stream(
                        text=content,
                        provider_choice=settings.provider_choice,
                        prompt=settings.prompt,
                        chunk_size=settings.chunk_size,
                        chunk_by=settings.chunk_by,
                        model_choice=settings.selected_model,  # Updated reference
                        api_keys=env_vars
                    )
                    merged_text = "\n".join(responses)
                    save_processed_result(file, merged_text)

                    # Path to the processed file
                    processed_file_path = PROCESSED_DIR / file  # Ensure 'file' includes '.txt'

                    if not os.path.exists(processed_file_path):
                        handle_error("FileNotFound", f"Processed file not found: {processed_file_path}")
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
                        handle_error("EmailError", f"Failed to send email for file '{file}': {e}")
                        # Continue processing other files even if email fails
                except Exception as e:
                    handle_error("ProcessingError", f"Failed to process file '{file}': {e}")

        # Create a list of tasks for concurrent processing
        tasks = [process_and_email_file(file) for file in uploaded_files]

        # Run all tasks concurrently
        await asyncio.gather(*tasks)

        task_status[task_id] = "Completed"
    except Exception as e:
        handle_error("ProcessingError", f"Task {task_id} failed: {e}")
        task_status[task_id] = f"Failed: {e}"

@router.get("/status/{task_id}", summary="Get Task Status")
async def get_task_status_endpoint(task_id: str):
    status = task_status.get(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task ID not found.")
    return {"task_id": task_id, "status": status}
