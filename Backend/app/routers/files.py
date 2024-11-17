# app/routers/files.py

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import List
from app.models.user import User
from app.providers.auth import get_current_user
from app.schemas.file_schemas import UploadedFileSchema
from app.utils.file_utils import (
    get_processed_files_size,
    get_uploaded_files_size,
    save_uploaded_file,
    get_uploaded_files,
    load_uploaded_file_content,
    update_file_content,
    delete_all_files,
    handle_error
)

router = APIRouter(
    prefix="/files",
    tags=["File Management"],
    responses={404: {"description": "Not found"}},
)

@router.post("/upload", summary="Upload Text Files")
async def upload_files(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload one or multiple text files for the current user.
    """
    try:
        saved_files = []
        for file in files:
            if not file.filename.endswith(".txt"):
                raise HTTPException(status_code=400, detail=f"Only .txt files are allowed. '{file.filename}' is not allowed.")
            content = await file.read()
            content_str = content.decode('utf-8')
            save_uploaded_file(file.filename, content_str, user_id=current_user.id)
            saved_files.append(file.filename)
        return {"message": f"Uploaded files: {', '.join(saved_files)}"}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to upload files: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload files: {e}")

@router.get("/", summary="List Uploaded Files", response_model=List[str])
def list_files(
    current_user: User = Depends(get_current_user)
):
    """
    List all uploaded files for the current user.
    """
    try:
        files = get_uploaded_files(user_id=current_user.id)
        return files
    except Exception as e:
        handle_error("ProcessingError", f"Failed to list files: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list files: {e}")

@router.get("/{filename}", summary="Get File Content", response_model=UploadedFileSchema)
def get_file_content(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve the content of a specific uploaded file for the current user.
    """
    try:
        content = load_uploaded_file_content(filename, user_id=current_user.id)
        if not content:
            raise HTTPException(status_code=404, detail="File not found.")
        return UploadedFileSchema(filename=filename, content=content)
    except Exception as e:
        handle_error("ProcessingError", f"Failed to retrieve file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve file: {e}")

@router.put("/{filename}", summary="Edit File Content")
def edit_file_content(
    filename: str,
    new_content: str,
    current_user: User = Depends(get_current_user)
):
    """
    Edit the content of a specific uploaded file for the current user.
    """
    try:
        update_file_content(filename, new_content, user_id=current_user.id)
        return {"message": f"File '{filename}' updated successfully."}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to update file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update file: {e}")

@router.delete("/clear", summary="Clear All Uploaded Files")
def clear_files(
    current_user: User = Depends(get_current_user)
):
    """
    Clear all uploaded files and related data for the current user.
    """
    try:
        delete_all_files(user_id=current_user.id)
        return {"message": "All uploaded files cleared successfully."}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to clear files: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear files: {e}")

@router.get("/size/uploaded", summary="Get Uploaded Files Size")
def get_uploaded_files_size_endpoint(
    current_user: User = Depends(get_current_user)
):
    """
    Get the total size of uploaded files in bytes for the current user.
    """
    try:
        size = get_uploaded_files_size(user_id=current_user.id)
        return {"uploaded_files_size_bytes": size}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to get uploaded files size: {e}")
        return {"message": f"Failed to get uploaded files size: {e}"}

@router.get("/size/processed", summary="Get Processed Files Size")
def get_processed_files_size_endpoint(
    current_user: User = Depends(get_current_user)
):
    """
    Get the total size of processed files in bytes for the current user.
    """
    try:
        size = get_processed_files_size(user_id=current_user.id)
        return {"processed_files_size_bytes": size}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to get processed files size: {e}")
        return {"message": f"Failed to get processed files size: {e}"}
