# app/models/processing_status.py

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from app.config.database import Base
import uuid
from datetime import datetime

class ProcessingFileStatus(Base):
    __tablename__ = "processing_file_status"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, ForeignKey("processing_jobs.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)

    total_chunks = Column(Integer, default=0)
    processed_chunks = Column(Integer, default=0)
    progress_percentage = Column(Float, default=0.0)

    status = Column(String, default="pending")  # e.g. "in_progress", "completed", "failed"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # If you want relationships:
    # job = relationship("ProcessingJob", back_populates="file_statuses")
    # user = relationship("User")

