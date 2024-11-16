# app/routers/files.py

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from app.models.file import UploadedFileInfo
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
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Upload one or multiple text files.
    """
    try:
        saved_files = []
        for file in files:
            if not file.filename.endswith(".txt"):
                raise HTTPException(status_code=400, detail=f"Only .txt files are allowed. '{file.filename}' is not allowed.")
            content = await file.read()
            content_str = content.decode('utf-8')
            save_uploaded_file(file.filename, content_str)
            saved_files.append(file.filename)
        return {"message": f"Uploaded files: {', '.join(saved_files)}"}
    except HTTPException as he:
        raise he
    except Exception as e:
        handle_error("ProcessingError", f"Failed to upload files: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload files: {e}")

@router.get("/", summary="List Uploaded Files", response_model=List[str])
def list_files():
    """
    List all uploaded files.
    """
    try:
        files = get_uploaded_files()
        return files
    except Exception as e:
        handle_error("ProcessingError", f"Failed to list files: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list files: {e}")

@router.get("/{filename}", summary="Get File Content", response_model=UploadedFileInfo)
def get_file_content(filename: str):
    """
    Retrieve the content of a specific uploaded file.
    """
    try:
        content = load_uploaded_file_content(filename)
        if not content:
            raise HTTPException(status_code=404, detail="File not found.")
        return UploadedFileInfo(filename=filename, content=content)
    except HTTPException as he:
        raise he
    except Exception as e:
        handle_error("ProcessingError", f"Failed to retrieve file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve file: {e}")

@router.put("/{filename}", summary="Edit File Content")
def edit_file_content(filename: str, new_content: str):
    """
    Edit the content of a specific uploaded file.
    """
    try:
        update_file_content(filename, new_content)
        return {"message": f"File '{filename}' updated successfully."}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to update file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update file: {e}")

@router.delete("/clear", summary="Clear All Uploaded Files")
def clear_files():
    """
    Clear all uploaded files and related data.
    """
    try:
        delete_all_files()
        return {"message": "All uploaded files cleared successfully."}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to clear files: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear files: {e}")

@router.get("/size/uploaded", summary="Get Uploaded Files Size")
def get_uploaded_files_size_endpoint():
    """
    Get the total size of uploaded files in bytes.
    """
    try:
        size = get_uploaded_files_size()
        return {"uploaded_files_size_bytes": size}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to get uploaded files size: {e}")
        return {"message": f"Failed to get uploaded files size: {e}"}

@router.get("/size/processed", summary="Get Processed Files Size")
def get_processed_files_size_endpoint():
    """
    Get the total size of processed files in bytes.
    """
    try:
        size = get_processed_files_size()
        return {"processed_files_size_bytes": size}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to get processed files size: {e}")
        return {"message": f"Failed to get processed files size: {e}"}