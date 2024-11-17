# app/schemas/processing_schemas.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class ProcessingSettings(BaseModel):
    provider_choice: str = Field(..., description="Choice of AI provider (e.g., 'openai', 'anthropic', 'gemini')")
    prompt: str = Field(..., description="Prompt to send to the AI model")
    chunk_size: Optional[int] = Field(1024, description="Size of text chunks")
    chunk_by: Optional[str] = Field("word", description="Method to chunk text ('word', 'character')")
    selected_model: Optional[str] = Field(None, description="Specific model choice if applicable")
    email: EmailStr = Field(..., description="Email address to send the processed files to")
    openai_api_key: Optional[str] = Field(None, description="User's OpenAI API Key")
    anthropic_api_key: Optional[str] = Field(None, description="User's Anthropic API Key")
    gemini_api_key: Optional[str] = Field(None, description="User's Gemini API Key")

    class Config:
        from_attributes = True

class ProcessingJobSchema(BaseModel):
    id: Optional[str]
    user_id: Optional[str]
    provider_choice: str
    prompt: str
    chunk_size: int
    chunk_by: str
    selected_model: Optional[str]
    email: EmailStr
    status: Optional[str]
    created_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
