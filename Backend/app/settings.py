# app/settings.py

import os
from typing import Optional
from pydantic import EmailStr, Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Keys
    openai_api_key: Optional[str] = Field(None, description="User's OpenAI API Key")
    anthropic_api_key: Optional[str] = Field(None, description="User's Anthropic API Key")
    gemini_api_key: Optional[str] = Field(None, description="User's Gemini API Key")
    api_key: Optional[str] = Field(None, description="API Key for Authentication")

    # Email Configuration
    mail_username: Optional[str] = Field(None, description="Username for the mail server")
    mail_password: Optional[str] = Field(None, description="Password for the mail server")
    mail_from: Optional[EmailStr] = Field(None, description="Sender's email address")
    mail_port: Optional[int] = Field(None, description="Port for the mail server")
    mail_server: Optional[str] = Field(None, description="Mail server address")
    mail_tls: Optional[bool] = Field(False, description="Enable TLS for the mail server")
    mail_ssl: Optional[bool] = Field(True, description="Enable SSL for the mail server")

    # Rate Limit Config
    max_rpm: int = 100
    max_rph: int = 3000
    cooldown_period: int = 10
    token_limit: int = 100000

    # Additional settings can be added here
    secret_key: str = "qwertyuioplkjhgfdsazxcvbnm"  # Use a strong, unique key
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    database_url: str = Field(..., env="DATABASE_URL")  
    frontend_url: str = Field(..., env="FRONTEND_URL")
    backend_url: str = Field(..., env="BACKEND_URL")
    model_config = {
        "env_file": ".env",  # Specifies the .env file location
        "extra": "forbid",    # Disallows extra fields not defined in the model
    }

settings = Settings()
