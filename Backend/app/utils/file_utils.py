# app/utils/file_utils.py

import os
import time
import shutil
import errno
import re
from pathlib import Path

# Define paths using pathlib for better path handling
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Adjust as per directory structure
ERROR_LOG_PATH = BASE_DIR / "logs" / "error_log.txt"
PROMPTS_DIR = BASE_DIR / "prompts"
UPLOAD_DIR = BASE_DIR / "storage" / "uploads"
PROCESSED_DIR = BASE_DIR / "storage" / "processed"

def handle_error(error_type: str, message: str):
    """
    Logs errors to a file with a timestamp.
    """
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    formatted_error = f"[{timestamp}] - {error_type}: {message}\n"

    ERROR_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(ERROR_LOG_PATH, "a") as log_file:
            log_file.write(formatted_error)
    except OSError as e:
        # If logging fails, print to console
        print(f"Failed to log error: {e}")

def sanitize_file_name(file_name: str) -> str:
    """
    Sanitizes the file name by replacing invalid characters with an underscore.
    """
    return re.sub(r'[<>:"/\\|?*\r\n]+', '_', file_name)

def list_saved_prompts() -> list:
    """
    Lists all saved prompts in the prompts directory.
    """
    try:
        PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
        prompts = [f.stem for f in PROMPTS_DIR.glob('*.txt')]
        return prompts
    except OSError as e:
        handle_error("ProcessingError", f"Failed to list saved prompts: {e}")
        return []

def load_prompt(name: str = "Default Prompt") -> str:
    """
    Loads a prompt by name.
    """
    try:
        PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
        file_path = PROMPTS_DIR / f"{sanitize_file_name(name)}.txt"
        with file_path.open('r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        handle_error("FileNotFound", f"Prompt '{name}' not found.")
        return ""
    except OSError as e:
        handle_error("ProcessingError", f"Failed to load prompt '{name}': {e}")
        return ""

def save_prompt(name: str, content: str):
    """
    Saves a prompt with the given name and content.
    """
    try:
        PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
        file_path = PROMPTS_DIR / f"{sanitize_file_name(name)}.txt"
        with file_path.open('w', encoding='utf-8') as file:
            file.write(content)
    except OSError as e:
        if e.errno == errno.ENOSPC:
            handle_error("StorageError", "No space left on device. Unable to save the prompt.")
        else:
            handle_error("ProcessingError", f"Failed to save prompt '{name}': {e}")

def delete_prompt(name: str):
    """
    Deletes a prompt by name.
    """
    try:
        file_path = PROMPTS_DIR / f"{sanitize_file_name(name)}.txt"
        if file_path.exists():
            file_path.unlink()
        else:
            handle_error("FileNotFound", f"Prompt '{name}' does not exist.")
    except OSError as e:
        handle_error("ProcessingError", f"Failed to delete prompt '{name}': {e}")

def clear_error_logs():
    """
    Clears the error logs by overwriting the log file with empty content.
    """
    try:
        if ERROR_LOG_PATH.exists():
            with ERROR_LOG_PATH.open("w") as log_file:
                log_file.write("")
    except OSError as e:
        handle_error("ProcessingError", f"Failed to clear error logs: {e}")

def rotate_logs(max_size: int = 10*1024*1024):
    """
    Rotates the log file if it exceeds max_size.
    """
    if ERROR_LOG_PATH.exists() and ERROR_LOG_PATH.stat().st_size > max_size:
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        archived_log = BASE_DIR / f"logs/error_log_{timestamp}.bak"
        try:
            shutil.move(str(ERROR_LOG_PATH), str(archived_log))
            # Create a new empty log file
            with ERROR_LOG_PATH.open("w") as log_file:
                log_file.write("")
        except OSError as e:
            handle_error("ProcessingError", f"Failed to rotate logs: {e}")

def list_errors() -> list:
    """
    Retrieves the list of error logs.
    """
    try:
        if not ERROR_LOG_PATH.exists():
            return []
        with ERROR_LOG_PATH.open("r", encoding='utf-8') as log_file:
            return log_file.readlines()
    except OSError as e:
        handle_error("ProcessingError", f"Failed to read error logs: {e}")
        return []

def clear_cache():
    """
    Placeholder for cache clearing logic.
    """
    # Implement cache clearing logic if necessary
    pass

def save_uploaded_file(filename: str, content: str):
    """
    Saves an uploaded file to the storage directory.
    """
    try:
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        file_path = UPLOAD_DIR / sanitize_file_name(filename)
        with file_path.open('w', encoding='utf-8') as file:
            file.write(content)
    except OSError as e:
        handle_error("ProcessingError", f"Failed to save uploaded file '{filename}': {e}")

def get_uploaded_files() -> list:
    """
    Lists all uploaded files.
    """
    try:
        if not UPLOAD_DIR.exists():
            return []
        return [f.name for f in UPLOAD_DIR.iterdir() if f.is_file()]
    except OSError as e:
        handle_error("ProcessingError", f"Failed to list uploaded files: {e}")
        return []

def load_uploaded_file_content(filename: str) -> str:
    """
    Loads the content of an uploaded file.
    """
    try:
        file_path = UPLOAD_DIR / sanitize_file_name(filename)
        print(f"Attempting to load file: {file_path}")  # Debug log
        with file_path.open('r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        handle_error("FileNotFound", f"Uploaded file '{filename}' not found.")
        return ""
    except OSError as e:
        handle_error("ProcessingError", f"Failed to load uploaded file '{filename}': {e}")
        return ""

def update_file_content(filename: str, new_content: str):
    """
    Updates the content of an uploaded file.
    """
    try:
        file_path = UPLOAD_DIR / sanitize_file_name(filename)
        if not file_path.exists():
            handle_error("FileNotFound", f"Uploaded file '{filename}' does not exist.")
            return
        with file_path.open('w', encoding='utf-8') as file:
            file.write(new_content)
    except OSError as e:
        handle_error("ProcessingError", f"Failed to update uploaded file '{filename}': {e}")

def delete_all_files():
    """
    Deletes all uploaded and processed files.
    """
    try:
        if UPLOAD_DIR.exists():
            shutil.rmtree(UPLOAD_DIR)
        if PROCESSED_DIR.exists():
            shutil.rmtree(PROCESSED_DIR)
    except OSError as e:
        handle_error("ProcessingError", f"Failed to delete all files: {e}")

def save_processed_result(filename: str, content: str):
    """
    Saves the processed result of a file.
    """
    try:
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        file_path = PROCESSED_DIR / sanitize_file_name(filename)
        with file_path.open('w', encoding='utf-8') as file:
            file.write(content)
    except OSError as e:
        handle_error("ProcessingError", f"Failed to save processed result for '{filename}': {e}")

def get_processed_results() -> dict:
    """
    Retrieves all processed results.
    """
    results = {}
    try:
        if not PROCESSED_DIR.exists():
            return results
        for file in PROCESSED_DIR.iterdir():
            if file.is_file():
                with file.open('r', encoding='utf-8') as f:
                    results[file.name] = f.read()
    except OSError as e:
        handle_error("ProcessingError", f"Failed to retrieve processed results: {e}")
    return results
