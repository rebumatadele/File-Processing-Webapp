# app/routers/errors.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.models.user import User
from app.providers.auth import get_current_user, get_db
from app.models.error import ErrorLog

router = APIRouter(
    prefix="/errors",
    tags=["Error Logging"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", summary="Get Error Logs")
def get_error_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve the list of error logs for the current user from the ErrorLog table.
    """
    logs = db.query(ErrorLog).filter_by(user_id=current_user.id).all()
    # Return as needed, e.g. a list of dicts
    return [
        {
            "id": log.id,
            "timestamp": log.timestamp,
            "error_type": log.error_type,
            "message": log.message
        }
        for log in logs
    ]

@router.delete("/", summary="Clear Error Logs")
def clear_errors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Clear all error logs for the current user from the DB.
    """
    try:
        db.query(ErrorLog).filter_by(user_id=current_user.id).delete()
        db.commit()
        return {"message": "Error logs cleared successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to clear error logs: {e}")
