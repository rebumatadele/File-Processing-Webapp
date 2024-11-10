# app/models/processing.py

from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class ProcessingSettings(BaseModel):
    chunk_size: int = Field(..., example=500, ge=1, le=5000)
    chunk_by: str = Field(..., example="words", pattern="^(words|sentences|paragraphs)$")
    provider_choice: str = Field(..., example="Gemini")
    selected_model: Optional[str] = Field(None, example="gemini-1.5-flash")  # Renamed field
    prompt: str = Field(..., example="Your prompt here.")
    email: EmailStr = Field(..., example="user@gmail.com")
