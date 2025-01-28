# app/routers/usage.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict

from app.utils.rate_limiter import RateLimiter
from app.dependencies.rate_limiters import get_all_rate_limiters
from app.dependencies.database import get_db
from app.providers.auth import get_current_user  # Ensure this is implemented
from app.models.user import User  # Assuming you have a User model

router = APIRouter(
    prefix="/usage",
    tags=["Usage / Rate Limits"]
)

@router.get("/", summary="Get current Anthropic (Claude) usage status")
def get_anthropic_usage(
    rate_limiters: Dict[str, RateLimiter] = Depends(get_all_rate_limiters),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Ensure only authenticated users can access
):
    """
    Returns the current usage and rate-limit data from the RateLimiter for Anthropic (Claude) specific to the authenticated user.
    """
    anthropic_rl = rate_limiters.get("anthropic")
    if not anthropic_rl:
        raise HTTPException(status_code=404, detail="Anthropic rate limiter not found.")
    
    return anthropic_rl.get_current_limits(db)
    
