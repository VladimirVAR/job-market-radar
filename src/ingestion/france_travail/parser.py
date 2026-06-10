"""Source-specific parser for France Travail API responses.

The parser extracts raw job records and technical identifiers only. It must not
perform analytical transformations such as skill extraction, seniority inference,
contract normalization, or relevance scoring.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any


class FranceTravailParseError(ValueError):
    """Raised when a France Travail payload cannot be parsed as expected."""


@dataclass(frozen=True)
class RawJobPayload:
    """Raw job payload plus source-level technical identifiers."""

    source_job_id: str
    raw_payload: dict[str, Any]
    source_url: str | None = None


def extract_job_records(response_payload: dict[str, Any] | list[Any] | None) -> list[dict[str, Any]]:
    """Extract raw job posting objects from a France Travail response.

    The expected search response contains a `resultats` list. Fallbacks are kept
    intentionally conservative to support minor API shape differences or test
    fixtures without deeply transforming the data.
    """

    if response_payload is None:
        return []

    if isinstance(response_payload, list):
        return [item for item in response_payload if isinstance(item, dict)]

    if not isinstance(response_payload, dict):
        raise FranceTravailParseError(
            f"Expected dict/list response payload, got {type(response_payload).__name__}"
        )

    candidates = response_payload.get("resultats")
    if candidates is None:
        candidates = response_payload.get("results") or response_payload.get("offres") or []

    if not isinstance(candidates, list):
        raise FranceTravailParseError("Expected job records container to be a list")

    return [item for item in candidates if isinstance(item, dict)]


def extract_source_job_id(job_payload: dict[str, Any]) -> str:
    """Extract France Travail source job id from a raw job payload."""

    for key in ("id", "identifiant", "source_job_id"):
        value = job_payload.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()

    raise FranceTravailParseError("France Travail job payload does not contain a source job id")


def extract_source_url(job_payload: dict[str, Any]) -> str | None:
    """Best-effort extraction of source URL without analytical transformation."""

    direct_url = job_payload.get("url") or job_payload.get("source_url") or job_payload.get("urlOrigine")
    if direct_url:
        return str(direct_url)

    origine_offre = job_payload.get("origineOffre")
    if isinstance(origine_offre, dict):
        nested_url = origine_offre.get("urlOrigine") or origine_offre.get("url")
        if nested_url:
            return str(nested_url)

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


def parse_content_range(content_range: str | None) -> dict[str, int | None]:
    """Parse Content-Range metadata when returned by the API.

    Supports common forms such as `offres 0-149/1234` and `0-149/1234`.
    """

    if not content_range:
        return {"first_index": None, "last_index": None, "total_results": None}

    match = re.search(r"(\d+)\s*-\s*(\d+)\s*/\s*(\d+|\*)", content_range)
    if not match:
        return {"first_index": None, "last_index": None, "total_results": None}

    total_raw = match.group(3)
    return {
        "first_index": int(match.group(1)),
        "last_index": int(match.group(2)),
        "total_results": None if total_raw == "*" else int(total_raw),
    }
