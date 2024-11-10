# app/models/file.py

from pydantic import BaseModel, Field

class UploadedFileInfo(BaseModel):
    filename: str
    content: str

class ProcessedFileInfo(BaseModel):
    filename: str
    content: str
