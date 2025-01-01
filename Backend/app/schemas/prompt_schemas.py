# app/schemas/prompt_schemas.py

from datetime import datetime
from pydantic import BaseModel, Field, validator
from typing import Optional, List
import re

class PromptBase(BaseModel):
    name: str = Field(..., example="Default Prompt", min_length=1, max_length=100)
    description: Optional[str] = Field(None, example="A default prompt for general use.")
    tags: Optional[List[str]] = Field(None, example=["general", "default"])
    content: str = Field(..., example="Your prompt content here.")

    @validator('name')
    def name_must_be_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z0-9 _-]+$', v):
            raise ValueError('Prompt name must be alphanumeric and can include spaces, underscores, or hyphens.')
        return v

    @validator('tags', each_item=True)
    def tags_must_be_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z0-9 _-]+$', v):
            raise ValueError('Each tag must be alphanumeric and can include spaces, underscores, or hyphens.')
        return v

class PromptCreate(PromptBase):
    pass

class PromptUpdate(BaseModel):
    description: Optional[str] = Field(None, example="Updated description.")
    tags: Optional[List[str]] = Field(None, example=["updated", "prompt"])
    content: Optional[str] = Field(None, example="Updated prompt content.")

class PromptSchema(PromptBase):
    id: Optional[str]
    user_id: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class PromptResponse(PromptSchema):
    pass
