# app/utils/file_utils.py

from datetime import datetime
import re
from typing import Optional, List, Dict, Any, Union
import os
from typing import Optional, List, Dict
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.prompt import Prompt
from app.models.file import UploadedFile, ProcessedFile
from app.utils.error_utils import handle_error
from app.utils.encryption_utils import xor_bytes, base64_to_bytes, bytes_to_base64

def sanitize_file_name(file_name: str) -> str:
    """
    Sanitizes the file name by replacing invalid characters with underscores.
    """
    return re.sub(r'[<>:"/\\|?*\r\n]+', '_', file_name)

def save_uploaded_file(
    session: Session,
    filename: str,
    encrypted_data_b64: str,
    encryption_key_b64: str,
    user_id: str
):
    """
    Saves an XOR-encrypted file (both data + key in base64) to the DB.
    """
    try:
        sanitized = sanitize_file_name(filename)

        new_file = UploadedFile(
            user_id=user_id,
            filename=sanitized,
            encrypted_content=encrypted_data_b64,  # store as-is
            encryption_key=encryption_key_b64
        )
        session.add(new_file)
        session.commit()

    except Exception as e:
        handle_error("ProcessingError", f"Failed to save uploaded file '{filename}': {e}", user_id=user_id)
        session.rollback()
        raise

def get_uploaded_files(session: Session, user_id: str) -> List[str]:
    try:
        files = session.query(UploadedFile).filter_by(user_id=user_id).all()
        return [f.filename for f in files]
    except Exception as e:
        handle_error("ProcessingError", f"Failed to list uploaded files: {e}", user_id=user_id)
        return []

def load_uploaded_file_content(session: Session, filename: str, user_id: str) -> str:
    """
    Returns the **decrypted** plaintext content of the file.
    """
    try:
        sanitized = sanitize_file_name(filename)
        file_record = session.query(UploadedFile).filter_by(
            user_id=user_id,
            filename=sanitized
        ).first()

        if not file_record:
            handle_error("FileNotFound", f"Uploaded file '{filename}' not found in DB.", user_id=user_id)
            return ""

        # 1) decode from base64
        encrypted_bytes = base64_to_bytes(file_record.encrypted_content)
        key_bytes = base64_to_bytes(file_record.encryption_key)

        # 2) XOR to get plaintext
        plaintext_bytes = xor_bytes(encrypted_bytes, key_bytes)
        return plaintext_bytes.decode("utf-8", errors="replace")

    except Exception as e:
        handle_error("ProcessingError", f"Failed to load uploaded file '{filename}': {e}", user_id=user_id)
        return ""

def update_file_content_with_new_key(
    session: Session,
    filename: str,
    new_encrypted_content_b64: str,
    new_encryption_key_b64: str,
    user_id: str
):
    """
    Updates both the encrypted content and encryption key of a file in the database.
    """
    try:
        sanitized = sanitize_file_name(filename)
        file_record = session.query(UploadedFile).filter_by(
            user_id=user_id,
            filename=sanitized
        ).first()

        if not file_record:
            handle_error("FileNotFound", f"Uploaded file '{filename}' not found in DB.", user_id=user_id)
            raise HTTPException(status_code=404, detail=f"File '{filename}' not found.")

        # Update the record with the new encrypted content and new key
        file_record.encrypted_content = new_encrypted_content_b64
        file_record.encryption_key = new_encryption_key_b64

        session.commit()

    except HTTPException:
        raise
    except Exception as e:
        handle_error("ProcessingError", f"Failed to update file '{filename}': {e}", user_id=user_id)
        session.rollback()
        raise

def delete_all_files(session: Session, user_id: str):
    """
    Deletes all 'UploadedFile' and 'ProcessedFile' rows for the user from the DB.
    Utilizes ORM methods to respect cascade deletes.
    """
    try:
        # Retrieve all UploadedFile records for the user
        uploaded_files = session.query(UploadedFile).filter_by(user_id=user_id).all()
        
        # Delete each UploadedFile; associated ProcessedFiles will be deleted via cascade
        for file in uploaded_files:
            session.delete(file)
        
        session.commit()
    except Exception as e:
        handle_error("ProcessingError", f"Failed to delete all files for user {user_id}: {e}", user_id=user_id)
        session.rollback()
def delete_specific_file(session: Session, filename: str, user_id: str):
    """
    Deletes a specific uploaded file and its associated processed files.
    """
    try:
        # Sanitize the filename to prevent SQL injection or other issues
        sanitized = sanitize_file_name(filename)
        
        # Retrieve the specific UploadedFile record
        file_record = session.query(UploadedFile).filter_by(
            user_id=user_id,
            filename=sanitized
        ).first()
        
        if not file_record:
            # If the file does not exist, raise a 404 error
            handle_error("FileNotFound", f"Uploaded file '{filename}' not found in DB.", user_id=user_id)
            raise HTTPException(status_code=404, detail=f"File '{filename}' not found.")
        
        # Delete the UploadedFile; associated ProcessedFiles will be deleted via cascade
        session.delete(file_record)
        session.commit()
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions to be handled by the router
    except Exception as e:
        handle_error("ProcessingError", f"Failed to delete file '{filename}': {e}", user_id=user_id)
        session.rollback()
        raise

def save_processed_result(
    session: Session,
    filename: str,
    plaintext_processed: str,
    uploaded_file_id: str,
    reuse_key_b64: str
) -> str:
    """
    Saves the processed result in XOR-encrypted form using the same (or a new) key.
    For simplicity, let's re-use the same key from the original file.
    """
    from app.utils.encryption_utils import xor_bytes, base64_to_bytes, bytes_to_base64

    try:
        sanitized = sanitize_file_name(filename)

        # 1) Convert plaintext + key to bytes
        plain_bytes = plaintext_processed.encode("utf-8")
        key_bytes = base64_to_bytes(reuse_key_b64)
        if len(plain_bytes) != len(key_bytes):
            # If the processed text is a different length, you have to generate a new key.
            # For demonstration, let's do that below if they differ:
            import os
            key_bytes = os.urandom(len(plain_bytes))

        # 2) XOR to encrypt
        enc_bytes = xor_bytes(plain_bytes, key_bytes)

        # 3) Base64
        enc_b64 = bytes_to_base64(enc_bytes)
        key_b64 = bytes_to_base64(key_bytes)

        new_processed = ProcessedFile(
            uploaded_file_id=uploaded_file_id,
            filename=sanitized,
            encrypted_content=enc_b64,
            encryption_key=key_b64,
        )
        session.add(new_processed)
        session.commit()

        # Optionally save a physical text file for reference or emailing:
        tmp_dir = "tmp_processed_files"
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_file_path = os.path.join(tmp_dir, f"{sanitized}_processed.txt")
        with open(tmp_file_path, "w", encoding="utf-8") as f:
            f.write(plaintext_processed)

        return tmp_file_path

    except Exception as e:
        handle_error("ProcessingError", f"Failed to save processed result for '{filename}': {e}", user_id=None)
        session.rollback()
        raise

def get_processed_results(session: Session, user_id: str) -> Dict[str, str]:
    """
    Return {filename: decrypted_content} from ProcessedFile for this user.
    """
    results = {}
    try:
        from app.utils.encryption_utils import xor_bytes, base64_to_bytes

        processed = (
            session.query(ProcessedFile)
            .join(UploadedFile, ProcessedFile.uploaded_file_id == UploadedFile.id)
            .filter(UploadedFile.user_id == user_id)
            .all()
        )
        for p in processed:
            enc_bytes = base64_to_bytes(p.encrypted_content)
            key_bytes = base64_to_bytes(p.encryption_key)
            plain_bytes = xor_bytes(enc_bytes, key_bytes)
            results[p.filename] = plain_bytes.decode("utf-8", errors="replace")
    except Exception as e:
        handle_error("ProcessingError", f"Failed to retrieve processed results: {e}", user_id=user_id)
    return results

def get_uploaded_files_size(session: Session, user_id: str) -> int:
    """
    Sums the size of the *encrypted* data in DB for the user. 
    (If you want the size of the plaintext, you'll need to do a decrypt first.)
    """
    try:
        files = session.query(UploadedFile).filter_by(user_id=user_id).all()
        return sum(len(f.encrypted_content.encode('utf-8')) for f in files)
    except Exception as e:
        handle_error("ProcessingError", f"Failed to calculate uploaded files size: {e}", user_id=user_id)
        return 0

def get_processed_files_size(session: Session, user_id: str) -> int:
    """
    Sums the size of the *encrypted* processed data for the user.
    """
    try:
        processed = (
            session.query(ProcessedFile)
            .join(UploadedFile, ProcessedFile.uploaded_file_id == UploadedFile.id)
            .filter(UploadedFile.user_id == user_id)
            .all()
        )
        return sum(len(p.encrypted_content.encode('utf-8')) for p in processed)
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