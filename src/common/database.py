"""PostgreSQL connection helpers for Python ingestion."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from src.common.config import DatabaseConfig
from src.common.exceptions import DatabaseError


@contextmanager
def get_connection(config: DatabaseConfig | None = None) -> Iterator[object]:
    """Yield a psycopg2 PostgreSQL connection and close it afterwards.

    The function imports psycopg2 lazily so static checks and unit tests that do
    not touch the database can still import the project modules.
    """

    try:
        import psycopg2  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise DatabaseError(
            "psycopg2 is required for PostgreSQL loading. "
            "Install psycopg2-binary or add it to requirements.txt."
        ) from exc

    db_config = config or DatabaseConfig.from_env()
    connection = psycopg2.connect(
        host=db_config.host,
        port=db_config.port,
        dbname=db_config.database,
        user=db_config.user,
        password=db_config.password,
    )
    connection.autocommit = False
    try:
        yield connection
    finally:
        connection.close()


def jsonb(value: object) -> object:
    """Wrap a Python object for insertion into a PostgreSQL JSONB column."""

    try:
        from psycopg2.extras import Json  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise DatabaseError(
            "psycopg2 is required for PostgreSQL JSONB loading."
        ) from exc
    return Json(value)
