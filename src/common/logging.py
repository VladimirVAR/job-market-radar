"""Project logging helpers.

The file name follows the repository structure from Task 001. Internally we
import the standard-library module under an alias to avoid confusion.
"""

from __future__ import annotations

import logging as py_logging
import os


def configure_logging(level: str | None = None) -> None:
    """Configure simple console logging for local pipeline runs."""

    resolved_level = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    py_logging.basicConfig(
        level=getattr(py_logging, resolved_level, py_logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def get_logger(name: str) -> py_logging.Logger:
    """Return a standard Python logger."""

    return py_logging.getLogger(name)
