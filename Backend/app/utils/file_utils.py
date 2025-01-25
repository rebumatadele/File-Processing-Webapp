# app/utils/file_utils.py

from datetime import datetime
import re
from typing import Optional, List, Dict, Any, Union
import os

from sqlalchemy.orm import Session
from app.models.prompt import Prompt
from app.models.file import UploadedFile, ProcessedFile
from app.utils.error_utils import handle_error
from app.utils.cache_utils import get_cached_result, set_cached_result

def sanitize_file_name(file_name: str) -> str:
    """
    Sanitizes the file name by replacing invalid characters with underscores.
    """
    return re.sub(r'[<>:"/\\|?*\r\n]+', '_', file_name)

def save_uploaded_file(
    session: Session,
    filename: str,
    content: str,
    user_id: str
):
    """
    Saves an uploaded file in the DB (UploadedFile table).
    """
    try:
        sanitized = sanitize_file_name(filename)
        new_file = UploadedFile(
            user_id=user_id,
            filename=sanitized,
            content=content
        )
        session.add(new_file)
        session.commit()
    except Exception as e:
        handle_error("ProcessingError", f"Failed to save uploaded file '{filename}': {e}", user_id=user_id)
        session.rollback()

def get_uploaded_files(session: Session, user_id: str) -> List[str]:
    """
    Returns a list of all uploaded file names from the DB for this user.
    """
    try:
        files = session.query(UploadedFile).filter_by(user_id=user_id).all()
        return [f.filename for f in files]
    except Exception as e:
        handle_error("ProcessingError", f"Failed to list uploaded files: {e}", user_id=user_id)
        return []

def load_uploaded_file_content(session: Session, filename: str, user_id: str) -> str:
    """
    Loads the content of an uploaded file from the DB.
    """
    try:
        sanitized = sanitize_file_name(filename)
        file_record = session.query(UploadedFile).filter_by(
            user_id=user_id,
            filename=sanitized
        ).first()
        if file_record:
            return file_record.content
        else:
            handle_error("FileNotFound", f"Uploaded file '{filename}' not found in DB.", user_id=user_id)
            return ""
    except Exception as e:
        handle_error("ProcessingError", f"Failed to load uploaded file '{filename}': {e}", user_id=user_id)
        return ""

def update_file_content(
    session: Session,
    filename: str,
    new_content: str,
    user_id: str
):
    """
    Updates the content of an uploaded file in the DB.
    """
    try:
        sanitized = sanitize_file_name(filename)
        file_record = session.query(UploadedFile).filter_by(
            user_id=user_id,
            filename=sanitized
        ).first()
        if not file_record:
            handle_error("FileNotFound", f"Uploaded file '{filename}' does not exist in DB.", user_id=user_id)
            return
        file_record.content = new_content
        session.commit()
    except Exception as e:
        handle_error("ProcessingError", f"Failed to update file '{filename}': {e}", user_id=user_id)
        session.rollback()

def delete_all_files(session: Session, user_id: str):
    """
    Deletes all 'UploadedFile' and 'ProcessedFile' rows for the user from the DB.
    """
    try:
        session.query(UploadedFile).filter_by(user_id=user_id).delete()
        session.query(ProcessedFile).filter_by(user_id=user_id).delete()
        session.commit()
    except Exception as e:
        handle_error("ProcessingError", f"Failed to delete all files for user {user_id}: {e}", user_id=user_id)
        session.rollback()

def save_processed_result(
    session: Session,
    filename: str,
    content: str,
    uploaded_file_id: str
) -> str:
    """
    Saves a processed result into the DB (ProcessedFile table) and returns the path to the temporary file.
    """
    try:
        sanitized = sanitize_file_name(filename)
        new_processed = ProcessedFile(
            uploaded_file_id=uploaded_file_id,
            filename=sanitized,
            content=content,
            processed_at=datetime.utcnow()
        )
        session.add(new_processed)
        session.commit()
        print(f"[DB] Successfully saved processed file: {filename}")

        # Save the processed content to a temporary file for attachment
        tmp_dir = "tmp_processed_files"
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_file_path = os.path.join(tmp_dir, f"{sanitized}_processed.txt")
        with open(tmp_file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[FileUtils] Processed file saved at {tmp_file_path}")

        return tmp_file_path  # Return the path for attachment

    except Exception as e:
        handle_error("ProcessingError", f"Failed to save processed result for '{filename}': {e}", user_id=None)
        print(f"[DB] Exception while saving processed file '{filename}': {e}")
        session.rollback()
        raise  # Re-raise the exception to handle it upstream

def get_processed_results(session: Session, user_id: str) -> Dict[str, str]:
    """
    Retrieves all processed results from the DB for the user, returning a dict {filename: content}.
    """
    results = {}
    try:
        # If `ProcessedFile` doesn't store user_id directly, we can join on `UploadedFile`
        processed = (
            session.query(ProcessedFile)
            .join(UploadedFile, ProcessedFile.uploaded_file_id == UploadedFile.id)
            .filter(UploadedFile.user_id == user_id)
            .all()
        )
        for p in processed:
            results[p.filename] = p.content
    except Exception as e:
        handle_error("ProcessingError", f"Failed to retrieve processed results: {e}", user_id=user_id)
    return results

def get_uploaded_files_size(session: Session, user_id: str) -> int:
    """
    Calculates the total byte size of all uploaded files for the user.
    """
    try:
        files = session.query(UploadedFile).filter_by(user_id=user_id).all()
        return sum(len(f.content.encode('utf-8')) for f in files)
    except Exception as e:
        handle_error("ProcessingError", f"Failed to calculate uploaded files size: {e}", user_id=user_id)
        return 0

def get_processed_files_size(session: Session, user_id: str) -> int:
    """
    Calculates the total byte size of all processed files for the user.
    """
    try:
        processed = (
            session.query(ProcessedFile)
            .join(UploadedFile, ProcessedFile.uploaded_file_id == UploadedFile.id)
            .filter(UploadedFile.user_id == user_id)
            .all()
        )
        return sum(len(p.content.encode('utf-8')) for p in processed)
    except Exception as e:
        handle_error("ProcessingError", f"Failed to calculate processed files size: {e}", user_id=user_id)
        return 0

# =========================
#  Prompt-Related Functions
#  (DB-based, no caching)
# =========================

def list_saved_prompts(
    session: Session,
    user_id: str,
    search: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> List[str]:
    """
    Lists all saved prompts for the user, optionally filtering by search term and tags.
    """
    try:
        query = session.query(Prompt).filter(Prompt.user_id == user_id)

        if search:
            query = query.filter(Prompt.name.ilike(f"%{search}%"))

        if tags:
            # Prompt.tags is typically comma-separated in your schema
            for tag in tags:
                query = query.filter(Prompt.tags.ilike(f"%{tag}%"))

        prompts = query.all()
        return [p.name for p in prompts]
    except Exception as e:
        handle_error("ProcessingError", f"Failed to list saved prompts: {e}", user_id=user_id)
        return []

def load_prompt(session: Session, name: str, user_id: str) -> Optional[str]:
    """
    Loads a prompt's content by name for the user.
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

def save_prompt(
    session: Session,
    name: str,
    content: str,
    user_id: str,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None
):
    """
    Saves (creates or updates) a prompt record in the DB.
    """
    try:
        prompt = session.query(Prompt).filter_by(user_id=user_id, name=name).first()

        if prompt:
            # Update existing
            prompt.content = content
            if description is not None:
                prompt.description = description
            if tags is not None:
                prompt.tags = ",".join(tags)
            prompt.updated_at = datetime.utcnow()
        else:
            # Create new
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
    Deletes a prompt from the DB.
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