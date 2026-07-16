"""Shared utilities: logging setup and a simple timing context manager."""

from __future__ import annotations

import logging
import time
from types import TracebackType


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Return a configured logger that writes to stderr exactly once.

    Args:
        name: Logger name (usually ``__name__``).
        level: Logging level.

    Returns:
        A ``logging.Logger`` with a single stream handler.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        )
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


class Timer:
    """Context manager measuring wall-clock time in seconds via ``perf_counter``.

    Usage:
        >>> with Timer() as t:
        ...     do_work()
        >>> t.elapsed  # seconds (float)
    """

    def __init__(self) -> None:
        self.start: float = 0.0
        self.elapsed: float = 0.0

    def __enter__(self) -> Timer:
        self.start = time.perf_counter()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        self.elapsed = time.perf_counter() - self.start
        return False
