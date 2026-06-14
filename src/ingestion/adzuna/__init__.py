"""Adzuna ingestion package public API."""

from .auth import AdzunaAuthError, AdzunaCredentials
from .client import AdzunaApiResponse, AdzunaClient
from .parser import RawJobPayload, parse_raw_job_payloads
from .request_builder import SearchRequest, SearchScope, build_requests_for_scopes

__all__ = [
    "AdzunaAuthError",
    "AdzunaCredentials",
    "AdzunaApiResponse",
    "AdzunaClient",
    "RawJobPayload",
    "parse_raw_job_payloads",
    "SearchRequest",
    "SearchScope",
    "build_requests_for_scopes",
]
