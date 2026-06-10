"""Loader for raw.raw_api_requests.

Grain: one row per API request, page, or search parameter set.
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from src.common.database import jsonb
from src.common.dates import utc_now


def insert_api_request(
    connection: Any,
    batch_id: str,
    request_metadata: dict[str, Any],
) -> str:
    """Persist one API request metadata row and return request_id.

    Sensitive headers must already be removed by the API client.
    """

    request_id = str(uuid4())
    with connection.cursor() as cursor:
        cursor.execute(
            """
            insert into raw.raw_api_requests (
                request_id,
                batch_id,
                source_name,
                endpoint,
                http_method,
                request_url,
                request_params_json,
                search_scope_key,
                page_number,
                page_size,
                response_status_code,
                response_time_ms,
                response_headers_json,
                started_at,
                finished_at,
                error_message,
                created_at
            )
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                request_id,
                batch_id,
                request_metadata.get("source_name", "france_travail"),
                request_metadata.get("endpoint"),
                request_metadata.get("http_method", "GET"),
                request_metadata.get("request_url"),
                jsonb(request_metadata.get("request_params") or {}),
                request_metadata.get("search_scope_key"),
                request_metadata.get("page_number"),
                request_metadata.get("page_size"),
                request_metadata.get("response_status_code"),
                request_metadata.get("response_time_ms"),
                jsonb(request_metadata.get("response_headers") or {}),
                request_metadata.get("started_at") or utc_now(),
                request_metadata.get("finished_at") or utc_now(),
                request_metadata.get("error_message"),
                utc_now(),
            ),
        )
    connection.commit()
    return request_id
