"""Environment-based configuration for ingestion pipelines."""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from typing import Any

from src.common.exceptions import ConfigurationError


@dataclass(frozen=True)
class DatabaseConfig:
    """PostgreSQL connection settings."""

    host: str = "localhost"
    port: int = 5432
    database: str = "job_market_radar"
    user: str = "job_market_radar"
    password: str = "change_me"

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Read database settings from environment variables."""

        return cls(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            database=os.getenv("POSTGRES_DB", "job_market_radar"),
            user=os.getenv("POSTGRES_USER", "job_market_radar"),
            password=os.getenv("POSTGRES_PASSWORD", "change_me"),
        )


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class FranceTravailIngestionConfig:
    """Configuration for the France Travail raw ingestion pipeline."""

    source_name: str = "france_travail"
    pipeline_name: str = "france_travail_ingestion"
    triggered_by: str = "manual"
    search_keywords: list[str] = field(default_factory=lambda: ["data engineer"])
    locations: list[str] = field(default_factory=list)
    contract_types: list[str] = field(default_factory=list)
    remote_values: list[str] = field(default_factory=list)
    max_pages: int = 1
    page_size: int = 50
    sample_mode: bool = False
    sample_file_path: str = "data/sample/france_travail_sample_response.json"

    @classmethod
    def from_env(cls) -> "FranceTravailIngestionConfig":
        """Read France Travail ingestion settings from environment variables.

        Useful variables:
        - PIPELINE_TRIGGERED_BY
        - FRANCE_TRAVAIL_SEARCH_KEYWORDS, comma-separated
        - FRANCE_TRAVAIL_LOCATIONS, comma-separated
        - FRANCE_TRAVAIL_CONTRACT_TYPES, comma-separated
        - FRANCE_TRAVAIL_REMOTE_VALUES, comma-separated
        - FRANCE_TRAVAIL_MAX_PAGES
        - FRANCE_TRAVAIL_PAGE_SIZE
        - FRANCE_TRAVAIL_SAMPLE_MODE
        - FRANCE_TRAVAIL_SAMPLE_FILE
        """

        max_pages = int(os.getenv("FRANCE_TRAVAIL_MAX_PAGES", "1"))
        page_size = int(os.getenv("FRANCE_TRAVAIL_PAGE_SIZE", "50"))
        if max_pages < 1:
            raise ConfigurationError("FRANCE_TRAVAIL_MAX_PAGES must be >= 1")
        if page_size < 1:
            raise ConfigurationError("FRANCE_TRAVAIL_PAGE_SIZE must be >= 1")

        keywords = _split_csv(os.getenv("FRANCE_TRAVAIL_SEARCH_KEYWORDS")) or ["data engineer"]

        return cls(
            triggered_by=os.getenv("PIPELINE_TRIGGERED_BY", "manual"),
            search_keywords=keywords,
            locations=_split_csv(os.getenv("FRANCE_TRAVAIL_LOCATIONS")),
            contract_types=_split_csv(os.getenv("FRANCE_TRAVAIL_CONTRACT_TYPES")),
            remote_values=_split_csv(os.getenv("FRANCE_TRAVAIL_REMOTE_VALUES")),
            max_pages=max_pages,
            page_size=page_size,
            sample_mode=_env_bool("FRANCE_TRAVAIL_SAMPLE_MODE", False),
            sample_file_path=os.getenv(
                "FRANCE_TRAVAIL_SAMPLE_FILE",
                "data/sample/france_travail_sample_response.json",
            ),
        )

    def to_config_snapshot(self) -> dict[str, Any]:
        """Return serializable config metadata for logs or future raw batch extensions."""

        return {
            "source_name": self.source_name,
            "pipeline_name": self.pipeline_name,
            "triggered_by": self.triggered_by,
            "search_keywords": self.search_keywords,
            "locations": self.locations,
            "contract_types": self.contract_types,
            "remote_values": self.remote_values,
            "max_pages": self.max_pages,
            "page_size": self.page_size,
            "sample_mode": self.sample_mode,
            "sample_file_path": self.sample_file_path if self.sample_mode else None,
        }
