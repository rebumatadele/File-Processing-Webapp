# app/models/result.py

from pydantic import BaseModel, Field

class ProcessingResult(BaseModel):
    filename: str
    content: str
