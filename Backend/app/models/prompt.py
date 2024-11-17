# app/models/prompt.py

from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base
import uuid

class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    content = Column(Text, nullable=False)

    user = relationship("User", back_populates="prompts")
