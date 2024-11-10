# app/routers/results.py

from fastapi import APIRouter, HTTPException
import os
from fastapi.responses import FileResponse
from app.models.result import ProcessingResult
from app.utils.file_utils import get_processed_results, sanitize_file_name, handle_error

router = APIRouter(
    prefix="/results",
    tags=["Results Retrieval"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", summary="Get All Processed Results", response_model=dict)
def get_all_results():
    """
    Retrieve all processed results.
    """
    try:
        results = get_processed_results()
        return results
    except Exception as e:
        handle_error("ProcessingError", f"Failed to retrieve results: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve results: {e}")

@router.get("/{filename}", summary="Get Processed Result for a Specific File", response_model=ProcessingResult)
def get_result(filename: str):
    """
    Retrieve the processed result for a specific file.
    """
    try:
        results = get_processed_results()
        content = results.get(filename)
        if not content:
            raise HTTPException(status_code=404, detail="Processed result not found for the specified file.")
        return ProcessingResult(filename=filename, content=content)
    except HTTPException as he:
        raise he
    except Exception as e:
        handle_error("ProcessingError", f"Failed to retrieve result: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve result: {e}")

@router.get("/{filename}/download", summary="Download Processed Result")
def download_result(filename: str):
    """
    Download the processed result as a text file.
    """
    try:
        results = get_processed_results()
        content = results.get(filename)
        if not content:
            raise HTTPException(status_code=404, detail="Processed result not found for the specified file.")
        sanitized_filename = sanitize_file_name(filename) + "_processed.txt"
        file_path = os.path.join("storage", "processed", sanitized_filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return FileResponse(
            path=file_path,
            media_type='text/plain',
            filename=sanitized_filename
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        handle_error("ProcessingError", f"Failed to download result: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download result: {e}")
