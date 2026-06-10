# Task 013B Local Execution Runbook

## 1. Commit Task 013 first

```bash
git status
git add src/pipeline/run_data_quality_checks.py reports/task_execution/013-activate-live-france-travail-ingestion-report.md
git commit -m "Complete Task 013 live France Travail ingestion"
git status
```

Expected:

```text
nothing to commit, working tree clean
```

## 2. Apply Task 013B files

Copy prepared files into the repository.

## 3. Reset Docker volumes

```bash
docker compose down -v
docker compose up -d --build
docker compose ps -a
```

## 4. Confirm live `.env`

```text
FRANCE_TRAVAIL_SAMPLE_MODE=false
FRANCE_TRAVAIL_CLIENT_ID=configured locally
FRANCE_TRAVAIL_CLIENT_SECRET=configured locally
FRANCE_TRAVAIL_SEARCH_KEYWORDS=data engineer,analytics engineer
FRANCE_TRAVAIL_MAX_PAGES=1
FRANCE_TRAVAIL_PAGE_SIZE=50
```

Do not commit `.env`.

## 5. Run clean live ingestion

```bash
python -m src.pipeline.run_france_travail_ingestion
```

## 6. Run dbt build

```bash
dbt build --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar
```

## 7. Run data quality checks

```bash
python -m src.pipeline.run_data_quality_checks
```

## 8. Validate Streamlit

```bash
streamlit run streamlit_app/app.py
```

## 9. Validate Airflow

```bash
docker compose exec airflow-webserver airflow dags unpause job_market_radar
docker compose exec airflow-webserver airflow dags trigger job_market_radar --run-id task_013B_clean_live_airflow_validation
docker compose exec airflow-webserver airflow tasks states-for-dag-run job_market_radar task_013B_clean_live_airflow_validation
```

## 10. Fill report and commit Task 013B

Update report values from `PENDING` to actual results.

```bash
git add tasks/README.md tasks/011A-build-analytics-marts.md tasks/011B-create-streamlit-dashboard.md tasks/013-activate-live-france-travail-ingestion.md tasks/013B-project-plan-reconciliation-and-clean-live-baseline.md tasks/014-final-polish-public-release-readiness.md backlog.md reports/task_execution/013B-project-plan-reconciliation-and-clean-live-baseline-report.md
git commit -m "Complete Task 013B project plan reconciliation and clean live baseline"
```
