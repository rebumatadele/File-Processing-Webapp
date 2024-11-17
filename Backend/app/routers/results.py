# app/routers/results.py

from fastapi import APIRouter, HTTPException, Depends
import os
from fastapi.responses import FileResponse
from app.models.user import User
from app.providers.auth import get_current_user
from app.schemas.result_schemas import ProcessingResultSchema
from app.utils.file_utils import get_processed_results, sanitize_file_name, handle_error

router = APIRouter(
    prefix="/results",
    tags=["Results Retrieval"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", summary="Get All Processed Results", response_model=dict)
def get_all_results(
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all processed results for the current user.
    """
    try:
        results = get_processed_results(user_id=current_user.id)
        return results
    except Exception as e:
        handle_error("ProcessingError", f"Failed to retrieve results: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve results: {e}")

@router.get("/{filename}", summary="Get Processed Result for a Specific File", response_model=ProcessingResultSchema)
def get_result(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve the processed result for a specific file for the current user.
    """
    try:
        results = get_processed_results(user_id=current_user.id)
        content = results.get(filename)
        if not content:
            raise HTTPException(status_code=404, detail="Processed result not found for the specified file.")
        return ProcessingResultSchema(filename=filename, content=content)
    except Exception as e:
        handle_error("ProcessingError", f"Failed to retrieve result: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve result: {e}")

@router.get("/{filename}/download", summary="Download Processed Result")
def download_result(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Download the processed result as a text file for the current user.
    """
    try:
        results = get_processed_results(user_id=current_user.id)
        content = results.get(filename)
        if not content:
            raise HTTPException(status_code=404, detail="Processed result not found for the specified file.")
        sanitized_filename = sanitize_file_name(filename) + "_processed.txt"
        file_path = os.path.join("storage", "processed", current_user.id, sanitized_filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return FileResponse(
            path=file_path,
            media_type='text/plain',
            filename=sanitized_filename
        )
    except Exception as e:
        handle_error("ProcessingError", f"Failed to download result: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download result: {e}")
