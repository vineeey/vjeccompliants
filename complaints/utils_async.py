from __future__ import annotations

import threading
import logging
from typing import Callable, Any


logger = logging.getLogger(__name__)


def run_in_background(func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
    """Run a callable in a daemon thread, swallowing exceptions with logging.

    Designed for short, non-critical background tasks in dev/small deployments.
    For production, prefer a proper task queue (e.g., Celery, RQ, Huey).
    """

    def _wrapper():
        try:
            func(*args, **kwargs)
        except Exception:  # pragma: no cover - background safety
            logger.exception("Background task failed: %s", getattr(func, "__name__", func))

    t = threading.Thread(target=_wrapper, daemon=True)
    t.start()
