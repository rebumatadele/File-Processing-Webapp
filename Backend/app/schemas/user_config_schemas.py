# app/schemas/user_config_schemas.py

from pydantic import BaseModel, Field
from typing import Optional

class ConfigRequest(BaseModel):
    provider_choice: str = Field(..., example="OpenAI", description="AI provider choice (e.g., OpenAI, Anthropic, Gemini)")
    api_key: str = Field(..., example="sk-...", description="API key for the selected provider")

    class Config:
        from_attributes = True

class UserConfigResponse(BaseModel):
    user_id: str = Field(..., example="user_12345", description="Unique user ID")
    openai_api_key: Optional[str] = Field(None, example="sk-...", description="User's OpenAI API key")
    anthropic_api_key: Optional[str] = Field(None, example="anthropic-api-key", description="User's Anthropic API key")
    gemini_api_key: Optional[str] = Field(None, example="gemini-api-key", description="User's Gemini API key")

    class Config:
        from_attributes = True
