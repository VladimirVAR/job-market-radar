"""Run Adzuna raw ingestion.

    python -m src.pipeline.run_adzuna_ingestion

The pipeline creates one load batch, stores every API request metadata row, and
stores raw job payloads as JSONB. It intentionally stops at the raw layer.

Sample mode is enabled by default (ADZUNA_SAMPLE_MODE=true) until real
ADZUNA_APP_ID and ADZUNA_APP_KEY credentials are configured.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from src.common.config import AdzunaIngestionConfig, DatabaseConfig
from src.common.database import get_connection
from src.common.logging import configure_logging, get_logger
from src.ingestion.adzuna import (
    AdzunaApiResponse,
    AdzunaClient,
    SearchRequest,
    SearchScope,
    build_requests_for_scopes,
    parse_raw_job_payloads,
)
from src.loaders.batch_loader import create_load_batch, mark_batch_failed, mark_batch_finished
from src.loaders.raw_job_loader import insert_raw_job_postings
from src.loaders.request_loader import insert_api_request

LOGGER = get_logger(__name__)


@dataclass(frozen=True)
class IngestionSummary:
    """Execution summary returned by the raw ingestion pipeline."""

    batch_id: str
    status: str
    requests_made: int
    successful_requests: int
    failed_requests: int
    records_loaded: int
    error_message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "status": self.status,
            "requests_made": self.requests_made,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "records_loaded": self.records_loaded,
            "error_message": self.error_message,
        }


def _build_search_scopes(config: AdzunaIngestionConfig) -> list[SearchScope]:
    """Build configured Adzuna search scopes."""

    locations = config.locations or [None]

    scopes: list[SearchScope] = []
    for keyword in config.search_keywords:
        for location in locations:
            scopes.append(
                SearchScope(
                    keywords=keyword,
                    location=location,
                )
            )
    return scopes


def _build_requests(config: AdzunaIngestionConfig) -> list[SearchRequest]:
    """Build all paginated Adzuna requests for the run."""

    return build_requests_for_scopes(
        scopes=_build_search_scopes(config),
        max_pages=config.max_pages,
        page_size=config.page_size,
        country=config.country,
    )


def _resolve_sample_file(path_from_config: str) -> Path:
    """Resolve sample path from CWD or repository root."""

    candidate = Path(path_from_config)
    if candidate.exists():
        return candidate

    repo_relative = Path(__file__).resolve().parents[2] / path_from_config
    if repo_relative.exists():
        return repo_relative

    raise FileNotFoundError(f"Sample response file not found: {path_from_config}")


def _sample_response_for_request(
    request: SearchRequest,
    config: AdzunaIngestionConfig,
) -> AdzunaApiResponse:
    """Build a fake API response from a local sample JSON file."""

    sample_file = _resolve_sample_file(config.sample_file_path)
    payload = json.loads(sample_file.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc).isoformat()
    return AdzunaApiResponse(
        source_name=config.source_name,
        endpoint=request.endpoint,
        http_method="GET",
        request_url=f"sample://{sample_file}",
        request_params=request.params,
        search_scope_key=request.search_scope_key,
        page_number=request.page_number,
        page_size=request.page_size,
        response_status_code=200,
        response_time_ms=0,
        response_headers={"x-sample-mode": "true"},
        response_payload=payload,
        content_range={"first_index": None, "last_index": None, "total_results": None},
        started_at=now,
        finished_at=now,
        error_message=None,
    )


def run_adzuna_ingestion(
    config: AdzunaIngestionConfig | None = None,
    database_config: DatabaseConfig | None = None,
) -> IngestionSummary:
    """Run one Adzuna raw ingestion batch."""

    ingestion_config = config or AdzunaIngestionConfig.from_env()
    db_config = database_config or DatabaseConfig.from_env()

    batch_id: str | None = None
    requests_made = 0
    successful_requests = 0
    failed_requests = 0
    records_loaded = 0
    errors: list[str] = []

    with get_connection(db_config) as connection:
        batch_id = create_load_batch(
            connection=connection,
            source_name=ingestion_config.source_name,
            pipeline_name=ingestion_config.pipeline_name,
            triggered_by=ingestion_config.triggered_by,
        )
        LOGGER.info("Created load batch %s", batch_id)

        try:
            requests_to_run = _build_requests(ingestion_config)
            LOGGER.info("Built %s Adzuna search request(s)", len(requests_to_run))

            client = None if ingestion_config.sample_mode else AdzunaClient()

            for search_request in requests_to_run:
                requests_made += 1
                request_id: str | None = None

                try:
                    if ingestion_config.sample_mode:
                        api_response = _sample_response_for_request(search_request, ingestion_config)
                    else:
                        assert client is not None
                        api_response = client.send_search_request(search_request)

                    request_id = insert_api_request(
                        connection=connection,
                        batch_id=batch_id,
                        request_metadata=api_response.to_request_metadata(),
                    )
                    LOGGER.info(
                        "Stored API request %s for search_scope_key=%s page=%s",
                        request_id,
                        api_response.search_scope_key,
                        api_response.page_number,
                    )

                    if api_response.error_message or not _is_success_status(
                        api_response.response_status_code
                    ):
                        failed_requests += 1
                        error = api_response.error_message or (
                            f"Unexpected HTTP status: {api_response.response_status_code}"
                        )
                        errors.append(error)
                        LOGGER.warning("Adzuna request failed: %s", error)
                        continue

                    raw_jobs = parse_raw_job_payloads(api_response.response_payload)
                    inserted_count = insert_raw_job_postings(
                        connection=connection,
                        batch_id=batch_id,
                        request_id=request_id,
                        search_scope_key=api_response.search_scope_key or "unknown_search_scope",
                        raw_jobs=raw_jobs,
                        source_name=ingestion_config.source_name,
                    )
                    records_loaded += inserted_count
                    successful_requests += 1
                    LOGGER.info(
                        "Stored %s raw job posting row(s) for request_id=%s",
                        inserted_count,
                        request_id,
                    )

                except Exception as request_exc:  # noqa: BLE001 - pipeline must record partial failures
                    failed_requests += 1
                    error = f"Request processing failed: {request_exc}"
                    errors.append(error)
                    LOGGER.exception(error)
                    try:
                        connection.rollback()
                    except Exception:  # pragma: no cover - defensive rollback
                        LOGGER.exception("Rollback failed after request error")

                    if request_id is None:
                        LOGGER.warning("No request_id was created for the failed request")
                    continue

            if failed_requests == 0:
                final_status = "success"
                error_message = None
            elif successful_requests > 0 or records_loaded > 0:
                final_status = "partial_success"
                error_message = "; ".join(errors)[:2000]
            else:
                final_status = "failed"
                error_message = "; ".join(errors)[:2000] or "No successful API requests"

            mark_batch_finished(
                connection=connection,
                batch_id=batch_id,
                status=final_status,
                records_loaded=records_loaded,
                requests_made=requests_made,
                error_message=error_message,
            )

            return IngestionSummary(
                batch_id=batch_id,
                status=final_status,
                requests_made=requests_made,
                successful_requests=successful_requests,
                failed_requests=failed_requests,
                records_loaded=records_loaded,
                error_message=error_message,
            )

        except Exception as pipeline_exc:  # noqa: BLE001 - batch must be marked failed
            LOGGER.exception("Adzuna ingestion failed")
            try:
                connection.rollback()
                mark_batch_failed(
                    connection=connection,
                    batch_id=batch_id,
                    records_loaded=records_loaded,
                    requests_made=requests_made,
                    error_message=str(pipeline_exc)[:2000],
                )
            except Exception:
                LOGGER.exception("Could not mark batch %s as failed", batch_id)
            raise


def _is_success_status(status_code: int | None) -> bool:
    return status_code is not None and 200 <= status_code < 300


def main() -> None:
    """CLI entrypoint."""

    configure_logging()
    summary = run_adzuna_ingestion()
    print(json.dumps(summary.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
