# app/dependencies/rate_limiters.py

from typing import Dict
from fastapi import Depends
from app.utils.rate_limiter import RateLimiter
from app.providers.auth import get_current_user
from app.models.user import User

def get_all_rate_limiters(
    current_user: User = Depends(get_current_user)
) -> Dict[str, RateLimiter]:
    """
    Dependency that provides a dictionary of all RateLimiter instances for the current user.
    """
    return {
        "anthropic": RateLimiter(provider="anthropic", user_id=current_user.id),
        "openai": RateLimiter(provider="openai", user_id=current_user.id),
        "gemini": RateLimiter(provider="gemini", user_id=current_user.id)
    }
