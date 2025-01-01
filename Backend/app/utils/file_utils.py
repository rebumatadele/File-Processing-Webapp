# app/utils/file_utils.py

from datetime import datetime
import hashlib
import os
import time
import shutil
import errno
import re
from pathlib import Path
import json
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.prompt import Prompt
from app.config.database import SessionLocal  # This import can be removed if sessions are injected
# Define paths using pathlib for better path handling
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Adjust as per directory structure
ERROR_LOG_PATH = BASE_DIR / "logs" / "error_log.txt"
# Removed PROMPTS_DIR as prompts are now handled via the database
UPLOAD_DIR = BASE_DIR / "storage" / "uploads"
PROCESSED_DIR = BASE_DIR / "storage" / "processed"

CONFIG_DIR = BASE_DIR / "config"
USER_CONFIG_FILE = CONFIG_DIR / "user_configs.json"

CACHE_DIR = BASE_DIR / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def get_user_upload_dir(user_id: str) -> Path:
    return BASE_DIR / "storage" / "uploads" / user_id

def get_user_processed_dir(user_id: str) -> Path:
    return BASE_DIR / "storage" / "processed" / user_id

def get_user_cache_dir(user_id: str) -> Path:
    return CACHE_DIR / user_id

def get_user_error_log_path(user_id: str) -> Path:
    return BASE_DIR / "logs" / f"{user_id}_error_log.txt"

def handle_error(error_type: str, message: str, user_id: Optional[str] = None):
    """
    Logs errors to a file with a timestamp. If user_id is provided, logs are stored per user.
    """
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    formatted_error = f"[{timestamp}] - {error_type}: {message}\n"

    if user_id:
        error_log_path = get_user_error_log_path(user_id)
    else:
        error_log_path = BASE_DIR / "logs" / "error_log.txt"

    error_log_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(error_log_path, "a") as log_file:
            log_file.write(formatted_error)
    except OSError as e:
        # If logging fails, print to console
        print(f"Failed to log error: {e}")

def sanitize_file_name(file_name: str) -> str:
    """
    Sanitizes the file name by replacing invalid characters with an underscore.
    """
    return re.sub(r'[<>:"/\\|?*\r\n]+', '_', file_name)

# ======== Database-Based Prompt Functions ========

def list_saved_prompts(session: Session, user_id: str, search: Optional[str] = None, tags: Optional[List[str]] = None) -> List[str]:
    """
    Lists all saved prompts for the user, optionally filtering by search term and tags.
    """
    try:
        query = session.query(Prompt).filter(Prompt.user_id == user_id)

        if search:
            query = query.filter(Prompt.name.ilike(f"%{search}%"))

        if tags:
            for tag in tags:
                query = query.filter(Prompt.tags.ilike(f"%{tag}%"))

        prompts = query.all()
        return [prompt.name for prompt in prompts]
    except Exception as e:
        handle_error("ProcessingError", f"Failed to list saved prompts: {e}", user_id=user_id)
        return []

def load_prompt(session: Session, name: str, user_id: str) -> Optional[str]:
    """
    Loads a prompt by name for the user.
    """
    try:
        prompt = session.query(Prompt).filter_by(user_id=user_id, name=name).first()
        if prompt:
            return prompt.content
        else:
            handle_error("FileNotFound", f"Prompt '{name}' not found.", user_id=user_id)
            return None
    except Exception as e:
        handle_error("ProcessingError", f"Failed to load prompt '{name}': {e}", user_id=user_id)
        return None

def save_prompt(session: Session, name: str, content: str, user_id: str, description: Optional[str] = None, tags: Optional[List[str]] = None):
    """
    Saves a prompt with the given name and content for the user.
    If the prompt exists, it updates the existing prompt.
    """
    try:
        prompt = session.query(Prompt).filter_by(user_id=user_id, name=name).first()

        if prompt:
            # Update existing prompt
            prompt.content = content
            prompt.description = description if description is not None else prompt.description
            prompt.tags = ",".join(tags) if tags else prompt.tags
            prompt.updated_at = datetime.utcnow()
        else:
            # Create new prompt
            new_prompt = Prompt(
                user_id=user_id,
                name=name,
                content=content,
                description=description,
                tags=",".join(tags) if tags else None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(new_prompt)

        session.commit()
    except Exception as e:
        handle_error("ProcessingError", f"Failed to save prompt '{name}': {e}", user_id=user_id)
        session.rollback()

def delete_prompt(session: Session, name: str, user_id: str):
    """
    Deletes a prompt by name for the user.
    """
    try:
        prompt = session.query(Prompt).filter_by(user_id=user_id, name=name).first()
        if prompt:
            session.delete(prompt)
            session.commit()
        else:
            handle_error("FileNotFound", f"Prompt '{name}' does not exist.", user_id=user_id)
    except Exception as e:
        handle_error("ProcessingError", f"Failed to delete prompt '{name}': {e}", user_id=user_id)
        session.rollback()

# ======== Other File-Based Functionalities ========

def clear_error_logs(user_id: str):
    """
    Clears the error logs for the user.
    """
    try:
        error_log_path = get_user_error_log_path(user_id)
        if error_log_path.exists():
            with error_log_path.open("w") as log_file:
                log_file.write("")
    except OSError as e:
        handle_error("ProcessingError", f"Failed to clear error logs: {e}", user_id=user_id)

def list_errors(user_id: str) -> list:
    """
    Retrieves the list of error logs for the user.
    """
    try:
        error_log_path = get_user_error_log_path(user_id)
        if not error_log_path.exists():
            return []
        with error_log_path.open("r", encoding='utf-8') as log_file:
            return log_file.readlines()
    except OSError as e:
        handle_error("ProcessingError", f"Failed to read error logs: {e}", user_id=user_id)
        return []

def clear_cache(user_id: str):
    """
    Clears the application cache for the user.
    """
    try:
        user_cache_dir = get_user_cache_dir(user_id)
        if user_cache_dir.exists():
            shutil.rmtree(user_cache_dir)
            user_cache_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        handle_error("ProcessingError", f"Failed to clear cache: {e}", user_id=user_id)

def save_uploaded_file(filename: str, content: str, user_id: str):
    """
    Saves an uploaded file to the user's storage directory.
    """
    try:
        user_upload_dir = get_user_upload_dir(user_id)
        user_upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = user_upload_dir / sanitize_file_name(filename)
        with file_path.open('w', encoding='utf-8') as file:
            file.write(content)
    except OSError as e:
        handle_error("ProcessingError", f"Failed to save uploaded file '{filename}': {e}", user_id=user_id)

def get_uploaded_files(user_id: str) -> list:
    """
    Lists all uploaded files for the user.
    """
    try:
        user_upload_dir = get_user_upload_dir(user_id)
        if not user_upload_dir.exists():
            return []
        return [f.name for f in user_upload_dir.iterdir() if f.is_file()]
    except OSError as e:
        handle_error("ProcessingError", f"Failed to list uploaded files: {e}", user_id=user_id)
        return []

def load_uploaded_file_content(filename: str, user_id: str) -> str:
    """
    Loads the content of an uploaded file for the user.
    """
    try:
        user_upload_dir = get_user_upload_dir(user_id)
        file_path = user_upload_dir / sanitize_file_name(filename)
        with file_path.open('r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        handle_error("FileNotFound", f"Uploaded file '{filename}' not found.", user_id=user_id)
        return ""
    except OSError as e:
        handle_error("ProcessingError", f"Failed to load uploaded file '{filename}': {e}", user_id=user_id)
        return ""

def update_file_content(filename: str, new_content: str, user_id: str):
    """
    Updates the content of an uploaded file for the user.
    """
    try:
        user_upload_dir = get_user_upload_dir(user_id)
        file_path = user_upload_dir / sanitize_file_name(filename)
        if not file_path.exists():
            handle_error("FileNotFound", f"Uploaded file '{filename}' does not exist.", user_id=user_id)
            return
        with file_path.open('w', encoding='utf-8') as file:
            file.write(new_content)
    except OSError as e:
        handle_error("ProcessingError", f"Failed to update uploaded file '{filename}': {e}", user_id=user_id)

def delete_all_files(user_id: str):
    """
    Deletes all uploaded and processed files for the user.
    """
    try:
        user_upload_dir = get_user_upload_dir(user_id)
        user_processed_dir = get_user_processed_dir(user_id)
        if user_upload_dir.exists():
            shutil.rmtree(user_upload_dir)
        if user_processed_dir.exists():
            shutil.rmtree(user_processed_dir)
    except OSError as e:
        handle_error("ProcessingError", f"Failed to delete all files: {e}", user_id=user_id)

def save_processed_result(filename: str, content: str, user_id: str):
    """
    Saves the processed result of a file for the user.
    """
    try:
        user_processed_dir = get_user_processed_dir(user_id)
        user_processed_dir.mkdir(parents=True, exist_ok=True)
        file_path = user_processed_dir / sanitize_file_name(filename)
        with file_path.open('w', encoding='utf-8') as file:
            file.write(content)
    except OSError as e:
        handle_error("ProcessingError", f"Failed to save processed result for '{filename}': {e}", user_id=user_id)

def get_processed_results(user_id: str) -> dict:
    """
    Retrieves all processed results for the user.
    """
    results = {}
    try:
        user_processed_dir = get_user_processed_dir(user_id)
        if not user_processed_dir.exists():
            return results
        for file in user_processed_dir.iterdir():
            if file.is_file():
                with file.open('r', encoding='utf-8') as f:
                    results[file.name] = f.read()
    except OSError as e:
        handle_error("ProcessingError", f"Failed to retrieve processed results: {e}", user_id=user_id)
    return results

def get_uploaded_files_size(user_id: str) -> int:
    """
    Calculates the total size of all uploaded files in bytes for the user.
    """
    total_size = 0
    try:
        user_upload_dir = get_user_upload_dir(user_id)
        if not user_upload_dir.exists():
            return total_size
        for file in user_upload_dir.iterdir():
            if file.is_file():
                total_size += file.stat().st_size
    except OSError as e:
        handle_error("ProcessingError", f"Failed to calculate uploaded files size: {e}", user_id=user_id)
    return total_size

def get_processed_files_size(user_id: str) -> int:
    """
    Calculates the total size of all processed files in bytes for the user.
    """
    total_size = 0
    try:
        user_processed_dir = get_user_processed_dir(user_id)
        if not user_processed_dir.exists():
            return total_size
        for file in user_processed_dir.iterdir():
            if file.is_file():
                total_size += file.stat().st_size
    except OSError as e:
        handle_error("ProcessingError", f"Failed to calculate processed files size: {e}", user_id=user_id)
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
        handle_error("ProcessingError", f"Failed to save user config for {user_id}: {e}", user_id=user_id)

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
        handle_error("ProcessingError", f"Failed to retrieve user config for {user_id}: {e}", user_id=user_id)
        return None

# ======== Cache-Related Functions ========

def generate_cache_key(chunk: str, provider_choice: str, model_choice: Optional[str], user_id: str) -> str:
    """
    Generates a SHA256 hash key based on the chunk content, configuration, and user_id.
    """
    key_string = f"{user_id}:{provider_choice}:{model_choice}:{chunk}"
    return hashlib.sha256(key_string.encode('utf-8')).hexdigest()

def get_cache_file_path(cache_key: str, user_id: str) -> Path:
    """
    Returns the file path for a given cache key for the user.
    """
    user_cache_dir = get_user_cache_dir(user_id)
    user_cache_dir.mkdir(parents=True, exist_ok=True)
    return user_cache_dir / f"{cache_key}.json"

def get_cached_result(chunk: str, provider_choice: str, model_choice: Optional[str], user_id: str) -> Optional[str]:
    """
    Retrieves the cached result for a given chunk and configuration for the user.
    Returns None if not found.
    """
    cache_key = generate_cache_key(chunk, provider_choice, model_choice, user_id)
    cache_file = get_cache_file_path(cache_key, user_id)
    if cache_file.exists():
        try:
            with cache_file.open('r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("result")
        except (OSError, json.JSONDecodeError) as e:
            handle_error("CacheError", f"Failed to read cache file {cache_file}: {e}", user_id=user_id)
            return None
    return None

def set_cached_result(chunk: str, provider_choice: str, model_choice: Optional[str], result: str, user_id: str):
    """
    Caches the result for a given chunk and configuration for the user.
    """
    cache_key = generate_cache_key(chunk, provider_choice, model_choice, user_id)
    cache_file = get_cache_file_path(cache_key, user_id)
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
        handle_error("CacheError", f"Failed to write cache file {cache_file}: {e}", user_id=user_id)

def get_cache_size(user_id: str) -> int:
    """
    Calculates the total size of the cache in bytes for the user.
    """
    total_size = 0
    try:
        user_cache_dir = get_user_cache_dir(user_id)
        if not user_cache_dir.exists():
            return total_size
        for dirpath, dirnames, filenames in os.walk(user_cache_dir):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.isfile(fp):
                    total_size += os.path.getsize(fp)
    except OSError as e:
        handle_error("ProcessingError", f"Failed to calculate cache size: {e}", user_id=user_id)
    return total_size

def list_cache_contents(user_id: str) -> list:
    """
    Lists all files in the cache directory for the user.
    """
    try:
        user_cache_dir = get_user_cache_dir(user_id)
        if not user_cache_dir.exists():
            return []
        return [f.name for f in user_cache_dir.iterdir() if f.is_file()]
    except OSError as e:
        handle_error("ProcessingError", f"Failed to list cache contents: {e}", user_id=user_id)
        return []
