# app/models/processing.py

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.config.database import Base
import uuid
from datetime import datetime

class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    provider_choice = Column(String, nullable=False)
    prompt = Column(Text, nullable=False)
    chunk_size = Column(Integer, default=1024)
    chunk_by = Column(String, default="word")
    selected_model = Column(String, nullable=True)
    email = Column(String, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="processing_jobs")
    results = relationship("ProcessingResult", back_populates="job", cascade="all, delete-orphan")
