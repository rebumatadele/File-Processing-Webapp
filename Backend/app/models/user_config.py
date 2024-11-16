# app/models/user_config.py

from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class UserConfig(BaseModel):
    user_id: str = Field(..., example="user_12345")
    openai_api_key: Optional[str] = Field(None, example="sk-...")
    anthropic_api_key: Optional[str] = Field(None, example="anthropic-api-key")
    gemini_api_key: Optional[str] = Field(None, example="gemini-api-key")
