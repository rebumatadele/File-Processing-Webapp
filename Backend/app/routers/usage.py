# app/routers/usage.py

from fastapi import APIRouter
from app.utils.rate_limiter import rate_limiter_instance

router = APIRouter(
    prefix="/usage",
    tags=["Usage / Rate Limits"]
)

@router.get("/anthropic", summary="Get current Anthropic usage status")
def get_anthropic_usage():
    """
    Returns the current usage and rate-limit data from the RateLimiter.
    """
    return rate_limiter_instance.get_current_limits()
