# Task 010 Execution Report — Create Airflow DAG

## 1. Task Summary

**Task:** Task 010 — Create Airflow DAG
**Responsible role:** Orchestration / DevOps Engineer
**DAG id:** `job_market_radar`
**Deliverable:** `dags/job_market_radar_dag.py`

The purpose of this task is to connect existing pipeline components into a simple Airflow workflow.

Airflow is used only for orchestration. The DAG does not contain ingestion logic, SQL transformations, dbt model logic, data quality logic, Streamlit logic, relevance scoring, or business rules.

---

## 2. Implemented DAG

Created:

```text
dags/job_market_radar_dag.py
```

DAG id:

```text
job_market_radar
```

Schedule:

```python
schedule=None
```

This keeps the DAG manual-only for the MVP.

Default configuration:

```text
owner: job_market_radar
retries: 1
retry_delay: 5 minutes
catchup: False
```

---

## 3. Task List

The DAG contains the following tasks:

```text
start
ingest_france_travail_raw_jobs
dbt_build
run_data_quality_checks
generate_weekly_report
end
```

---

## 4. Dependency Graph

Implemented dependency flow:

```text
start
  >> ingest_france_travail_raw_jobs
  >> dbt_build
  >> run_data_quality_checks
  >> generate_weekly_report
  >> end
```

This ensures:

- ingestion runs before dbt
- dbt runs before data quality checks
- data quality checks run before report generation
- report generation runs before the final marker task

---

## 5. Exact Commands Used by Each Task

### `start`

Operator:

```text
EmptyOperator
```

Purpose:

```text
Simple start marker.
```

---

### `ingest_france_travail_raw_jobs`

Operator:

```text
BashOperator
```

Command:

```bash
python -m src.pipeline.run_france_travail_ingestion
```

Purpose:

```text
Creates a load batch, calls France Travail API or sample mode, stores request metadata,
and writes raw job postings into PostgreSQL.
```

This task does not run dbt.

---

### `dbt_build`

Operator:

```text
BashOperator
```

Command:

```bash
dbt build --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar
```

In the Airflow container, the command is executed from the configured project root:

```text
/opt/airflow/project
```

Purpose:

```text
Validates raw sources, builds staging and warehouse models, and runs dbt tests.
```

A pre-check is included to fail clearly if:

```text
dbt_job_market_radar/profiles.yml
```

is not available inside the Airflow container.

---

### `run_data_quality_checks`

Operator:

```text
BashOperator
```

Command:

```bash
python -m src.pipeline.run_data_quality_checks
```

Purpose:

```text
Runs dbt parse, dbt validation selector, and custom raw/staging/warehouse checks.
```

This task runs after `dbt_build`.

---

### `generate_weekly_report`

Operator:

```text
BashOperator
```

Command behavior:

```bash
if src/reporting/generate_weekly_markdown_report.py exists:
    python -m src.reporting.generate_weekly_markdown_report
else:
    echo "Weekly report generation placeholder. Full report logic will be implemented later."
```

Purpose:

```text
Keeps the DAG structure complete without blocking Task 010 if weekly reporting logic is not ready yet.
```

---

### `end`

Operator:

```text
EmptyOperator
```

Purpose:

```text
Simple end marker.
```

---

## 6. Path Handling

The DAG does not hardcode local Windows paths.

Default container-side project root:

```text
/opt/airflow/project
```

This is compatible with the Docker Compose volume mount used for the local MVP environment.

Configurable environment variables:

```text
PROJECT_ROOT
DBT_PROJECT_DIR
DBT_PROFILES_DIR
```

Default values:

```text
PROJECT_ROOT=/opt/airflow/project
DBT_PROJECT_DIR=/opt/airflow/project/dbt_job_market_radar
DBT_PROFILES_DIR=/opt/airflow/project/dbt_job_market_radar
```

---

## 7. dbt Profile Handling

Chosen approach:

```text
Option A — use project-local dbt_job_market_radar/profiles.yml mounted into the Airflow container.
```

Expected file inside the Airflow container:

```text
/opt/airflow/project/dbt_job_market_radar/profiles.yml
```

Important:

```text
profiles.yml should not be committed if it contains local credentials or secrets.
profiles.yml.example can be committed if it uses placeholders or environment variables.
```

The `dbt_build` task includes a clear runtime check. If `profiles.yml` is missing, the task fails with an explicit message explaining what file is missing and how to fix it.

---

## 8. Sample Mode Handling

The DAG itself does not require real France Travail credentials.

For local MVP testing, sample mode should be configured through environment variables outside the DAG:

```text
FRANCE_TRAVAIL_SAMPLE_MODE=true
FRANCE_TRAVAIL_SAMPLE_FILE=data/sample/france_travail_sample_response.json
```

The ingestion task simply runs:

```bash
python -m src.pipeline.run_france_travail_ingestion
```

The ingestion module is responsible for deciding whether to use real API mode or sample mode based on environment configuration.

---

## 9. Validation Commands

Run from repository root.

### Check running containers

```bash
docker compose ps
```

Expected important services:

```text
job_market_radar_postgres
job_market_radar_airflow_postgres
job_market_radar_airflow_webserver
job_market_radar_airflow_scheduler
```

---

### Check DAG visibility

```bash
docker compose exec airflow-webserver airflow dags list
```

Expected:

```text
job_market_radar
```

---

### Check task list

```bash
docker compose exec airflow-webserver airflow tasks list job_market_radar
```

Expected:

```text
start
ingest_france_travail_raw_jobs
dbt_build
run_data_quality_checks
generate_weekly_report
end
```

---

### Optional task tests

```bash
docker compose exec airflow-webserver airflow tasks test job_market_radar ingest_france_travail_raw_jobs 2026-01-01
docker compose exec airflow-webserver airflow tasks test job_market_radar dbt_build 2026-01-01
docker compose exec airflow-webserver airflow tasks test job_market_radar run_data_quality_checks 2026-01-01
```

---

### Minimum command checks if task tests are too heavy

```bash
docker compose exec airflow-webserver python -m src.pipeline.run_data_quality_checks
```

```bash
docker compose exec airflow-webserver dbt build --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar
```

---

## 10. Local Validation Status

This report file was prepared with the implementation.

The following commands still need to be executed in the local Docker environment after copying the DAG into the repository:

```bash
docker compose exec airflow-webserver airflow dags list
docker compose exec airflow-webserver airflow tasks list job_market_radar
```

Record the actual local outputs here after execution.

---

## 11. Acceptance Criteria Mapping

| Acceptance Criterion | Status |
|---|---:|
| `dags/job_market_radar_dag.py` exists | Prepared |
| DAG id is `job_market_radar` | Prepared |
| DAG is visible in Airflow | Pending local validation |
| DAG has expected task structure | Prepared |
| DAG dependencies are correct | Prepared |
| Ingestion runs before dbt | Prepared |
| Data quality checks run after dbt | Prepared |
| DAG does not contain business transformations | Passed by design |
| DAG does not hardcode Windows paths | Passed by design |
| DAG can run in sample mode | Prepared, depends on environment |
| Airflow can import the DAG without errors | Pending local validation |
| `airflow dags list` shows the DAG | Pending local validation |
| `airflow tasks list job_market_radar` shows expected tasks | Pending local validation |
| Task execution report saved under `reports/task_execution/` | Prepared |
| No secrets committed | Requires Git check before commit |

---

## 12. Known Limitations

1. `generate_weekly_report` uses safe conditional behavior:
   - runs the actual report module if it exists
   - otherwise prints a placeholder message

2. dbt profile availability depends on local environment:
   - `dbt_job_market_radar/profiles.yml` must exist in the mounted project directory
   - the file should remain uncommitted if it contains local credentials

3. Full DAG run should be validated after confirming:
   - sample mode is enabled or real API credentials are available
   - raw schema exists
   - dbt project and profiles are correctly configured

---

## 13. Follow-up for Next Roles

### For Task 011 — Streamlit Dashboard

Streamlit should consume marts only. The DAG does not implement dashboard logic.

### For Task 012 — Documentation / Demo

README and demo docs should include:

```text
docker compose up
Airflow UI URL
manual DAG trigger steps
sample mode instructions
dbt profile setup note
known limitations
```

---

## 14. Final Handoff

Prepared deliverables:

```text
dags/job_market_radar_dag.py
reports/task_execution/010-create-airflow-dag-report.md
docs/airflow_runbook.md
```

Recommended immediate next step:

```text
Copy files into the repository, restart or refresh Airflow, then run validation commands.
```
