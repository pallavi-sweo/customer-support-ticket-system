from __future__ import annotations

import functools
import logging
import time
from typing import Any, Callable, TypeVar, ParamSpec

P = ParamSpec("P")
R = TypeVar("R")


def timed(
    logger_name: str = "app.timing", threshold_ms: int = 50
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Measures execution time and logs if duration >= threshold_ms.
    Useful for spotting slow endpoints/DB calls early.
    """
    logger = logging.getLogger(logger_name)

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            if elapsed_ms >= threshold_ms:
                logger.info("slow_call func=%s elapsed_ms=%s", func.__name__, elapsed_ms)
            return result

        return wrapper

    return decorator


def log_call(logger_name: str = "app.calls") -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Logs function entry/exit. Keep it for key service/CRUD methods (not everything).
    """
    logger = logging.getLogger(logger_name)

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            logger.debug("enter func=%s", func.__name__)
            result = func(*args, **kwargs)
            logger.debug("exit func=%s", func.__name__)
            return result

        return wrapper

    return decorator


def db_timed(threshold_ms: int = 25) -> Callable[[Callable[P, R]], Callable[P, R]]:
    return timed(logger_name="app.db", threshold_ms=threshold_ms)
