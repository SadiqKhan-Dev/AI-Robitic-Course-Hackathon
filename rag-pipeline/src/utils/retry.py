"""Retry logic with exponential backoff."""

import asyncio
import random
from typing import Callable, TypeVar, Optional

import structlog

logger = structlog.get_logger(__name__)

T = TypeVar("T")


async def retry_with_exponential_backoff(
    func: Callable[..., T],
    *args,
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: float = 0.1,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    **kwargs,
) -> T:
    """Retry an async function with exponential backoff and jitter.

    Args:
        func: Async function to retry
        *args: Positional arguments for func
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        jitter: Random jitter factor (0-1) as fraction of delay
        exceptions: Tuple of exception types to catch and retry
        **kwargs: Keyword arguments for func

    Returns:
        Result of func call

    Raises:
        Last exception if all retries exhausted
    """
    last_exception: Optional[Exception] = None

    for attempt in range(max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except exceptions as e:
            last_exception = e

            if attempt == max_retries:
                logger.error(
                    "retry_exhausted",
                    func_name=func.__name__,
                    attempts=attempt + 1,
                    error=str(e),
                )
                raise

            # Calculate delay with exponential backoff and jitter
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter_amount = delay * jitter * random.random()
            total_delay = delay + jitter_amount

            logger.warning(
                "retry_attempt",
                func_name=func.__name__,
                attempt=attempt + 1,
                max_retries=max_retries,
                delay_seconds=total_delay,
                error=str(e),
            )

            await asyncio.sleep(total_delay)

    # Should not reach here, but satisfy type checker
    if last_exception:
        raise last_exception
    raise Exception("Unexpected retry state")


def create_retry_policy(
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
) -> dict:
    """Create a retry policy dictionary for configuration.

    Args:
        max_retries: Maximum retry attempts
        base_delay: Initial delay between retries
        max_delay: Maximum delay between retries

    Returns:
        Dictionary containing retry policy settings
    """
    return {
        "max_retries": max_retries,
        "base_delay": base_delay,
        "max_delay": max_delay,
    }
