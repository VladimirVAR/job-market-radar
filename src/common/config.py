"""Environment-based configuration for ingestion pipelines."""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional local dependency
    load_dotenv = None

from src.common.exceptions import ConfigurationError


def project_root() -> Path:
    """Return the repository root based on this module location."""

    return Path(__file__).resolve().parents[2]


def load_project_dotenv(*, override: bool = False) -> None:
    """Load the project-level .env file when python-dotenv is available.

    Docker Compose reads .env/env_file by itself, but local Python commands
    such as ``python -m src.pipeline.run_adzuna_ingestion`` do not. Loading
    the file here keeps all CLI entry points on the same configuration source.

    ``override`` stays False by default so explicitly exported environment
    variables still win over values from .env.
    """

    if load_dotenv is None:
        return

    load_dotenv(project_root() / ".env", override=override)


load_project_dotenv()


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


@dataclass(frozen=True)
class AdzunaIngestionConfig:
    """Configuration for the Adzuna raw ingestion pipeline."""

    source_name: str = "adzuna"
    pipeline_name: str = "adzuna_ingestion"
    triggered_by: str = "manual"
    search_keywords: list[str] = field(default_factory=lambda: ["data engineer"])
    locations: list[str] = field(default_factory=list)
    country: str = "fr"
    max_pages: int = 1
    page_size: int = 50
    sample_mode: bool = True
    sample_file_path: str = "data/sample/adzuna_sample_response.json"

    @classmethod
    def from_env(cls) -> "AdzunaIngestionConfig":
        """Read Adzuna ingestion settings from environment variables.

        Useful variables:
        - PIPELINE_TRIGGERED_BY
        - ADZUNA_SEARCH_KEYWORDS, comma-separated
        - ADZUNA_LOCATIONS, comma-separated
        - ADZUNA_COUNTRY (default: fr)
        - ADZUNA_MAX_PAGES
        - ADZUNA_PAGE_SIZE
        - ADZUNA_SAMPLE_MODE (default: true until real keys are configured)
        - ADZUNA_SAMPLE_FILE
        """

        max_pages = int(os.getenv("ADZUNA_MAX_PAGES", "1"))
        page_size = int(os.getenv("ADZUNA_PAGE_SIZE", "50"))
        if max_pages < 1:
            raise ConfigurationError("ADZUNA_MAX_PAGES must be >= 1")
        if page_size < 1:
            raise ConfigurationError("ADZUNA_PAGE_SIZE must be >= 1")

        keywords = _split_csv(os.getenv("ADZUNA_SEARCH_KEYWORDS")) or ["data engineer"]

        return cls(
            triggered_by=os.getenv("PIPELINE_TRIGGERED_BY", "manual"),
            search_keywords=keywords,
            locations=_split_csv(os.getenv("ADZUNA_LOCATIONS")),
            country=os.getenv("ADZUNA_COUNTRY", "fr"),
            max_pages=max_pages,
            page_size=page_size,
            sample_mode=_env_bool("ADZUNA_SAMPLE_MODE", True),
            sample_file_path=os.getenv(
                "ADZUNA_SAMPLE_FILE",
                "data/sample/adzuna_sample_response.json",
            ),
        )

    def to_config_snapshot(self) -> dict[str, Any]:
        """Return serializable config metadata for logs."""

        return {
            "source_name": self.source_name,
            "pipeline_name": self.pipeline_name,
            "triggered_by": self.triggered_by,
            "search_keywords": self.search_keywords,
            "locations": self.locations,
            "country": self.country,
            "max_pages": self.max_pages,
            "page_size": self.page_size,
            "sample_mode": self.sample_mode,
            "sample_file_path": self.sample_file_path if self.sample_mode else None,
        }
