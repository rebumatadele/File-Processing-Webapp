# app/models/result.py

from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.config.database import Base
import uuid
from datetime import datetime

class ProcessingResult(Base):
    __tablename__ = "processing_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    job_id = Column(String, ForeignKey("processing_jobs.id"), nullable=False)
    filename = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="processing_results")
    job = relationship("ProcessingJob", back_populates="results")
