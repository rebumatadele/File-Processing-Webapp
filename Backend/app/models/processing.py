# app/models/processing.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class ProcessingSettings(BaseModel):
    provider_choice: str = Field(..., description="Choice of AI provider (e.g., 'openai', 'anthropic', 'gemini')")
    prompt: str = Field(..., description="Prompt to send to the AI model")
    chunk_size: Optional[int] = Field(1024, description="Size of text chunks")
    chunk_by: Optional[str] = Field("word", description="Method to chunk text ('word', 'character')")
    selected_model: Optional[str] = Field(None, description="Specific model choice if applicable")
    email: EmailStr = Field(..., description="Email address to send the processed files to")
    
    # User-provided API keys
    openai_api_key: Optional[str] = Field(None, description="User's OpenAI API Key")
    anthropic_api_key: Optional[str] = Field(None, description="User's Anthropic API Key")
    gemini_api_key: Optional[str] = Field(None, description="User's Gemini API Key")
