# app/models/user.py

from sqlalchemy import Column, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship
from app.config.database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    config = relationship("UserConfig", back_populates="user", uselist=False)
    batches = relationship("Batch", back_populates="user")
    error_logs = relationship("ErrorLog", back_populates="user")
    uploaded_files = relationship("UploadedFile", back_populates="user")
    processing_jobs = relationship("ProcessingJob", back_populates="user")
    prompts = relationship("Prompt", back_populates="user")
    processing_results = relationship("ProcessingResult", back_populates="user")