# app/utils/rate_limiter.py

import asyncio
import time
from typing import Any, Dict, Optional
from datetime import datetime

from sqlalchemy.orm import Session
try:
    from sqlalchemy.exc import StaleDataError  # For SQLAlchemy >=1.4
except ImportError:
    try:
        from sqlalchemy.orm.exc import StaleDataError  # For SQLAlchemy <1.4
    except ImportError:
        # If StaleDataError is not found, define a fallback or raise an error
        StaleDataError = Exception  # Fallback to generic Exception
        print("StaleDataError not found in SQLAlchemy. Using generic Exception as fallback.")

from app.settings import settings
from app.models.rate_limiter import RateLimiterModel
from app.config.database import SessionLocal 

class RateLimiter:
    def __init__(self, provider: str, user_id: str):
        self.provider = provider
        self.user_id = user_id  # Store user_id for per-user rate limiting
        self.lock = asyncio.Lock()
        self.session_factory = SessionLocal  # Reference to the sessionmaker

    def _get_or_create_rate_limiter(self, session: Session) -> RateLimiterModel:
        rate_limiter = session.query(RateLimiterModel).filter_by(provider=self.provider, user_id=self.user_id).first()
        if not rate_limiter:
            rate_limiter = RateLimiterModel(
                provider=self.provider,
                user_id=self.user_id,
                max_rpm=settings.max_rpm,
                max_rph=settings.max_rph,
                cooldown_period=settings.cooldown_period,
                reset_time_rpm=time.time() + 60,
                reset_time_rph=time.time() + 3600,
                request_count_rpm=0,
                request_count_rph=0
            )
            session.add(rate_limiter)
            session.commit()
            session.refresh(rate_limiter)
        return rate_limiter

    async def acquire(self):
        async with self.lock:
            success = False
            while not success:
                session = self.session_factory()
                try:
                    rate_limiter = self._get_or_create_rate_limiter(session)
                    now = time.time()

                    if now >= rate_limiter.reset_time_rpm:
                        rate_limiter.reset_time_rpm = now + 60
                        rate_limiter.request_count_rpm = 0

                    if now >= rate_limiter.reset_time_rph:
                        rate_limiter.reset_time_rph = now + 3600
                        rate_limiter.request_count_rph = 0

                    # If rate limits exceeded, wait for cooldown_period or last_retry_after if set
                    if (rate_limiter.request_count_rpm >= rate_limiter.max_rpm) or \
                       (rate_limiter.request_count_rph >= rate_limiter.max_rph):
                        wait_time = rate_limiter.last_retry_after or rate_limiter.cooldown_period
                        await asyncio.sleep(wait_time)
                        now = time.time()
                        rate_limiter.reset_time_rpm = now + 60
                        rate_limiter.reset_time_rph = now + 3600
                        rate_limiter.request_count_rpm = 0
                        rate_limiter.request_count_rph = 0

                    rate_limiter.request_count_rpm += 1
                    rate_limiter.request_count_rph += 1

                    # Increment version for optimistic locking
                    rate_limiter.version += 1

                    session.commit()
                    success = True
                except StaleDataError:
                    session.rollback()
                    # Retry fetching the updated rate limiter
                except Exception as e:
                    session.rollback()
                    print(f"Unexpected error during rate limiting: {e}")
                    raise e
                finally:
                    session.close()

    async def update_from_headers(self, headers: Dict[str, Any]):
        async with self.lock:
            success = False
            while not success:
                session = self.session_factory()
                try:
                    rate_limiter = self._get_or_create_rate_limiter(session)

                    # Update AI provider rate limit data
                    ai_usage = rate_limiter.ai_usage or {}
                    # Adjust the keys based on actual headers from the provider
                    # Example for Anthropic headers:
                    ai_usage['requests_limit'] = self._safe_int(headers.get('anthropic-ratelimit-requests-limit'))
                    ai_usage['requests_remaining'] = self._safe_int(headers.get('anthropic-ratelimit-requests-remaining'))
                    ai_usage['requests_reset_time'] = self._parse_datetime(headers.get('anthropic-ratelimit-requests-reset')).isoformat() if self._parse_datetime(headers.get('anthropic-ratelimit-requests-reset')) else None

                    ai_usage['tokens_limit'] = self._safe_int(headers.get('anthropic-ratelimit-tokens-limit'))
                    ai_usage['tokens_remaining'] = self._safe_int(headers.get('anthropic-ratelimit-tokens-remaining'))
                    ai_usage['tokens_reset_time'] = self._parse_datetime(headers.get('anthropic-ratelimit-tokens-reset')).isoformat() if self._parse_datetime(headers.get('anthropic-ratelimit-tokens-reset')) else None

                    ai_usage['input_tokens_limit'] = self._safe_int(headers.get('anthropic-ratelimit-input-tokens-limit'))
                    ai_usage['input_tokens_remaining'] = self._safe_int(headers.get('anthropic-ratelimit-input-tokens-remaining'))
                    ai_usage['input_tokens_reset_time'] = self._parse_datetime(headers.get('anthropic-ratelimit-input-tokens-reset')).isoformat() if self._parse_datetime(headers.get('anthropic-ratelimit-input-tokens-reset')) else None

                    ai_usage['output_tokens_limit'] = self._safe_int(headers.get('anthropic-ratelimit-output-tokens-limit'))
                    ai_usage['output_tokens_remaining'] = self._safe_int(headers.get('anthropic-ratelimit-output-tokens-remaining'))
                    ai_usage['output_tokens_reset_time'] = self._parse_datetime(headers.get('anthropic-ratelimit-output-tokens-reset')).isoformat() if self._parse_datetime(headers.get('anthropic-ratelimit-output-tokens-reset')) else None

                    rate_limiter.ai_usage = ai_usage

                    # Handle Retry-After header
                    retry_after = headers.get('retry-after')
                    if retry_after:
                        try:
                            rate_limiter.last_retry_after = float(retry_after)
                        except ValueError:
                            rate_limiter.last_retry_after = None

                    # Increment version for optimistic locking
                    rate_limiter.version += 1

                    session.commit()
                    success = True
                except StaleDataError:
                    session.rollback()
                    # Retry fetching the updated rate limiter
                except Exception as e:
                    session.rollback()
                    print(f"Unexpected error during updating from headers: {e}")
                    raise e
                finally:
                    session.close()

    def get_current_limits(self, db: Session) -> Dict[str, Any]:
        """
        Retrieves the current rate limits and usage.
        """
        rate_limiter = db.query(RateLimiterModel).filter_by(provider=self.provider, user_id=self.user_id).first()
        if not rate_limiter:
            return {}
        return {
            "local_usage": {
                "max_rpm": rate_limiter.max_rpm,
                "max_rph": rate_limiter.max_rph,
                "current_rpm": rate_limiter.request_count_rpm,
                "current_rph": rate_limiter.request_count_rph,
                "reset_time_rpm": rate_limiter.reset_time_rpm,
                "reset_time_rph": rate_limiter.reset_time_rph,
                "cooldown_period": rate_limiter.cooldown_period,
                "last_retry_after": rate_limiter.last_retry_after,
            },
            "ai_usage": rate_limiter.ai_usage or {}
        }

    def _safe_int(self, value: Optional[str]) -> Optional[int]:
        try:
            return int(value) if value is not None else None
        except:
            return None

    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        if not dt_str:
            return None
        try:
            # Removing trailing Z for ISO format parsing
            if dt_str.endswith('Z'):
                dt_str = dt_str[:-1]
            return datetime.fromisoformat(dt_str)
        except Exception:
            return None