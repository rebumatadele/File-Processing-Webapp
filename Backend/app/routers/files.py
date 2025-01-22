# app/routers/files.py

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import List
from sqlalchemy.orm import Session
from app.models.user import User
from app.providers.auth import get_current_user, get_db
from app.schemas.file_schemas import FileContentSchema
from app.utils.error_utils import handle_error
from app.utils.file_utils import (
    save_uploaded_file,
    get_uploaded_files,
    load_uploaded_file_content,
    update_file_content,
    delete_all_files,
    get_uploaded_files_size,
    get_processed_files_size
)

router = APIRouter(
    prefix="/files",
    tags=["File Management"],
    responses={404: {"description": "Not found"}},
)

@router.post("/upload", summary="Upload Text Files")
async def upload_files(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        saved_files = []
        for file in files:
            if not file.filename.endswith(".txt"):
                raise HTTPException(
                    status_code=400,
                    detail=f"Only .txt files are allowed. '{file.filename}' is not allowed."
                )
            content_bytes = await file.read()
            content_str = content_bytes.decode("utf-8", errors="replace")

            save_uploaded_file(db, file.filename, content_str, user_id=current_user.id)
            saved_files.append(file.filename)

        return {"message": f"Uploaded files: {', '.join(saved_files)}"}
    except Exception as e:
        handle_error("FileUploadError", f"Failed to upload files: {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=f"Failed to upload files: {e}")

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

@router.get("/{filename}", summary="Get File Content", response_model=FileContentSchema)
def get_file_content(
    filename: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        content = load_uploaded_file_content(db, filename, user_id=current_user.id)
        if not content:
            raise HTTPException(status_code=404, detail="File not found.")
        return FileContentSchema(filename=filename, content=content)
    except Exception as e:
        handle_error("ProcessingError", f"Failed to retrieve file: {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve file: {e}")

@router.put("/{filename}", summary="Edit File Content")
def edit_file_content(
    filename: str,
    new_content: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        update_file_content(db, filename, new_content, user_id=current_user.id)
        return {"message": f"File '{filename}' updated successfully."}
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
