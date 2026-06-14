"""Adzuna API client.

The client isolates source-specific HTTP logic and returns raw payloads plus
request metadata. It does not write to PostgreSQL and does not transform
business fields. Raw loading belongs to src/loaders.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import os
import time
from typing import Any
from urllib.parse import urljoin

import requests

from .auth import AdzunaCredentials
from .request_builder import SearchRequest


DEFAULT_BASE_URL = "https://api.adzuna.com/v1/api/jobs"
DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_SECONDS = 1.0
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class AdzunaClientError(RuntimeError):
    """Raised when the Adzuna client cannot complete a request."""


@dataclass(frozen=True)
class AdzunaApiResponse:
    """Response payload plus request metadata for raw loaders."""

    source_name: str
    endpoint: str
    http_method: str
    request_url: str
    request_params: dict[str, Any]
    search_scope_key: str | None
    page_number: int | None
    page_size: int | None
    response_status_code: int | None
    response_time_ms: int | None
    response_headers: dict[str, Any]
    response_payload: dict[str, Any] | list[Any] | None
    content_range: dict[str, int | None]
    started_at: str
    finished_at: str
    error_message: str | None

    def to_request_metadata(self) -> dict[str, Any]:
        """Return a serializable dict suitable for raw request loaders."""

        return asdict(self)


class AdzunaClient:
    """Source-specific client for Adzuna job-search API."""

    def __init__(
        self,
        credentials: AdzunaCredentials | None = None,
        base_url: str | None = None,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_seconds: float = DEFAULT_BACKOFF_SECONDS,
        source_name: str = "adzuna",
    ) -> None:
        self.credentials = credentials or AdzunaCredentials.from_env()
        self.base_url = (base_url or os.getenv("ADZUNA_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self.source_name = source_name

    def send_search_request(self, request: SearchRequest) -> AdzunaApiResponse:
        """Send a pre-built search request."""

        return self._send_request(
            endpoint=request.endpoint,
            params=request.params,
            search_scope_key=request.search_scope_key,
            page_number=request.page_number,
            page_size=request.page_size,
        )

    def _send_request(
        self,
        endpoint: str,
        params: dict[str, Any],
        search_scope_key: str | None,
        page_number: int | None,
        page_size: int | None,
    ) -> AdzunaApiResponse:
        """Send GET request with retry handling and metadata capture."""

        endpoint_path = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        request_url = urljoin(f"{self.base_url}/", endpoint_path.lstrip("/"))

        # Inject auth params — never stored in DB (raw_job_loader strips them)
        auth_params = self.credentials.as_query_params()
        full_params = {**auth_params, **params}

        # Strip auth from stored metadata
        safe_params = {k: v for k, v in params.items()}

        started_at_dt = datetime.now(timezone.utc)
        started_at = started_at_dt.isoformat()
        response_payload: dict[str, Any] | list[Any] | None = None
        response_headers: dict[str, Any] = {}
        status_code: int | None = None
        response_time_ms: int | None = None
        error_message: str | None = None

        for attempt in range(1, self.max_retries + 1):
            perf_start = time.perf_counter()
            try:
                response = requests.get(
                    request_url,
                    params=full_params,
                    headers={"Accept": "application/json"},
                    timeout=self.timeout_seconds,
                )
                response_time_ms = int((time.perf_counter() - perf_start) * 1000)
                status_code = response.status_code
                response_headers = _safe_headers(dict(response.headers))

                if response.status_code in RETRYABLE_STATUS_CODES and attempt < self.max_retries:
                    time.sleep(self.backoff_seconds * attempt)
                    continue

                if response.content:
                    try:
                        response_payload = response.json()
                    except ValueError:
                        response_payload = None
                        error_message = "Response body is not valid JSON"
                else:
                    response_payload = None

                if response.status_code >= 400:
                    body_preview = response.text[:500] if response.text else ""
                    error_message = f"Adzuna API returned HTTP {response.status_code}: {body_preview}"
                break

            except requests.Timeout as exc:
                response_time_ms = int((time.perf_counter() - perf_start) * 1000)
                error_message = f"Adzuna API timeout: {exc}"
                if attempt < self.max_retries:
                    time.sleep(self.backoff_seconds * attempt)
                    continue
            except requests.RequestException as exc:
                response_time_ms = int((time.perf_counter() - perf_start) * 1000)
                error_message = f"Adzuna API request failed: {exc}"
                if attempt < self.max_retries:
                    time.sleep(self.backoff_seconds * attempt)
                    continue

        finished_at = datetime.now(timezone.utc).isoformat()
        return AdzunaApiResponse(
            source_name=self.source_name,
            endpoint=endpoint_path,
            http_method="GET",
            request_url=request_url,
            request_params=safe_params,
            search_scope_key=search_scope_key,
            page_number=page_number,
            page_size=page_size,
            response_status_code=status_code,
            response_time_ms=response_time_ms,
            response_headers=response_headers,
            response_payload=response_payload,
            content_range={"first_index": None, "last_index": None, "total_results": None},
            started_at=started_at,
            finished_at=finished_at,
            error_message=error_message,
        )


def _safe_headers(headers: dict[str, Any]) -> dict[str, Any]:
    """Remove potentially sensitive headers before metadata persistence."""

    blocked = {"authorization", "proxy-authorization", "cookie", "set-cookie"}
    return {key: value for key, value in headers.items() if key.lower() not in blocked}
