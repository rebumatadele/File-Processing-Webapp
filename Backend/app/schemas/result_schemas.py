# app/schemas/result_schemas.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProcessingResultSchema(BaseModel):
    id: Optional[str]
    user_id: Optional[str]
    job_id: Optional[str]
    filename: str
    content: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True
