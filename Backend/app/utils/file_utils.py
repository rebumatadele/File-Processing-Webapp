# app/utils/file_utils.py

import hashlib
import os
import time
import shutil
import errno
import re
from pathlib import Path
import json
from typing import Optional

# Define paths using pathlib for better path handling
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Adjust as per directory structure
ERROR_LOG_PATH = BASE_DIR / "logs" / "error_log.txt"
PROMPTS_DIR = BASE_DIR / "prompts"
UPLOAD_DIR = BASE_DIR / "storage" / "uploads"
PROCESSED_DIR = BASE_DIR / "storage" / "processed"

CONFIG_DIR = BASE_DIR / "config"
USER_CONFIG_FILE = CONFIG_DIR / "user_configs.json"

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Adjust as per directory structure
CACHE_DIR = BASE_DIR / "cache"

# Ensuring CACHE_DIR exists
CACHE_DIR.mkdir(parents=True, exist_ok=True)

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
    Clears the application cache by deleting all files in the cache directory.
    """
    try:
        if CACHE_DIR.exists():
            shutil.rmtree(CACHE_DIR)
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        handle_error("ProcessingError", f"Failed to clear cache: {e}")

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

def get_uploaded_files_size() -> int:
    """
    Calculates the total size of all uploaded files in bytes.
    """
    total_size = 0
    try:
        if not UPLOAD_DIR.exists():
            return total_size
        for file in UPLOAD_DIR.iterdir():
            if file.is_file():
                total_size += file.stat().st_size
    except OSError as e:
        handle_error("ProcessingError", f"Failed to calculate uploaded files size: {e}")
    return total_size

def get_processed_files_size() -> int:
    """
    Calculates the total size of all processed files in bytes.
    """
    total_size = 0
    try:
        if not PROCESSED_DIR.exists():
            return total_size
        for file in PROCESSED_DIR.iterdir():
            if file.is_file():
                total_size += file.stat().st_size
    except OSError as e:
        handle_error("ProcessingError", f"Failed to calculate processed files size: {e}")
    return total_size

def save_user_config(user_id: str, config: dict):
    """
    Saves the user configuration to a JSON file.
    """
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        if USER_CONFIG_FILE.exists():
            with USER_CONFIG_FILE.open('r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {}
        data[user_id] = config
        with USER_CONFIG_FILE.open('w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except OSError as e:
        handle_error("ProcessingError", f"Failed to save user config for {user_id}: {e}")

def get_user_config(user_id: str) -> Optional[dict]:
    """
    Retrieves the user configuration from the JSON file.
    """
    try:
        if not USER_CONFIG_FILE.exists():
            return None
        with USER_CONFIG_FILE.open('r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get(user_id)
    except OSError as e:
        handle_error("ProcessingError", f"Failed to retrieve user config for {user_id}: {e}")
        return None
    
    

# Cache-related functions

def generate_cache_key(chunk: str, provider_choice: str, model_choice: Optional[str] = None) -> str:
    """
    Generates a SHA256 hash key based on the chunk content and configuration.
    """
    key_string = f"{provider_choice}:{model_choice}:{chunk}"
    return hashlib.sha256(key_string.encode('utf-8')).hexdigest()

def get_cache_file_path(cache_key: str) -> Path:
    """
    Returns the file path for a given cache key.
    """
    return CACHE_DIR / f"{cache_key}.json"

def get_cached_result(chunk: str, provider_choice: str, model_choice: Optional[str] = None) -> Optional[str]:
    """
    Retrieves the cached result for a given chunk and configuration.
    Returns None if not found.
    """
    cache_key = generate_cache_key(chunk, provider_choice, model_choice)
    cache_file = get_cache_file_path(cache_key)
    if cache_file.exists():
        try:
            with cache_file.open('r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("result")
        except (OSError, json.JSONDecodeError) as e:
            handle_error("CacheError", f"Failed to read cache file {cache_file}: {e}")
            return None
    return None

def set_cached_result(chunk: str, provider_choice: str, model_choice: Optional[str], result: str):
    """
    Caches the result for a given chunk and configuration.
    """
    cache_key = generate_cache_key(chunk, provider_choice, model_choice)
    cache_file = get_cache_file_path(cache_key)
    data = {
        "chunk": chunk,
        "provider_choice": provider_choice,
        "model_choice": model_choice,
        "result": result,
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
    }
    try:
        with cache_file.open('w', encoding='utf-8') as f:
            json.dump(data, f)
    except OSError as e:
        handle_error("CacheError", f"Failed to write cache file {cache_file}: {e}")

def get_cache_size() -> int:
    """
    Calculates the total size of the cache in bytes.
    """
    total_size = 0
    try:
        if not CACHE_DIR.exists():
            return total_size
        for dirpath, dirnames, filenames in os.walk(CACHE_DIR):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.isfile(fp):
                    total_size += os.path.getsize(fp)
    except OSError as e:
        handle_error("ProcessingError", f"Failed to calculate cache size: {e}")
    return total_size

def list_cache_contents() -> list:
    """
    Lists all files in the cache directory.
    """
    try:
        if not CACHE_DIR.exists():
            return []
        return [f.name for f in CACHE_DIR.iterdir() if f.is_file()]
    except OSError as e:
        handle_error("ProcessingError", f"Failed to list cache contents: {e}")
        return []