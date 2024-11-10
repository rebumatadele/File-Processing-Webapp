# app/models/error.py

from pydantic import BaseModel, Field

class ErrorLog(BaseModel):
    timestamp: str
    error_type: str
    message: str
