"""Loader for raw job posting tables.

Grain: one raw job posting payload per source job per request per batch.
Supports multiple sources via an allowlist of known target tables.
"""

from __future__ import annotations

from typing import Any, Iterable
from uuid import uuid4

from src.common.database import jsonb
from src.common.dates import utc_now
from src.common.hashing import stable_json_hash
from src.ingestion.france_travail.parser import RawJobPayload


_RAW_JOB_TABLES: dict[str, str] = {
    "france_travail": "raw.raw_france_travail_job_postings",
    "adzuna": "raw.raw_adzuna_job_postings",
}


def build_source_job_key(source_name: str, source_job_id: str) -> str:
    """Build the stable source-level job key required by the raw contract."""

    return f"{source_name}:{source_job_id}"


def build_payload_hash(raw_payload: dict[str, Any]) -> str:
    """Build a stable hash of the raw job payload."""

    return stable_json_hash(raw_payload)


def insert_raw_job_postings(
    connection: Any,
    batch_id: str,
    request_id: str,
    search_scope_key: str,
    raw_jobs: Iterable[RawJobPayload],
    source_name: str = "france_travail",
) -> int:
    """Insert raw job payloads and return inserted row count.

    Dispatches to the correct raw table based on source_name.
    This function intentionally extracts only technical lineage fields.
    """

    target_table = _RAW_JOB_TABLES.get(source_name)
    if target_table is None:
        known = list(_RAW_JOB_TABLES)
        raise ValueError(f"Unknown source_name: {source_name!r}. Known sources: {known}")

    rows = []
    now = utc_now()
    for raw_job in raw_jobs:
        source_job_id = str(raw_job.source_job_id)
        rows.append(
            (
                str(uuid4()),
                batch_id,
                request_id,
                source_name,
                source_job_id,
                build_source_job_key(source_name, source_job_id),
                search_scope_key,
                jsonb(raw_job.raw_payload),
                build_payload_hash(raw_job.raw_payload),
                now,
                now,
            )
        )

    if not rows:
        return 0

    with connection.cursor() as cursor:
        cursor.executemany(
            f"""
            insert into {target_table} (
                raw_job_posting_id,
                batch_id,
                request_id,
                source_name,
                source_job_id,
                source_job_key,
                search_scope_key,
                raw_payload_json,
                payload_hash,
                ingested_at,
                created_at
            )
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            rows,
        )
    connection.commit()
    return len(rows)
