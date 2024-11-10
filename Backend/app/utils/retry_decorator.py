# app/utils/retry_decorator.py

import asyncio
from functools import wraps
from typing import Callable, Type, Tuple
import time

def retry(
    max_retries: int = 3,
    initial_wait: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[BaseException], ...] = (Exception,)
) -> Callable:
    """
    Decorator to retry an asynchronous function upon specified exceptions.

    Args:
        max_retries (int): Maximum number of retries.
        initial_wait (float): Initial wait time between retries.
        backoff_factor (float): Multiplier for wait time after each retry.
        exceptions (Tuple[Type[BaseException], ...]): Exceptions to trigger a retry.

    Returns:
        Callable: Wrapped function with retry logic.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            wait = initial_wait
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries >= max_retries:
                        raise e
                    await asyncio.sleep(wait)
                    wait *= backoff_factor
        return wrapper
    return decorator
