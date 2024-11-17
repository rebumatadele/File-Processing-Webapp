# app/schemas/batch_schemas.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from datetime import datetime

class BatchRequestItemSchema(BaseModel):
    id: Optional[str]
    custom_id: str = Field(..., description="Unique identifier for the request")
    params: dict = Field(..., description="Parameters for the Messages API")
    batch_id: Optional[str]
    result: Optional[str]

    class Config:
        from_attributes = True

class BatchSchema(BaseModel):
    id: Optional[str]
    user_id: Optional[str]
    external_batch_id: Optional[str]
    prompt: str = Field(..., description="Prompt to send to Claude")
    chunk_size: int = Field(..., description="Size of text chunks")
    chunk_by: str = Field(..., description="Method to chunk text ('word', 'sentence', 'character')")
    selected_model: str = Field(..., description="Specific Claude model to use")
    email: Optional[EmailStr] = Field(None, description="Email address to send the processed files to")
    status: Optional[str]
    request_counts: Optional[Dict]
    created_at: Optional[datetime]
    ended_at: Optional[datetime]
    expires_at: Optional[datetime]
    results_url: Optional[str]
    items: Optional[List[BatchRequestItemSchema]] = []

    class Config:
        from_attributes = True

class StartBatchProcessingRequest(BaseModel):
    prompt: str = Field(..., description="Prompt to send to Claude")
    chunk_size: int = Field(..., description="Size of text chunks")
    chunk_by: str = Field(..., description="Method to chunk text ('word', 'sentence', 'character')")
    selected_model: str = Field(..., description="Specific Claude model to use")
    email: Optional[EmailStr] = Field(None, description="Email address to send the processed files to")
    anthropic_api_key: Optional[str] = Field(None, description="User's Anthropic API Key")

    class Config:
        from_attributes = True

class StartBatchProcessingResponse(BaseModel):
    batch_id: str = Field(..., description="Unique identifier for the batch")
    message: str = Field(..., description="Status message")

    class Config:
        from_attributes = True

class BatchStatusResponse(BaseModel):
    batch_id: str = Field(..., description="Unique identifier for the batch")
    processing_status: str = Field(..., description="Current processing status of the batch")
    request_counts: Optional[Dict] = Field(..., description="Counts of request statuses within the batch")
    created_at: Optional[datetime] = Field(None, description="Batch creation timestamp")
    ended_at: Optional[datetime] = Field(None, description="Batch completion timestamp")
    expires_at: Optional[datetime] = Field(None, description="Batch expiration timestamp")
    results_url: Optional[str] = Field(None, description="URL to fetch batch results")

    class Config:
        from_attributes = True
