"""Source-specific parser for Adzuna API responses.

The parser extracts raw job records and technical identifiers only. It must not
perform analytical transformations such as skill extraction, seniority inference,
contract normalization, or relevance scoring.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class AdzunaParseError(ValueError):
    """Raised when an Adzuna payload cannot be parsed as expected."""


@dataclass(frozen=True)
class RawJobPayload:
    """Raw job payload plus source-level technical identifiers."""

    source_job_id: str
    raw_payload: dict[str, Any]
    source_url: str | None = None


def extract_job_records(response_payload: dict[str, Any] | list[Any] | None) -> list[dict[str, Any]]:
    """Extract raw job posting objects from an Adzuna response.

    Adzuna search responses contain a `results` list at the top level.
    """

    if response_payload is None:
        return []

    if isinstance(response_payload, list):
        return [item for item in response_payload if isinstance(item, dict)]

    if not isinstance(response_payload, dict):
        raise AdzunaParseError(
            f"Expected dict/list response payload, got {type(response_payload).__name__}"
        )

    candidates = response_payload.get("results")
    if candidates is None:
        candidates = response_payload.get("jobs") or response_payload.get("data") or []

    if not isinstance(candidates, list):
        raise AdzunaParseError("Expected job records container to be a list")

    return [item for item in candidates if isinstance(item, dict)]


def extract_source_job_id(job_payload: dict[str, Any]) -> str:
    """Extract Adzuna source job id from a raw job payload."""

    for key in ("id", "source_job_id"):
        value = job_payload.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()

    raise AdzunaParseError("Adzuna job payload does not contain a source job id")


def extract_source_url(job_payload: dict[str, Any]) -> str | None:
    """Best-effort extraction of source URL without analytical transformation."""

    for key in ("redirect_url", "url", "source_url"):
        value = job_payload.get(key)
        if value:
            return str(value)

    return None


def parse_raw_job_payloads(response_payload: dict[str, Any] | list[Any] | None) -> list[RawJobPayload]:
    """Return raw job objects with only source-level metadata extracted."""

    raw_jobs: list[RawJobPayload] = []
    for job_record in extract_job_records(response_payload):
        raw_jobs.append(
            RawJobPayload(
                source_job_id=extract_source_job_id(job_record),
                source_url=extract_source_url(job_record),
                raw_payload=job_record,
            )
        )
    return raw_jobs
