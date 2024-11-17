# app/models/user_config.py

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base
import uuid

class UserConfig(Base):
    __tablename__ = "user_configs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    openai_api_key = Column(String, nullable=True)
    anthropic_api_key = Column(String, nullable=True)
    gemini_api_key = Column(String, nullable=True)

    user = relationship("User", back_populates="config")
