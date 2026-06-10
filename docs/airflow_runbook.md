# Airflow Runbook — Job Market Radar

## Purpose

This runbook explains how to validate and run the `job_market_radar` Airflow DAG locally.

The DAG orchestrates the MVP pipeline:

```text
start
  -> ingest_france_travail_raw_jobs
  -> dbt_build
  -> run_data_quality_checks
  -> generate_weekly_report
  -> end
```

Airflow only orchestrates existing commands. It does not contain transformation logic, relevance scoring, dashboard logic, or business SQL.

---

## Start local environment

From the repository root:

```bash
docker compose up
```

In a second terminal:

```bash
docker compose ps
```

Expected services:

```text
job_market_radar_postgres
job_market_radar_airflow_postgres
job_market_radar_airflow_webserver
job_market_radar_airflow_scheduler
```

---

## Open Airflow UI

```text
http://localhost:8080
```

Default local credentials:

```text
admin / admin
```

---

## Check DAG visibility

```bash
docker compose exec airflow-webserver airflow dags list
```

Expected DAG:

```text
job_market_radar
```

---

## Check DAG task list

```bash
docker compose exec airflow-webserver airflow tasks list job_market_radar
```

Expected tasks:

```text
start
ingest_france_travail_raw_jobs
dbt_build
run_data_quality_checks
generate_weekly_report
end
```

---

## Sample mode

For local testing without real France Travail credentials, configure sample mode through `.env`:

```text
FRANCE_TRAVAIL_SAMPLE_MODE=true
FRANCE_TRAVAIL_SAMPLE_FILE=data/sample/france_travail_sample_response.json
```

Do not commit `.env`.

---

## dbt profile

The Airflow container expects:

```text
/opt/airflow/project/dbt_job_market_radar/profiles.yml
```

This maps to the local repository file:

```text
dbt_job_market_radar/profiles.yml
```

If it contains local credentials, do not commit it.

If missing, create it from:

```text
dbt_job_market_radar/profiles.yml.example
```

provided the example profile uses placeholders or environment variables.

---

## Test individual tasks

```bash
docker compose exec airflow-webserver airflow tasks test job_market_radar ingest_france_travail_raw_jobs 2026-01-01
docker compose exec airflow-webserver airflow tasks test job_market_radar dbt_build 2026-01-01
docker compose exec airflow-webserver airflow tasks test job_market_radar run_data_quality_checks 2026-01-01
```

---

## Run the DAG manually

From Airflow UI:

```text
DAGs -> job_market_radar -> Trigger DAG
```

Or from CLI:

```bash
docker compose exec airflow-webserver airflow dags trigger job_market_radar
```

---

## Troubleshooting

### DAG not visible

Check that this file exists locally:

```text
dags/job_market_radar_dag.py
```

Then check import errors:

```bash
docker compose exec airflow-webserver airflow dags list-import-errors
```

### dbt task fails

Check:

```bash
docker compose exec airflow-webserver ls -la /opt/airflow/project/dbt_job_market_radar
docker compose exec airflow-webserver ls -la /opt/airflow/project/dbt_job_market_radar/profiles.yml
```

Then run:

```bash
docker compose exec airflow-webserver dbt debug --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar
```

### Ingestion task fails due to credentials

Use sample mode for local validation:

```text
FRANCE_TRAVAIL_SAMPLE_MODE=true
FRANCE_TRAVAIL_SAMPLE_FILE=data/sample/france_travail_sample_response.json
```

Then restart Airflow services if needed.

---

## Git safety checklist

Before commit:

```bash
git status
```

Do not commit:

```text
.env
dbt_job_market_radar/profiles.yml
dbt_job_market_radar/target/
dbt_job_market_radar/logs/
Airflow logs
local secrets
```
