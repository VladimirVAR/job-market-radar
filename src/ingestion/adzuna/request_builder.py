"""Request builders for Adzuna job-search API.

This module owns source-specific query parameters and pagination mechanics.
It does not call the API and does not load data into the database.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import re
from typing import Any, Iterable


SOURCE_NAME = "adzuna"
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 50
DEFAULT_COUNTRY = "fr"


class AdzunaRequestError(ValueError):
    """Raised when an Adzuna request cannot be built safely."""


@dataclass(frozen=True)
class SearchRequest:
    """A single Adzuna search request/page."""

    endpoint: str
    params: dict[str, Any]
    search_scope_key: str
    page_number: int | None = None
    page_size: int | None = None


@dataclass(frozen=True)
class SearchScope:
    """Comparable Adzuna search scope.

    Pagination is intentionally not part of the scope identity.
    """

    keywords: str
    location: str | None = None
    contract_type: str | None = None
    remote: str | None = None
    extra_params: dict[str, Any] = field(default_factory=dict)

    def to_base_params(self) -> dict[str, Any]:
        """Convert the search scope to Adzuna API query params."""

        params: dict[str, Any] = {"what": self.keywords}
        if self.location:
            params["where"] = self.location
        if self.contract_type:
            # Adzuna: full_time, part_time, permanent, contract
            params["contract_type"] = self.contract_type
        if self.remote:
            params["title_only"] = self.remote

        params.update(self.extra_params)
        return _drop_empty_values(params)


def _drop_empty_values(params: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in params.items()
        if value is not None and value != "" and value != [] and value != {}
    }


def _slugify(value: Any) -> str:
    text = str(value).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "any"


def build_search_scope_key(source_name: str, params: dict[str, Any]) -> str:
    """Build a stable comparable search-scope key.

    Pagination parameters are excluded because pages belong to the same scope.
    """

    comparable_params = {
        key: params[key]
        for key in sorted(params)
        if key not in {"page", "results_per_page", "page_number", "page_size"}
    }
    canonical = json.dumps(comparable_params, ensure_ascii=False, sort_keys=True, default=str)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]

    keyword_part = _slugify(comparable_params.get("what", "any_keywords"))
    location_part = _slugify(comparable_params.get("where", "any_location"))
    return f"{source_name}:{keyword_part}:{location_part}:{digest}"


def build_search_request(
    params: dict[str, Any],
    page_number: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
    country: str = DEFAULT_COUNTRY,
    source_name: str = SOURCE_NAME,
) -> SearchRequest:
    """Build one paginated Adzuna search request.

    Adzuna pagination: page number is part of the URL path, not a query param.
    Endpoint pattern: /{country}/search/{page}
    """

    if page_number < 1:
        raise AdzunaRequestError("page_number must be >= 1")
    if page_size < 1 or page_size > MAX_PAGE_SIZE:
        raise AdzunaRequestError(f"page_size must be between 1 and {MAX_PAGE_SIZE}")

    base_params = _drop_empty_values(dict(params))
    search_scope_key = build_search_scope_key(source_name, base_params)

    request_params = dict(base_params)
    request_params["results_per_page"] = page_size

    endpoint = f"/{country}/search/{page_number}"

    return SearchRequest(
        endpoint=endpoint,
        params=request_params,
        search_scope_key=search_scope_key,
        page_number=page_number,
        page_size=page_size,
    )


def build_paginated_search_requests(
    params: dict[str, Any],
    max_pages: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
    country: str = DEFAULT_COUNTRY,
    source_name: str = SOURCE_NAME,
) -> list[SearchRequest]:
    """Build multiple page requests for the same comparable search scope."""

    if max_pages < 1:
        raise AdzunaRequestError("max_pages must be >= 1")

    return [
        build_search_request(
            params=params,
            page_number=page_number,
            page_size=page_size,
            country=country,
            source_name=source_name,
        )
        for page_number in range(1, max_pages + 1)
    ]


def build_requests_for_scopes(
    scopes: Iterable[SearchScope],
    max_pages: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
    country: str = DEFAULT_COUNTRY,
) -> list[SearchRequest]:
    """Build requests for multiple configured search scopes."""

    requests: list[SearchRequest] = []
    for scope in scopes:
        requests.extend(
            build_paginated_search_requests(
                params=scope.to_base_params(),
                max_pages=max_pages,
                page_size=page_size,
                country=country,
            )
        )
    return requests
