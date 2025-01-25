# app/routers/results.py

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.models.processing import ProcessingJob
from app.models.user import User
from app.providers.auth import get_current_user, get_db
from app.schemas.result_schemas import ProcessingResultSchema
from app.utils.error_utils import handle_error
from app.utils.file_utils import get_processed_results, sanitize_file_name

router = APIRouter(
    prefix="/results",
    tags=["Results Retrieval"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", summary="Get All Processed Results", response_model=dict)
def get_all_results(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all processed results for the current user from DB.
    """
    try:
        results = get_processed_results(db, user_id=current_user.id)
        return results
    except Exception as e:
        handle_error("ProcessingError", f"Failed to retrieve results: {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{filename}", summary="Get Processed Result for a Specific File", response_model=ProcessingResultSchema)
def get_result(
    filename: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        all_results = get_processed_results(db, current_user.id)
        content = all_results.get(filename)
        if not content:
            raise HTTPException(status_code=404, detail="Processed result not found.")
        return ProcessingResultSchema(
            id=None,
            user_id=current_user.id,
            job_id=None,
            filename=filename,
            content=content,
            created_at=None
        )
    except Exception as e:
        handle_error("ProcessingError", f"Failed to retrieve result: {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{filename}/download", summary="Download Processed Result")
def download_result(
    filename: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a temporary .txt file and return a FileResponse.
    """
    try:
        results = get_processed_results(db, current_user.id)
        content = results.get(filename)
        if not content:
            raise HTTPException(status_code=404, detail="Processed result not found.")

        sanitized = sanitize_file_name(filename) + "_processed.txt"
        tmp_dir = f"tmp_downloads/{current_user.id}"
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_path = os.path.join(tmp_dir, sanitized)

        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(content)

        return FileResponse(
            path=tmp_path,
            media_type="text/plain",
            filename=sanitized
        )

    except Exception as e:
        handle_error("ProcessingError", f"Failed to download result: {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/final/download", summary="Download Final Aggregated Results")
def download_final_result(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download the final aggregated results file for the user.
    """
    try:
        # Assuming the latest completed job contains the final results
        latest_job = db.query(ProcessingJob).filter_by(user_id=current_user.id, status="completed").order_by(ProcessingJob.completed_at.desc()).first()
        if not latest_job:
            raise HTTPException(status_code=404, detail="No completed processing jobs found.")

        final_filename = f"final_results_{latest_job.id}.txt"
        sanitized = sanitize_file_name(final_filename)
        tmp_dir = f"tmp_downloads/{current_user.id}"
        final_file_path = os.path.join(tmp_dir, sanitized)

        if not os.path.exists(final_file_path):
            raise HTTPException(status_code=404, detail="Final results file not found.")

        return FileResponse(
            path=final_file_path,
            media_type="text/plain",
            filename=sanitized
        )

    except Exception as e:
        handle_error("ProcessingError", f"Failed to download final results: {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=str(e))
