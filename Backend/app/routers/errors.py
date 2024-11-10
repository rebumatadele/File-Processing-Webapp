# app/routers/errors.py

from fastapi import APIRouter
from typing import List
from app.utils.file_utils import list_errors, clear_error_logs
from app.models.error import ErrorLog

router = APIRouter(
    prefix="/errors",
    tags=["Error Logging"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", summary="Get Error Logs", response_model=List[str])
def get_error_logs():
    """
    Retrieve the list of error logs.
    """
    errors = list_errors()
    return errors

@router.delete("/", summary="Clear Error Logs")
def clear_errors():
    """
    Clear all error logs.
    """
    clear_error_logs()
    return {"message": "Error logs cleared successfully."}
