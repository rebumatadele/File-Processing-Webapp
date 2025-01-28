# app/models/rate_limiter.py

from sqlalchemy import Column, Integer, Float, DateTime, String, JSON, ForeignKey, UniqueConstraint
from app.config.database import Base
from sqlalchemy.sql import func
import uuid


class RateLimiterModel(Base):
    __tablename__ = "rate_limiters"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    provider = Column(String, nullable=False)  # e.g., 'anthropic', 'openai', 'gemini'
    user_id = Column(String, ForeignKey("users.id"), nullable=False)  # New field
    
    # Local rate limiting
    max_rpm = Column(Integer, nullable=False)
    max_rph = Column(Integer, nullable=False)
    cooldown_period = Column(Float, nullable=False)
    reset_time_rpm = Column(Float, nullable=False)
    reset_time_rph = Column(Float, nullable=False)
    request_count_rpm = Column(Integer, nullable=False, default=0)
    request_count_rph = Column(Integer, nullable=False, default=0)
    
    # AI Provider rate limit status
    ai_usage = Column(JSON, nullable=True)
    
    # Retry after
    last_retry_after = Column(Float, nullable=True)
    
    # Version for optimistic locking
    version = Column(Integer, nullable=False, default=1)
    
    # Timestamp
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('provider', 'user_id', name='_provider_user_uc'),
    )
