"""
Job Market Radar Airflow DAG.

This DAG orchestrates the MVP pipeline only.
It does not contain ingestion logic, SQL transformations, data quality logic,
dashboard logic, relevance scoring, or business rules.

Expected flow:
start
  -> ingest_france_travail_raw_jobs
  -> dbt_build
  -> run_data_quality_checks
  -> generate_weekly_report
  -> end
"""

from __future__ import annotations

import os
import shlex
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator


PROJECT_ROOT = os.getenv("PROJECT_ROOT", "/opt/airflow/project")
DBT_PROJECT_DIR = os.getenv(
    "DBT_PROJECT_DIR",
    os.path.join(PROJECT_ROOT, "dbt_job_market_radar"),
)
DBT_PROFILES_DIR = os.getenv("DBT_PROFILES_DIR", DBT_PROJECT_DIR)
DBT_THREADS = os.getenv("DBT_THREADS", "1")
DBT_TARGET_PATH = os.getenv(
    "DBT_TARGET_PATH",
    "/tmp/job_market_radar_dbt_target",
)
DBT_BIN = os.getenv("DBT_BIN", "dbt")


def project_command(command: str) -> str:
    """Run a shell command from the mounted project root inside the Airflow container."""
    return f"set -euo pipefail; cd {shlex.quote(PROJECT_ROOT)}; {command}"


default_args = {
    "owner": "job_market_radar",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="job_market_radar",
    description="Orchestrates Job Market Radar MVP ingestion, dbt build, validation, and report step.",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["job_market_radar", "mvp", "orchestration"],
    doc_md="""
# Job Market Radar MVP DAG

This DAG is intentionally simple and orchestration-focused.

It runs:

1. Raw France Travail ingestion
2. dbt build
3. Data quality checks
4. Weekly Markdown report generation
5. End marker

## Boundary

Airflow only orchestrates commands. It does not implement transformations, relevance scoring,
skill analytics, dashboard logic, or business rules.

## Container paths

By default, the project is expected to be mounted at:

```text
/opt/airflow/project
```

This can be overridden with:

```text
PROJECT_ROOT
DBT_PROJECT_DIR
DBT_PROFILES_DIR
```

## Sample mode

For local sample-mode testing, configure the environment outside the DAG, for example in `.env`:

```text
FRANCE_TRAVAIL_SAMPLE_MODE=true
FRANCE_TRAVAIL_SAMPLE_FILE=data/sample/france_travail_sample_response.json
```

The DAG does not require real France Travail credentials when the ingestion code is configured
to use sample mode.
""",
) as dag:
    start = EmptyOperator(task_id="start")

    ingest_france_travail_raw_jobs = BashOperator(
        task_id="ingest_france_travail_raw_jobs",
        bash_command=project_command(
            "python -m src.pipeline.run_france_travail_ingestion"
        ),
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=project_command(
            "test -f "
            + shlex.quote(os.path.join(DBT_PROFILES_DIR, "profiles.yml"))
            + " || "
            + "("
            + "echo 'ERROR: dbt profiles.yml not found in DBT_PROFILES_DIR="
            + shlex.quote(DBT_PROFILES_DIR)
            + "' && "
            + "echo 'Create dbt_job_market_radar/profiles.yml from profiles.yml.example or ensure it is mounted into the Airflow container.' && "
            + "exit 1"
            + "); "
            + shlex.quote(DBT_BIN)
            + " build --no-partial-parse --threads "
            + shlex.quote(DBT_THREADS)
            + " "
            + "--project-dir "
            + shlex.quote(DBT_PROJECT_DIR)
            + " "
            + "--profiles-dir "
            + shlex.quote(DBT_PROFILES_DIR)
            + " "
            + "--target-path "
            + shlex.quote(DBT_TARGET_PATH)
        ),
    )

    run_data_quality_checks = BashOperator(
        task_id="run_data_quality_checks",
        bash_command=project_command(
            "python -m src.pipeline.run_data_quality_checks"
        ),
    )

    generate_weekly_report = BashOperator(
        task_id="generate_weekly_report",
        bash_command=project_command(
            "python -m src.reporting.generate_weekly_markdown_report"
        ),
    )

    end = EmptyOperator(task_id="end")

    (
        start
        >> ingest_france_travail_raw_jobs
        >> dbt_build
        >> run_data_quality_checks
        >> generate_weekly_report
        >> end
    )
