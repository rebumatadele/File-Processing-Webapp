# app/models/cache.py
from sqlalchemy import JSON, Column, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.config.database import Base
import uuid
from datetime import datetime

class CachedResult(Base):
    __tablename__ = "cached_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=True)
    provider_choice = Column(String, nullable=False)
    model_choice = Column(String, nullable=True)
    chunk = Column(Text, nullable=False)
    response = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
