"""Request builders for France Travail job-search API.

This module owns source-specific query parameters and pagination mechanics.
It does not call the API and does not load data into the database.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import re
from typing import Any, Iterable


SOURCE_NAME = "france_travail"
DEFAULT_PAGE_SIZE = 150
MAX_PAGE_SIZE = 150
MAX_RANGE_START = 1000
MAX_RANGE_END = 1149
PAGINATION_KEY = "range"


class FranceTravailRequestError(ValueError):
    """Raised when a France Travail request cannot be built safely."""


@dataclass(frozen=True)
class SearchRequest:
    """A single France Travail search request/page."""

    endpoint: str
    params: dict[str, Any]
    search_scope_key: str
    page_number: int | None = None
    page_size: int | None = None


@dataclass(frozen=True)
class SearchScope:
    """Comparable France Travail search scope.

    Pagination is intentionally not part of the scope identity. The same search
    scope can produce multiple API pages.
    """

    keywords: str
    location: str | None = None
    contract_type: str | None = None
    remote: str | None = None
    extra_params: dict[str, Any] = field(default_factory=dict)

    def to_base_params(self) -> dict[str, Any]:
        """Convert the search scope to France Travail API params.

        This keeps API parameter names source-specific, for example `motsCles`.
        """

        params: dict[str, Any] = {"motsCles": self.keywords}
        if self.location:
            # `location` can be a commune, department, or caller-provided field.
            # For MVP, pass it as a generic location filter only when configured.
            # A later refinement can split it into commune/departement/pays.
            params["commune"] = self.location
        if self.contract_type:
            params["typeContrat"] = self.contract_type
        if self.remote:
            params["teletravail"] = self.remote

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

    Pagination parameters are excluded because pages belong to the same search
    scope. The readable prefix helps debugging, while the hash prevents very
    long keys when many filters are configured.
    """

    comparable_params = {
        key: params[key]
        for key in sorted(params)
        if key not in {PAGINATION_KEY, "page", "pageNumber", "pageSize"}
    }
    canonical = json.dumps(comparable_params, ensure_ascii=False, sort_keys=True, default=str)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]

    keyword_part = _slugify(comparable_params.get("motsCles", "any_keywords"))
    location_part = _slugify(
        comparable_params.get("commune")
        or comparable_params.get("departement")
        or comparable_params.get("lieu")
        or "any_location"
    )
    return f"{source_name}:{keyword_part}:{location_part}:{digest}"


def build_range_param(page_number: int, page_size: int = DEFAULT_PAGE_SIZE) -> str:
    """Build France Travail `range` pagination parameter.

    France Travail Offres d'emploi v2 historically supports ranges of up to
    150 records per request and up to 0-1149 total window for a broad search.
    """

    if page_number < 1:
        raise FranceTravailRequestError("page_number must be >= 1")
    if page_size < 1 or page_size > MAX_PAGE_SIZE:
        raise FranceTravailRequestError(f"page_size must be between 1 and {MAX_PAGE_SIZE}")

    start = (page_number - 1) * page_size
    end = start + page_size - 1

    if start > MAX_RANGE_START or end > MAX_RANGE_END:
        raise FranceTravailRequestError(
            f"France Travail pagination range {start}-{end} exceeds MVP safety limit "
            f"{MAX_RANGE_START}-{MAX_RANGE_END}. Narrow the search scope instead."
        )

    return f"{start}-{end}"


def build_search_request(
    params: dict[str, Any],
    page_number: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
    endpoint: str = "/offres/search",
    source_name: str = SOURCE_NAME,
) -> SearchRequest:
    """Build one paginated search request."""

    base_params = _drop_empty_values(dict(params))
    search_scope_key = build_search_scope_key(source_name, base_params)
    request_params = dict(base_params)
    request_params[PAGINATION_KEY] = build_range_param(page_number, page_size)

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
    endpoint: str = "/offres/search",
    source_name: str = SOURCE_NAME,
) -> list[SearchRequest]:
    """Build multiple page requests for the same comparable search scope."""

    if max_pages < 1:
        raise FranceTravailRequestError("max_pages must be >= 1")

    return [
        build_search_request(
            params=params,
            page_number=page_number,
            page_size=page_size,
            endpoint=endpoint,
            source_name=source_name,
        )
        for page_number in range(1, max_pages + 1)
    ]


def build_requests_for_scopes(
    scopes: Iterable[SearchScope],
    max_pages: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> list[SearchRequest]:
    """Build requests for multiple configured search scopes."""

    requests: list[SearchRequest] = []
    for scope in scopes:
        requests.extend(
            build_paginated_search_requests(
                params=scope.to_base_params(),
                max_pages=max_pages,
                page_size=page_size,
            )
        )
    return requests
