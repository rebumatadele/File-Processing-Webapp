# app/models/prompt.py

from pydantic import BaseModel, Field

class Prompt(BaseModel):
    name: str = Field(..., example="Default Prompt")
    content: str = Field(..., example="Your prompt content here.")
