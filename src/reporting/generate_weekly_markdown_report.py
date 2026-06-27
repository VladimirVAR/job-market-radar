"""Generate a weekly Markdown market report from marts.mart_weekly_market_summary."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from src.common.config import DatabaseConfig
from src.common.database import get_connection
from src.common.logging import configure_logging, get_logger

LOGGER = get_logger(__name__)


@dataclass(frozen=True)
class ReportConfig:
    output_dir: str = "reports/weekly"

    @classmethod
    def from_env(cls) -> "ReportConfig":
        return cls(
            output_dir=os.getenv("REPORT_OUTPUT_DIR", "reports/weekly"),
        )


def _format_array(value: Any) -> str:
    if not value:
        return "—"
    if isinstance(value, (list, tuple)):
        return ", ".join(str(item) for item in value if item)
    return str(value)


def _fetch_summary(connection: Any) -> dict[str, Any] | None:
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM marts.mart_weekly_market_summary LIMIT 1")
        row = cursor.fetchone()
        if row is None:
            return None
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))


def _render_markdown(row: dict[str, Any]) -> str:
    week_start = row.get("week_start_date", "unknown")
    week_end = row.get("week_end_date", "unknown")
    total = row.get("total_active_jobs", 0)
    new_jobs_raw = row.get("new_jobs")
    new_jobs = "Not available yet" if new_jobs_raw is None else new_jobs_raw
    closed = row.get("closed_or_missing_jobs", 0)
    relevant = row.get("relevant_job_count", 0)
    high_match = row.get("high_match_job_count", 0)
    junior_friendly = row.get("junior_friendly_jobs", 0)
    avg_score = row.get("avg_relevance_score")
    top_skills = _format_array(row.get("top_skills"))
    top_missing = _format_array(row.get("top_missing_skills"))
    top_locations = _format_array(row.get("top_locations"))
    top_companies = _format_array(row.get("top_companies"))
    summary_text = row.get("summary_text", "")
    generated_at = row.get("generated_at", "")
    avg_score_str = f"{avg_score:.1f}" if avg_score is not None else "—"

    return f"""# Weekly Job Market Report — {week_start} to {week_end}

> Generated at {generated_at}

## Market snapshot

| Metric | Value |
|---|---|
| Total active jobs | {total} |
| New this week | {new_jobs} |
| Closed / missing | {closed} |
| Relevant jobs | {relevant} |
| High-match jobs | {high_match} |
| Junior-friendly | {junior_friendly} |
| Avg relevance score | {avg_score_str} |

## Top skills demanded

{top_skills}

## Top locations

{top_locations}

## Top companies

{top_companies}

## Top missing skills (growth gaps)

{top_missing}

## Summary

{summary_text}
"""


def generate_weekly_report(
    db_config: DatabaseConfig | None = None,
    report_config: ReportConfig | None = None,
) -> str | None:
    """Generate weekly Markdown report and write it to disk. Returns output path or None."""

    db_cfg = db_config or DatabaseConfig.from_env()
    rep_cfg = report_config or ReportConfig.from_env()

    output_dir = Path(rep_cfg.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with get_connection(db_cfg) as connection:
        row = _fetch_summary(connection)

    if row is None:
        LOGGER.warning("mart_weekly_market_summary returned no rows — skipping report generation")
        return None

    markdown = _render_markdown(row)

    report_date = row.get("week_start_date") or date.today()
    filename = f"weekly_report_{report_date}.md"
    output_path = output_dir / filename
    output_path.write_text(markdown, encoding="utf-8")

    LOGGER.info("Weekly report written to %s", output_path)
    return str(output_path)


def main() -> None:
    configure_logging()
    output_path = generate_weekly_report()
    if output_path:
        print(output_path)
    else:
        print("No report generated — mart returned no data")


if __name__ == "__main__":
    main()
