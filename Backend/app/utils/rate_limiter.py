# app/utils/rate_limiter.py

import asyncio
import time
from typing import Any, Dict, Optional
from datetime import datetime
from pydantic import BaseModel

from app.settings import settings

class RateLimiter:
    def __init__(self):
        # Local rate limiting parameters
        self.max_rpm = settings.max_rpm
        self.max_rph = settings.max_rph
        self.cooldown_period = settings.cooldown_period

        self.lock = asyncio.Lock()
        self.reset_time_rpm = time.time() + 60
        self.reset_time_rph = time.time() + 3600
        self.request_count_rpm = 0
        self.request_count_rph = 0

        # Anthropic rate limit status storage
        self.requests_limit: Optional[int] = None
        self.requests_remaining: Optional[int] = None
        self.requests_reset_time: Optional[datetime] = None

        self.tokens_limit: Optional[int] = None
        self.tokens_remaining: Optional[int] = None
        self.tokens_reset_time: Optional[datetime] = None

        self.input_tokens_limit: Optional[int] = None
        self.input_tokens_remaining: Optional[int] = None
        self.input_tokens_reset_time: Optional[datetime] = None

        self.output_tokens_limit: Optional[int] = None
        self.output_tokens_remaining: Optional[int] = None
        self.output_tokens_reset_time: Optional[datetime] = None

        self.last_retry_after: Optional[float] = None

    async def acquire(self):
        async with self.lock:
            now = time.time()

            if now >= self.reset_time_rpm:
                self.reset_time_rpm = now + 60
                self.request_count_rpm = 0

            if now >= self.reset_time_rph:
                self.reset_time_rph = now + 3600
                self.request_count_rph = 0

            # If rate limits exceeded, wait for cooldown_period or last_retry_after if set
            if (self.request_count_rpm >= self.max_rpm) or (self.request_count_rph >= self.max_rph):
                wait_time = self.last_retry_after or self.cooldown_period
                await asyncio.sleep(wait_time)
                now2 = time.time()
                self.reset_time_rpm = now2 + 60
                self.reset_time_rph = now2 + 3600
                self.request_count_rpm = 0
                self.request_count_rph = 0

            self.request_count_rpm += 1
            self.request_count_rph += 1

    async def update_from_anthropic_headers(self, headers: Dict[str, Any]):
        async with self.lock:
            # Update requests-related data
            self.requests_limit = self._safe_int(headers.get('anthropic-ratelimit-requests-limit'))
            self.requests_remaining = self._safe_int(headers.get('anthropic-ratelimit-requests-remaining'))
            self.requests_reset_time = self._parse_datetime(headers.get('anthropic-ratelimit-requests-reset'))

            # Update tokens-related data
            self.tokens_limit = self._safe_int(headers.get('anthropic-ratelimit-tokens-limit'))
            self.tokens_remaining = self._safe_int(headers.get('anthropic-ratelimit-tokens-remaining'))
            self.tokens_reset_time = self._parse_datetime(headers.get('anthropic-ratelimit-tokens-reset'))

            self.input_tokens_limit = self._safe_int(headers.get('anthropic-ratelimit-input-tokens-limit'))
            self.input_tokens_remaining = self._safe_int(headers.get('anthropic-ratelimit-input-tokens-remaining'))
            self.input_tokens_reset_time = self._parse_datetime(headers.get('anthropic-ratelimit-input-tokens-reset'))

            self.output_tokens_limit = self._safe_int(headers.get('anthropic-ratelimit-output-tokens-limit'))
            self.output_tokens_remaining = self._safe_int(headers.get('anthropic-ratelimit-output-tokens-remaining'))
            self.output_tokens_reset_time = self._parse_datetime(headers.get('anthropic-ratelimit-output-tokens-reset'))

            # Check for Retry-After header for special wait times
            retry_after = headers.get('retry-after')
            if retry_after:
                try:
                    self.last_retry_after = float(retry_after)
                except ValueError:
                    self.last_retry_after = None

    def get_current_limits(self) -> Dict[str, Any]:
        return {
            "local_usage": {
                "max_rpm": self.max_rpm,
                "max_rph": self.max_rph,
                "current_rpm": self.request_count_rpm,
                "current_rph": self.request_count_rph,
                "reset_time_rpm": self.reset_time_rpm,
                "reset_time_rph": self.reset_time_rph,
                "cooldown_period": self.cooldown_period,
                "last_retry_after": self.last_retry_after,
            },
            "anthropic_usage": {
                "requests_limit": self.requests_limit,
                "requests_remaining": self.requests_remaining,
                "requests_reset_time": self.requests_reset_time.isoformat() if self.requests_reset_time else None,
                "tokens_limit": self.tokens_limit,
                "tokens_remaining": self.tokens_remaining,
                "tokens_reset_time": self.tokens_reset_time.isoformat() if self.tokens_reset_time else None,
                "input_tokens_limit": self.input_tokens_limit,
                "input_tokens_remaining": self.input_tokens_remaining,
                "input_tokens_reset_time": self.input_tokens_reset_time.isoformat() if self.input_tokens_reset_time else None,
                "output_tokens_limit": self.output_tokens_limit,
                "output_tokens_remaining": self.output_tokens_remaining,
                "output_tokens_reset_time": self.output_tokens_reset_time.isoformat() if self.output_tokens_reset_time else None,
            }
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

# Instantiate a global RateLimiter
rate_limiter_instance = RateLimiter()
