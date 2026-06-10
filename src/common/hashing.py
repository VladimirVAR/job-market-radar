"""Stable hashing helpers for raw payload lineage."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json_dumps(payload: Any) -> str:
    """Serialize JSON-like data deterministically for hashing.

    The same logical payload should produce the same string even if dictionary
    key order differs.
    """

    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def sha256_text(value: str) -> str:
    """Return SHA-256 hex digest for UTF-8 text."""

    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def stable_json_hash(payload: Any) -> str:
    """Return a stable SHA-256 hash for a JSON-like payload."""

    return sha256_text(canonical_json_dumps(payload))
