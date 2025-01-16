# app/schemas/file_schemas.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UploadedFileSchema(BaseModel):
    id: Optional[str]
    user_id: Optional[str]
    filename: str
    content: str
    uploaded_at: Optional[datetime]

    class Config:
        from_attributes = True

class ProcessedFileSchema(BaseModel):
    id: Optional[str]
    uploaded_file_id: Optional[str]
    filename: str
    content: str
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True
class FileContentSchema(BaseModel):
    filename: str
    content: str