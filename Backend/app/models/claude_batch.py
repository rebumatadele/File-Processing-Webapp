# app/models/claude_batch.py

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from app.config.database import Base
import uuid
from datetime import datetime

class Batch(Base):
    __tablename__ = "batches"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    external_batch_id = Column(String, unique=True, nullable=True)
    prompt = Column(String, nullable=False)
    chunk_size = Column(Integer, nullable=False)
    chunk_by = Column(String, nullable=False)
    selected_model = Column(String, nullable=False)
    email = Column(String, nullable=True)
    status = Column(String, default="pending")
    request_counts = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    results_url = Column(String, nullable=True)

    user = relationship("User", back_populates="batches")
    items = relationship("BatchRequestItem", back_populates="batch", cascade="all, delete-orphan")

class BatchRequestItem(Base):
    __tablename__ = "batch_request_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = Column(String, ForeignKey("batches.id"), nullable=False)
    custom_id = Column(String, nullable=False)
    params = Column(JSON, nullable=False)
    result = Column(String, nullable=True)

    batch = relationship("Batch", back_populates="items")
