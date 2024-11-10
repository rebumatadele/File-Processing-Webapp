# app/utils/file_utils.py

import os
import time
import shutil
import errno
import re

# Define paths
ERROR_LOG_PATH = os.path.join("logs", "error_log.txt")
PROMPTS_DIR = os.path.join("prompts")  # Directory to store prompts
UPLOAD_DIR = os.path.join("storage", "uploads")  # Directory to store uploaded files
PROCESSED_DIR = os.path.join("storage", "processed")  # Directory for processed files

def handle_error(error_type: str, message: str):
    """
    Logs errors to a file with a timestamp.
    """
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    formatted_error = f"[{timestamp}] - {error_type}: {message}\n"

    os.makedirs(os.path.dirname(ERROR_LOG_PATH), exist_ok=True)
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
        os.makedirs(PROMPTS_DIR, exist_ok=True)
        prompts = [f[:-4] for f in os.listdir(PROMPTS_DIR) if f.endswith('.txt')]
        return prompts
    except OSError as e:
        handle_error("ProcessingError", f"Failed to list saved prompts: {e}")
        return []

def load_prompt(name: str = "Default Prompt") -> str:
    """
    Loads a prompt by name.
    """
    try:
        os.makedirs(PROMPTS_DIR, exist_ok=True)
        file_path = os.path.join(PROMPTS_DIR, f"{sanitize_file_name(name)}.txt")
        with open(file_path, 'r', encoding='utf-8') as file:
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
        os.makedirs(PROMPTS_DIR, exist_ok=True)
        file_path = os.path.join(PROMPTS_DIR, f"{sanitize_file_name(name)}.txt")
        with open(file_path, 'w', encoding='utf-8') as file:
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
        file_path = os.path.join(PROMPTS_DIR, f"{sanitize_file_name(name)}.txt")
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            handle_error("FileNotFound", f"Prompt '{name}' does not exist.")
    except OSError as e:
        handle_error("ProcessingError", f"Failed to delete prompt '{name}': {e}")

def clear_error_logs():
    """
    Clears the error logs by overwriting the log file with empty content.
    """
    try:
        if os.path.exists(ERROR_LOG_PATH):
            with open(ERROR_LOG_PATH, "w") as log_file:
                log_file.write("")
    except OSError as e:
        handle_error("ProcessingError", f"Failed to clear error logs: {e}")

def rotate_logs(max_size: int = 10*1024*1024):
    """
    Rotates the log file if it exceeds max_size.
    """
    if os.path.exists(ERROR_LOG_PATH) and os.path.getsize(ERROR_LOG_PATH) > max_size:
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        archived_log = f"{ERROR_LOG_PATH}.{timestamp}.bak"
        try:
            shutil.move(ERROR_LOG_PATH, archived_log)
            # Create a new empty log file
            with open(ERROR_LOG_PATH, "w") as log_file:
                log_file.write("")
        except OSError as e:
            handle_error("ProcessingError", f"Failed to rotate logs: {e}")

def list_errors() -> list:
    """
    Retrieves the list of error logs.
    """
    try:
        if not os.path.exists(ERROR_LOG_PATH):
            return []
        with open(ERROR_LOG_PATH, "r", encoding='utf-8') as log_file:
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
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(UPLOAD_DIR, sanitize_file_name(filename))
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
    except OSError as e:
        handle_error("ProcessingError", f"Failed to save uploaded file '{filename}': {e}")

def get_uploaded_files() -> list:
    """
    Lists all uploaded files.
    """
    try:
        if not os.path.exists(UPLOAD_DIR):
            return []
        return os.listdir(UPLOAD_DIR)
    except OSError as e:
        handle_error("ProcessingError", f"Failed to list uploaded files: {e}")
        return []

def load_uploaded_file_content(filename: str) -> str:
    """
    Loads the content of an uploaded file.
    """
    try:
        file_path = os.path.join(UPLOAD_DIR, sanitize_file_name(filename))
        with open(file_path, 'r', encoding='utf-8') as file:
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
        file_path = os.path.join(UPLOAD_DIR, sanitize_file_name(filename))
        if not os.path.exists(file_path):
            handle_error("FileNotFound", f"Uploaded file '{filename}' does not exist.")
            return
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
    except OSError as e:
        handle_error("ProcessingError", f"Failed to update uploaded file '{filename}': {e}")

def delete_all_files():
    """
    Deletes all uploaded and processed files.
    """
    try:
        if os.path.exists(UPLOAD_DIR):
            shutil.rmtree(UPLOAD_DIR)
        if os.path.exists(PROCESSED_DIR):
            shutil.rmtree(PROCESSED_DIR)
    except OSError as e:
        handle_error("ProcessingError", f"Failed to delete all files: {e}")

def save_processed_result(filename: str, content: str):
    """
    Saves the processed result of a file.
    """
    try:
        os.makedirs(PROCESSED_DIR, exist_ok=True)
        file_path = os.path.join(PROCESSED_DIR, sanitize_file_name(filename))
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
    except OSError as e:
        handle_error("ProcessingError", f"Failed to save processed result for '{filename}': {e}")

def get_processed_results() -> dict:
    """
    Retrieves all processed results.
    """
    results = {}
    try:
        if not os.path.exists(PROCESSED_DIR):
            return results
        for file in os.listdir(PROCESSED_DIR):
            with open(os.path.join(PROCESSED_DIR, file), 'r', encoding='utf-8') as f:
                results[file] = f.read()
    except OSError as e:
        handle_error("ProcessingError", f"Failed to retrieve processed results: {e}")
    return results
