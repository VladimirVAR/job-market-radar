"""Loader for raw.raw_load_batches.

Grain: one row per pipeline execution.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from src.common.dates import utc_now


VALID_FINAL_STATUSES = {"success", "failed", "partial_success"}


def create_load_batch(
    connection: Any,
    source_name: str,
    pipeline_name: str,
    triggered_by: str = "manual",
) -> str:
    """Create one raw load-batch row and return its batch_id.

    The pipeline must call this before making API requests.
    """

    batch_id = str(uuid4())
    now = utc_now()
    with connection.cursor() as cursor:
        cursor.execute(
            """
            insert into raw.raw_load_batches (
                batch_id,
                source_name,
                pipeline_name,
                started_at,
                finished_at,
                status,
                triggered_by,
                records_loaded,
                requests_made,
                error_message,
                created_at
            )
            values (%s, %s, %s, %s, null, %s, %s, %s, %s, null, %s)
            """,
            (
                batch_id,
                source_name,
                pipeline_name,
                now,
                "running",
                triggered_by,
                0,
                0,
                now,
            ),
        )
    connection.commit()
    return batch_id


def mark_batch_finished(
    connection: Any,
    batch_id: str,
    status: str,
    records_loaded: int,
    requests_made: int,
    error_message: str | None = None,
    finished_at: datetime | None = None,
) -> None:
    """Mark an existing batch as success, partial_success, or failed."""

    if status not in VALID_FINAL_STATUSES:
        raise ValueError(f"Invalid final batch status: {status}")

    with connection.cursor() as cursor:
        cursor.execute(
            """
            update raw.raw_load_batches
            set
                finished_at = %s,
                status = %s,
                records_loaded = %s,
                requests_made = %s,
                error_message = %s
            where batch_id = %s
            """,
            (
                finished_at or utc_now(),
                status,
                records_loaded,
                requests_made,
                error_message,
                batch_id,
            ),
        )
        if cursor.rowcount != 1:
            raise RuntimeError(f"Could not update raw.raw_load_batches for batch_id={batch_id}")
    connection.commit()


def mark_batch_failed(
    connection: Any,
    batch_id: str,
    error_message: str,
    records_loaded: int = 0,
    requests_made: int = 0,
) -> None:
    """Convenience wrapper for failed batches."""

    mark_batch_finished(
        connection=connection,
        batch_id=batch_id,
        status="failed",
        records_loaded=records_loaded,
        requests_made=requests_made,
        error_message=error_message,
    )
