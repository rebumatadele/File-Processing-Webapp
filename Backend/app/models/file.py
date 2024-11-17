# app/models/file.py

from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.config.database import Base
import uuid
from datetime import datetime

class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="uploaded_files")
    processed_files = relationship("ProcessedFile", back_populates="uploaded_file", cascade="all, delete-orphan")

class ProcessedFile(Base):
    __tablename__ = "processed_files"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    uploaded_file_id = Column(String, ForeignKey("uploaded_files.id"), nullable=False)
    filename = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    processed_at = Column(DateTime, default=datetime.utcnow)

    uploaded_file = relationship("UploadedFile", back_populates="processed_files")
