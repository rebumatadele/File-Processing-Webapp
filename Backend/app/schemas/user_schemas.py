# app/schemas/user_schemas.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True  # Updated for Pydantic v2

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True  # Updated for Pydantic v2

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True  # Updated for Pydantic v2

class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        from_attributes = True  # Optional, useful if needed

class TokenData(BaseModel):
    user_id: Optional[str] = None

    class Config:
        from_attributes = True  # Optional, useful if needed
