# app/models/error.py

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base
import uuid
from datetime import datetime

class ErrorLog(Base):
    __tablename__ = "error_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow)
    error_type = Column(String, nullable=False)
    message = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)

    user = relationship("User", back_populates="error_logs")
