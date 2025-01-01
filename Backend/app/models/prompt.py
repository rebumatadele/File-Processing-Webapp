# app/models/prompt.py

from sqlalchemy import Column, String, Text, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.config.database import Base
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY  # If using PostgreSQL

class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)  # Can store as comma-separated or JSON
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="prompts")

    __table_args__ = (
        # Ensure unique prompt names per user
        UniqueConstraint('user_id', 'name', name='_user_prompt_uc'),
    )
