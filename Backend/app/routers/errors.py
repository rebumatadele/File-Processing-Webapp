# app/routers/errors.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.user import User
from app.providers.auth import get_current_user
from app.utils.file_utils import list_errors, clear_error_logs

router = APIRouter(
    prefix="/errors",
    tags=["Error Logging"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", summary="Get Error Logs", response_model=List[str])
def get_error_logs(
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve the list of error logs for the current user.
    """
    errors = list_errors(user_id=current_user.id)
    return errors

@router.delete("/", summary="Clear Error Logs", response_model=dict)
def clear_errors(
    current_user: User = Depends(get_current_user)
):
    """
    Clear all error logs for the current user.
    """
    try:
        clear_error_logs(user_id=current_user.id)
        return {"message": "Error logs cleared successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear error logs: {e}")
