# app/schemas/error_schemas.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ErrorLogSchema(BaseModel):
    id: Optional[str]
    timestamp: datetime
    error_type: str
    message: str
    user_id: Optional[str]

    class Config:
        from_attributes = True
