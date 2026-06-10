"""Run data quality checks for Job Market Radar.

This module is intentionally small for the MVP.

It provides an Airflow-compatible entrypoint that runs dbt validation/build
commands using project-local paths. It exits with a non-zero code when dbt
validation fails.

Expected command from repository root:

    python -m src.pipeline.run_data_quality_checks
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DBT_PROJECT_DIR = PROJECT_ROOT / "dbt_job_market_radar"
DBT_PROFILES_DIR = DBT_PROJECT_DIR


def _run_command(command: Sequence[str], cwd: Path) -> None:
    """Run a command and raise RuntimeError if it fails."""

    printable_command = " ".join(command)
    print(f"\nRunning command:\n{printable_command}\n")

    completed_process = subprocess.run(
        command,
        cwd=str(cwd),
        check=False,
        text=True,
    )

    if completed_process.returncode != 0:
        raise RuntimeError(
            f"Data quality command failed with exit code "
            f"{completed_process.returncode}: {printable_command}"
        )


def run_data_quality_checks() -> None:
    """Run dbt-based data quality checks.

    The default selector focuses on the layers that exist in Task 009:
    raw sources, staging models, warehouse models, and custom tests.

    The selector can be overridden with DBT_QUALITY_SELECT if needed.
    """

    if not DBT_PROJECT_DIR.exists():
        raise FileNotFoundError(
            f"dbt project directory not found: {DBT_PROJECT_DIR}"
        )

    dbt_selector = os.getenv(
        "DBT_QUALITY_SELECT",
        "source:* path:models/staging path:models/warehouse path:models/marts path:tests",
    )

    dbt_threads = os.getenv("DBT_THREADS", "1").strip() or "1"

    if not dbt_threads.isdigit() or int(dbt_threads) < 1:
        raise ValueError(
            f"DBT_THREADS must be a positive integer, got: {dbt_threads}"
        )

    dbt_target_path = os.getenv(
        "DBT_TARGET_PATH",
        str(DBT_PROJECT_DIR / "target"),
    ).strip() or str(DBT_PROJECT_DIR / "target")

    dbt_bin = os.getenv("DBT_BIN", "dbt").strip() or "dbt"

    parse_command = [
        dbt_bin,
        "parse",
        "--no-partial-parse",
        "--project-dir",
        str(DBT_PROJECT_DIR),
        "--profiles-dir",
        str(DBT_PROFILES_DIR),
        "--target-path",
        dbt_target_path,
    ]

    build_command = [
        dbt_bin,
        "build",
        "--no-partial-parse",
        "--project-dir",
        str(DBT_PROJECT_DIR),
        "--profiles-dir",
        str(DBT_PROFILES_DIR),
        "--target-path",
        dbt_target_path,
        "--threads",
        dbt_threads,
        "--select",
        *dbt_selector.split(),
    ]

    print("Starting Job Market Radar data quality checks.")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"dbt project dir: {DBT_PROJECT_DIR}")
    print(f"dbt profiles dir: {DBT_PROFILES_DIR}")
    print(f"dbt selector: {dbt_selector}")
    print(f"dbt threads: {dbt_threads}")
    print(f"dbt target path: {dbt_target_path}")
    print(f"dbt executable: {dbt_bin}")

    _run_command(parse_command, cwd=PROJECT_ROOT)
    _run_command(build_command, cwd=PROJECT_ROOT)

    print("\nData quality checks completed successfully.")


def main() -> int:
    """CLI entrypoint."""

    try:
        run_data_quality_checks()
    except Exception as exc:  # noqa: BLE001 - CLI should print any failure clearly
        print("\nData quality checks failed.")
        print(f"Error: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
