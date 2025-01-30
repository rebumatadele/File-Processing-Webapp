# app/routers/files.py

from fastapi import APIRouter, HTTPException, Path, Depends, Request, Form
from typing import List
from sqlalchemy.orm import Session
from app.models.user import User
from app.providers.auth import get_current_user
from app.dependencies.database import get_db
from app.schemas.file_schemas import EditFileContentRequest, FileContentSchema
from app.utils.error_utils import handle_error
from app.utils.file_utils import (
    delete_specific_file,
    save_uploaded_file,
    get_uploaded_files,
    load_uploaded_file_content,
    update_file_content_with_new_key,
    delete_all_files,
    get_uploaded_files_size,
    get_processed_files_size
)
from fastapi import File, UploadFile

router = APIRouter(
    prefix="/files",
    tags=["File Management"],
    responses={404: {"description": "Not found"}},
)

@router.post("/upload", summary="Upload XOR-Encrypted Files")
async def upload_files(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Expects form data with multiple sets of:
        filename, encrypted_file, file_key
    all as base64 strings (except filename which is plain).
    """
    try:
        form = await request.form()

        # Each field is potentially repeated if multiple files are uploaded
        filenames = form.getlist("filename")
        encrypted_files = form.getlist("encrypted_file")
        file_keys = form.getlist("file_key")

        if len(filenames) != len(encrypted_files) or len(filenames) != len(file_keys):
            raise HTTPException(
                status_code=400,
                detail="Mismatched form data. Make sure 'filename', 'encrypted_file', and 'file_key' have the same length."
            )

        saved_files = []
        for i in range(len(filenames)):
            fname = filenames[i]
            enc_data = encrypted_files[i]
            key_data = file_keys[i]

            # Optionally validate .txt or something else
            # But since it's encrypted, you can’t rely on checking file extension.

            save_uploaded_file(
                session=db,
                filename=fname,
                encrypted_data_b64=enc_data,
                encryption_key_b64=key_data,
                user_id=current_user.id
            )
            saved_files.append(fname)

        return {"message": f"Successfully uploaded files: {', '.join(saved_files)}"}
    except Exception as e:
        handle_error("FileUploadError", f"Failed to upload encrypted files: {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=f"Failed to upload encrypted files: {e}")


@router.get("/", summary="List Uploaded Files", response_model=List[str])
def list_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return get_uploaded_files(db, current_user.id)
    except Exception as e:
        handle_error("ProcessingError", f"Failed to list files: {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=f"Failed to list files: {e}")


@router.get("/{filename}", summary="Get **Decrypted** File Content", response_model=FileContentSchema)
def get_file_content(
    filename: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns the decrypted, plaintext content. We XOR using the stored key.
    """
    try:
        content = load_uploaded_file_content(db, filename, user_id=current_user.id)
        if not content:
            raise HTTPException(status_code=404, detail="File not found or empty.")
        return FileContentSchema(filename=filename, content=content)
    except Exception as e:
        handle_error("ProcessingError", f"Failed to retrieve file: {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve file: {e}")


@router.put("/{filename}", summary="Edit File Content")
def edit_file_content(
    filename: str,
    request: EditFileContentRequest,  # Receive from request body
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Edits the content of a specific uploaded file by updating both the encryption key and encrypted content.
    """
    try:
        # Update the file with the new encrypted content and new key
        update_file_content_with_new_key(db, filename, request.encrypted_file, request.file_key, user_id=current_user.id)
        return {"message": f"File '{filename}' updated successfully (XOR)."}
    except HTTPException as he:
        raise he
    except Exception as e:
        handle_error("ProcessingError", f"Failed to update file: {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=f"Failed to update file: {e}")


@router.delete("/clear", summary="Clear All Uploaded Files")
def clear_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        delete_all_files(db, user_id=current_user.id)
        return {"message": "All uploaded files cleared successfully."}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to clear files: {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=f"Failed to clear files: {e}")


@router.delete("/{filename}", summary="Delete a Specific Uploaded File")
def delete_file(
    filename: str = Path(..., description="The name of the file to delete"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        delete_specific_file(db, filename, current_user.id)
        return {"message": f"File '{filename}' and its processed versions have been deleted successfully."}
    except HTTPException as he:
        raise he
    except Exception as e:
        handle_error("ProcessingError", f"Failed to delete file '{filename}': {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=f"Failed to delete file '{filename}': {e}")


@router.get("/size/uploaded", summary="Get Uploaded Files Size")
def get_uploaded_files_size_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        size = get_uploaded_files_size(db, current_user.id)
        return {"uploaded_files_size_bytes": size}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to get uploaded files size: {e}", user_id=current_user.id)
        return {"message": f"Failed to get uploaded files size: {e}"}


@router.get("/size/processed", summary="Get Processed Files Size")
def get_processed_files_size_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        size = get_processed_files_size(db, current_user.id)
        return {"processed_files_size_bytes": size}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to get processed files size: {e}", user_id=current_user.id)
        return {"message": f"Failed to get processed files size: {e}"}
