import asyncio
import logging
import time
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)


def report_crash(t, logger):
    try:
        exc = t.exception()
    except asyncio.CancelledError:
        return
    if exc is None:
        return
    if isinstance(exc, asyncio.CancelledError):
        return
    logger.error("crashed %s: %s", type(exc).__name__, exc, exc_info=(type(exc), exc, exc.__traceback__))


_throttle_dict: Dict[str, float] = {}


def log_with_throttle(
    log_func: Callable[..., None],
    message: str,
    *args: Any,
    interval_seconds: float = 30.0
) -> None:
    now = time.time()
    if message not in _throttle_dict or now - _throttle_dict[message] > interval_seconds:
        _throttle_dict[message] = now
        log_func(message, *args)


def truncate_middle(text: str, max_length: int = 5000) -> str:
    if len(text) <= max_length:
        return text
    keep_chars = max_length // 2
    return text[:keep_chars] + "\n...\n" + text[-keep_chars:]
