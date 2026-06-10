"""Date/time helpers for ingestion pipelines."""

from __future__ import annotations

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return the current timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    """Return the current UTC timestamp as ISO 8601 text."""

    return utc_now().isoformat()
