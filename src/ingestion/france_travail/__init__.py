"""France Travail ingestion client package."""

from .auth import FranceTravailAuthenticator, FranceTravailCredentials
from .client import FranceTravailApiResponse, FranceTravailClient
from .parser import RawJobPayload, parse_raw_job_payloads
from .request_builder import (
    SearchRequest,
    SearchScope,
    build_paginated_search_requests,
    build_requests_for_scopes,
)

__all__ = [
    "FranceTravailAuthenticator",
    "FranceTravailCredentials",
    "FranceTravailApiResponse",
    "FranceTravailClient",
    "RawJobPayload",
    "parse_raw_job_payloads",
    "SearchRequest",
    "SearchScope",
    "build_paginated_search_requests",
    "build_requests_for_scopes",
]
