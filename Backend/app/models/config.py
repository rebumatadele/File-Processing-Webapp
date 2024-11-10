# app/models/config.py

from pydantic import BaseModel, Field
from typing import Optional

class ConfigRequest(BaseModel):
    selected_model: Optional[str] = None  # Ensure no 'model_choice' here
    provider_choice: str = Field(..., example="OpenAI")
    api_key: str = Field(..., example="sk-...")
