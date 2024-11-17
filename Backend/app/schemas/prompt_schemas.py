# app/schemas/prompt_schemas.py

from pydantic import BaseModel, Field
from typing import Optional

class PromptSchema(BaseModel):
    id: Optional[str]
    user_id: Optional[str]
    name: str = Field(..., example="Default Prompt")
    content: str = Field(..., example="Your prompt content here.")

    class Config:
        from_attributes = True
