"""Database utilities for the Job Market Radar Streamlit dashboard.

Streamlit is a consumption layer only. All dashboard queries should read from
`marts.*` models that are prepared by dbt.
"""

from __future__ import annotations

import ast
import os
import re
from typing import Any
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


FORBIDDEN_BUSINESS_SCHEMAS = ("raw.", "staging.", "warehouse.")


class DashboardQueryError(ValueError):
    """Raised when a dashboard query violates the marts-only boundary."""


def _env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or value == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_database_url() -> str:
    """Build a PostgreSQL SQLAlchemy URL from environment variables."""
    host = _env("POSTGRES_HOST", "localhost")
    port = _env("POSTGRES_PORT", "5432")
    db = _env("POSTGRES_DB", "job_market_radar")
    user = _env("POSTGRES_USER", "job_market_radar")
    password = quote_plus(_env("POSTGRES_PASSWORD", "change_me"))
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


@st.cache_resource(show_spinner=False)
def get_engine() -> Engine:
    """Return a cached SQLAlchemy engine."""
    return create_engine(get_database_url(), pool_pre_ping=True)


def assert_marts_only(sql: str, *, allow_technical: bool = False) -> None:
    """Protect the dashboard boundary from accidental raw/staging/warehouse usage.

    Business pages must query only `marts.*` objects. The current MVP uses
    `marts.mart_data_freshness` for technical status as well, so the default is
    intentionally strict.
    """
    normalized = re.sub(r"\s+", " ", sql.lower())
    if allow_technical:
        return
    if any(schema in normalized for schema in FORBIDDEN_BUSINESS_SCHEMAS):
        raise DashboardQueryError(
            "Dashboard business queries must read from marts.* only. "
            "Move this logic upstream into dbt marts."
        )
    if "marts." not in normalized:
        raise DashboardQueryError(
            "Dashboard queries should explicitly read from marts.* models."
        )


@st.cache_data(ttl=300, show_spinner=False)
def load_dataframe(sql: str, params: dict[str, Any] | None = None) -> pd.DataFrame:
    """Execute a read-only SQL query and return a DataFrame."""
    assert_marts_only(sql)
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql_query(text(sql), conn, params=params or {})


def test_connection() -> tuple[bool, str]:
    """Return a lightweight database connection status."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("select 1"))
        return True, "Connected to PostgreSQL"
    except Exception as exc:  # pragma: no cover - UI status helper
        return False, str(exc)


def show_empty_state(message: str = "No data available yet. Run the pipeline to load job postings.") -> None:
    st.info(message)


def first_existing_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for column in candidates:
        if column in df.columns:
            return column
    return None


def _is_missing_scalar(value: Any) -> bool:
    """Return True for scalar null-like values without breaking on arrays/lists."""
    try:
        result = pd.isna(value)
    except TypeError:
        return False

    if isinstance(result, bool):
        return result
    return False


def _format_sequence(values: list[Any] | tuple[Any, ...] | set[Any]) -> str:
    return ", ".join(str(item) for item in values if item is not None and not _is_missing_scalar(item))


def format_list_like(value: Any) -> str:
    """Format arrays, tuples, JSON-like lists, or scalar values for tables."""
    if value is None:
        return ""

    if isinstance(value, (list, tuple, set)):
        return _format_sequence(value)

    if _is_missing_scalar(value):
        return ""

    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return ""

        if stripped.startswith("[") and stripped.endswith("]"):
            try:
                parsed = ast.literal_eval(stripped)
            except (SyntaxError, ValueError):
                return stripped
            if isinstance(parsed, (list, tuple, set)):
                return _format_sequence(parsed)

        if stripped.startswith("{") and stripped.endswith("}") and "," in stripped:
            # PostgreSQL array text fallback, for example: {Python,SQL,dbt}
            return ", ".join(item.strip().strip('"') for item in stripped[1:-1].split(",") if item.strip())

        return stripped

    return str(value)


def prepare_display_dataframe(df: pd.DataFrame, list_like_columns: list[str] | None = None) -> pd.DataFrame:
    """Return a UI-safe copy of a DataFrame with list-like columns formatted."""
    display_df = df.copy()
    for column in list_like_columns or []:
        if column in display_df.columns:
            display_df[column] = display_df[column].apply(format_list_like)
    return display_df
