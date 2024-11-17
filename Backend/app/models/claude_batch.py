# app/models/claude_batch.py

from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

class BatchRequestItem(BaseModel):
    custom_id: str = Field(..., description="Unique identifier for the request")
    params: dict = Field(..., description="Parameters for the Messages API")

class StartBatchProcessingRequest(BaseModel):
    prompt: str = Field(..., description="Prompt to send to Claude")
    chunk_size: int = Field(..., description="Size of text chunks")
    chunk_by: str = Field(..., description="Method to chunk text ('word' , 'sentence' , Character)")
    selected_model: str = Field(..., description="Specific Claude model to use")  # Renamed field
    email: Optional[EmailStr] = Field(None, description="Email address to send the processed files to")
    
    # User-provided API keys (optional)
    anthropic_api_key: Optional[str] = Field(None, description="User's Anthropic API Key")

class StartBatchProcessingResponse(BaseModel):
    batch_id: str = Field(..., description="Unique identifier for the batch")
    message: str = Field(..., description="Status message")

class BatchStatusResponse(BaseModel):
    batch_id: str = Field(..., description="Unique identifier for the batch")
    processing_status: str = Field(..., description="Current processing status of the batch")
    request_counts: dict = Field(..., description="Counts of request statuses within the batch")
    created_at: Optional[str] = Field(None, description="Batch creation timestamp")
    ended_at: Optional[str] = Field(None, description="Batch completion timestamp")
    expires_at: Optional[str] = Field(None, description="Batch expiration timestamp")
    results_url: Optional[str] = Field(None, description="URL to fetch batch results")
