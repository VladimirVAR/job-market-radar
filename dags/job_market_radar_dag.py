"""
Job Market Radar Airflow DAG.

This DAG orchestrates the local Job Market Radar data pipeline.
It does not contain ingestion logic, SQL transformations, data quality logic,
dashboard logic, relevance scoring, or business rules.

Expected flow:
start
  -> [ingest_france_travail_raw_jobs, ingest_adzuna_raw_jobs]
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


def dbt_build_command() -> str:
    """Return the dbt build command used by the orchestration task."""
    profiles_path = os.path.join(DBT_PROFILES_DIR, "profiles.yml")
    return (
        "test -f "
        + shlex.quote(profiles_path)
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
    )


default_args = {
    "owner": "job_market_radar",
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="job_market_radar",
    description="Orchestrates Job Market Radar ingestion, dbt build, validation, and report generation.",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    max_active_tasks=2,
    tags=["job_market_radar", "mvp", "orchestration"],
    doc_md="""
# Job Market Radar DAG

This DAG is intentionally simple and orchestration-focused.

It runs:

1. Raw France Travail ingestion
2. Raw Adzuna ingestion
3. dbt build
4. Data quality checks
5. Weekly Markdown report generation
6. End marker

## Boundary

Airflow only orchestrates commands. It does not implement transformations, relevance scoring,
skill analytics, dashboard logic, or business rules.

## Infrastructure boundary

Docker Compose starts the infrastructure: PostgreSQL, Airflow metadata database,
Airflow webserver, Airflow scheduler, volumes, and network.

PostgreSQL initializes raw schemas and raw tables from `sql/ddl` when the database
volume is created for the first time.

Airflow runs the pipeline after that infrastructure exists. It does not create Docker
containers and it does not start Streamlit. Streamlit is a separate dashboard process
that reads marts prepared by dbt.

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

## Database configuration

For local Windows commands, the project can use the published PostgreSQL port, for example:

```text
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5433
```

Inside Docker/Airflow, the project must use the Docker Compose service address:

```text
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
```

The Docker Compose configuration is expected to provide that container-specific override.

## Concurrency

This DAG allows only one active DAG run at a time (`max_active_runs=1`). This prevents
two concurrent `dbt build` tasks from trying to rebuild the same warehouse and marts
objects in the same PostgreSQL database.

The two ingestion tasks may run in parallel before dbt. The dbt build itself uses
`DBT_THREADS`, defaulting to `1`, for deterministic local execution.

## Sample mode

For local sample-mode testing, configure the environment outside the DAG, for example in `.env`:

```text
FRANCE_TRAVAIL_SAMPLE_MODE=true
FRANCE_TRAVAIL_SAMPLE_FILE=data/sample/france_travail_sample_response.json
ADZUNA_SAMPLE_MODE=true
ADZUNA_SAMPLE_FILE=data/sample/adzuna_sample_response.json
```

The DAG does not require real API credentials when the corresponding ingestion code is
configured to use sample mode.
""",
) as dag:
    start = EmptyOperator(task_id="start")

    ingest_france_travail_raw_jobs = BashOperator(
        task_id="ingest_france_travail_raw_jobs",
        bash_command=project_command(
            "python -m src.pipeline.run_france_travail_ingestion"
        ),
    )

    ingest_adzuna_raw_jobs = BashOperator(
        task_id="ingest_adzuna_raw_jobs",
        bash_command=project_command(
            "python -m src.pipeline.run_adzuna_ingestion"
        ),
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=project_command(dbt_build_command()),
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

    start >> [ingest_france_travail_raw_jobs, ingest_adzuna_raw_jobs] >> dbt_build
    dbt_build >> run_data_quality_checks >> generate_weekly_report >> end
