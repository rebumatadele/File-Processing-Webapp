# app/utils/error_utils.py (or keep name handle_error in file_utils.py)
from sqlalchemy.orm import Session
from app.models.error import ErrorLog
from app.config.database import SessionLocal

def handle_error(error_type: str, message: str, user_id: str = None):
    """
    Insert an error record into the DB. 
    Because this is a utility, we can open a short-lived session here 
    or pass in a session from the caller. 
    """
    with SessionLocal() as db:
        error = ErrorLog(
            error_type=error_type,
            message=message,
            user_id=user_id
        )
        db.add(error)
        db.commit()
