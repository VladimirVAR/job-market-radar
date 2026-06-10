# Task 013B Report — Project Plan Reconciliation & Clean Live Baseline

## Task Purpose

Task 013B reconciles the project plan with the real implementation history and validates the project from a clean live-data baseline before final public release polish.

This is a stabilization and release-governance task, not a feature task.

The task also intentionally validates reproducibility after a full Docker volume reset. During this validation, two real reproducibility issues were found and fixed:

1. the analytical PostgreSQL database did not auto-initialize project schemas and raw tables after `docker compose down -v`;
2. Airflow containers did not initially receive the same France Travail runtime configuration as manual/local ingestion.

Both issues were resolved as part of Task 013B.

---

## Files Created / Modified

### Created

```text
tasks/README.md
tasks/011A-build-analytics-marts.md
tasks/011B-create-streamlit-dashboard.md
tasks/013-activate-live-france-travail-ingestion.md
tasks/013B-project-plan-reconciliation-and-clean-live-baseline.md
tasks/014-final-polish-public-release-readiness.md
docs/release/task_013B_local_execution_runbook.md
reports/task_execution/013B-project-plan-reconciliation-and-clean-live-baseline-report.md
```

### Modified

```text
docker-compose.yml
tasks/backlog.md
```

### Final Git Status Before Commit

At the end of the validation work, the repository showed only expected Task 013B changes:

```text
modified:   docker-compose.yml
modified:   tasks/backlog.md

untracked:
  docs/release/
  reports/task_execution/013B-project-plan-reconciliation-and-clean-live-baseline-report.md
  tasks/011A-build-analytics-marts.md
  tasks/011B-create-streamlit-dashboard.md
  tasks/013-activate-live-france-travail-ingestion.md
  tasks/013B-project-plan-reconciliation-and-clean-live-baseline.md
  tasks/014-final-polish-public-release-readiness.md
  tasks/README.md
```

No `.env`, dbt `target/`, Docker volumes, credentials, logs, screenshots, or cache files were included in Git status.

---

## Updated Task Sequence

The project task sequence was reconciled to match the real implementation history:

```text
001 -> 002 -> 003 -> 004 -> 005 -> 006 -> 007 -> 008 -> 009 -> 010 -> 011A -> 011B -> 012 -> 013 -> 013B -> 014
```

## Backlog Changes

The backlog now reflects:

```text
Technical MVP foundation: complete
Live data validation: complete
Final public release polish: pending
```

The phase structure was updated to reflect the actual implementation path:

```text
Phase 7  — Analytics Marts
  Task 011A

Phase 8  — Streamlit Dashboard
  Task 011B

Phase 9  — Documentation / Demo
  Task 012

Phase 10 — Live Data Validation
  Task 013

Phase 11 — Plan Reconciliation & Clean Baseline
  Task 013B

Phase 12 — Final Polish / Public Release Readiness
  Task 014
```

Outdated warehouse expectations were marked as deferred/future where not implemented in the MVP:

```text
warehouse.wh_skills
warehouse.wh_job_posting_skills
candidate profile version models
skill dictionary version models
advanced inactive job logic
```

Current MVP handles skill demand and relevance logic in marts using rule-based SQL.

---

## Task 013 Commit Boundary

Task 013 was committed separately before Task 013B changes were started.

Expected Task 013 commit command:

```bash
git add src/pipeline/run_data_quality_checks.py reports/task_execution/013-activate-live-france-travail-ingestion-report.md
git commit -m "Complete Task 013 live France Travail ingestion"
```

### Result

```text
COMPLETED LOCALLY BEFORE TASK 013B
```

Task 013B changes were not mixed with Task 013.

---

## Clean Docker Volume Reset

Commands used:

```bash
git status
docker compose down -v
docker compose up -d --build
docker compose ps -a
```

### Final Container Status

After the clean rebuild, the expected services were started successfully:

```text
job_market_radar_postgres            healthy
job_market_radar_airflow_postgres    healthy
job_market_radar_airflow_init        exited 0
job_market_radar_airflow_scheduler   running
job_market_radar_airflow_webserver   running
```

### Result

```text
PASS
```

---

## Reproducibility Fix 1 — PostgreSQL Clean-Volume Bootstrap

### Issue Found

After running:

```bash
docker compose down -v
docker compose up -d --build
```

manual ingestion initially failed with:

```text
psycopg2.errors.UndefinedTable: relation "raw.raw_load_batches" does not exist
```

### Root Cause

The analytical PostgreSQL container started successfully, but the project DDL files were not automatically applied on a clean database volume.

This meant that a clean environment had PostgreSQL running, but the required schemas and raw ingestion tables did not exist.

### Fix

`docker-compose.yml` was updated so the analytical PostgreSQL service mounts project DDL scripts into PostgreSQL's initialization directory:

```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
  - ./sql/ddl:/docker-entrypoint-initdb.d:ro
```

This applies the SQL files on first initialization of a clean PostgreSQL volume.

The fix was applied only to the analytical PostgreSQL service, not to the Airflow metadata PostgreSQL service.

### Validation

After another clean reset and rebuild:

```bash
docker compose down -v
docker compose up -d --build
```

raw tables existed automatically without manual `psql < file.sql` commands:

```bash
docker compose exec postgres psql -U job_market_radar -d job_market_radar -c "\dt raw.*"
```

Result:

```text
raw.raw_api_requests
raw.raw_france_travail_job_postings
raw.raw_load_batches
```

### Result

```text
PASS
```

---

## Live Runtime Configuration

Required local live-mode values:

```text
FRANCE_TRAVAIL_SAMPLE_MODE=false
FRANCE_TRAVAIL_CLIENT_ID=configured locally
FRANCE_TRAVAIL_CLIENT_SECRET=configured locally
FRANCE_TRAVAIL_SEARCH_KEYWORDS=data engineer,analytics engineer
FRANCE_TRAVAIL_MAX_PAGES=1
FRANCE_TRAVAIL_PAGE_SIZE=50
```

Do not commit `.env`.

### Result

```text
PASS
```

---

## Reproducibility Fix 2 — Airflow / Manual Config Parity

### Issue Found

After the first clean live validation, manual ingestion and Airflow ingestion both succeeded, but they did not use the same France Travail runtime configuration.

Evidence:

```text
Manual ingestion:
  requests_made = 2
  records_loaded = 64

Airflow ingestion:
  requests_made = 1
  records_loaded = 50
```

Airflow container environment initially showed only:

```text
FRANCE_TRAVAIL_SAMPLE_MODE=false
```

It did not expose:

```text
FRANCE_TRAVAIL_SEARCH_KEYWORDS
FRANCE_TRAVAIL_MAX_PAGES
FRANCE_TRAVAIL_PAGE_SIZE
```

### Root Cause

France Travail runtime configuration was available to local/manual execution through the local environment, but not fully propagated into Airflow containers.

As a result, Airflow fell back to default ingestion parameters and executed only one search scope.

### Fix

`docker-compose.yml` was updated to pass France Travail runtime variables into the shared Airflow environment configuration:

```yaml
FRANCE_TRAVAIL_SEARCH_KEYWORDS: ${FRANCE_TRAVAIL_SEARCH_KEYWORDS:-data engineer}
FRANCE_TRAVAIL_MAX_PAGES: ${FRANCE_TRAVAIL_MAX_PAGES:-1}
FRANCE_TRAVAIL_PAGE_SIZE: ${FRANCE_TRAVAIL_PAGE_SIZE:-50}
```

The existing Airflow environment already included:

```yaml
FRANCE_TRAVAIL_CLIENT_ID: ${FRANCE_TRAVAIL_CLIENT_ID}
FRANCE_TRAVAIL_CLIENT_SECRET: ${FRANCE_TRAVAIL_CLIENT_SECRET}
FRANCE_TRAVAIL_SAMPLE_MODE: ${FRANCE_TRAVAIL_SAMPLE_MODE:-true}
FRANCE_TRAVAIL_SAMPLE_FILE: ${FRANCE_TRAVAIL_SAMPLE_FILE:-data/sample/france_travail_sample_response.json}
PIPELINE_TRIGGERED_BY: airflow
```

### Validation

After rebuilding the containers, both Airflow webserver and Airflow scheduler exposed the same runtime config:

```bash
docker compose exec airflow-webserver bash -lc "printenv | grep -E 'FRANCE_TRAVAIL_SAMPLE_MODE|FRANCE_TRAVAIL_SEARCH_KEYWORDS|FRANCE_TRAVAIL_MAX_PAGES|FRANCE_TRAVAIL_PAGE_SIZE'"
```

```bash
docker compose exec airflow-scheduler bash -lc "printenv | grep -E 'FRANCE_TRAVAIL_SAMPLE_MODE|FRANCE_TRAVAIL_SEARCH_KEYWORDS|FRANCE_TRAVAIL_MAX_PAGES|FRANCE_TRAVAIL_PAGE_SIZE'"
```

Result for both services:

```text
FRANCE_TRAVAIL_SAMPLE_MODE=false
FRANCE_TRAVAIL_PAGE_SIZE=50
FRANCE_TRAVAIL_SEARCH_KEYWORDS=data engineer,analytics engineer
FRANCE_TRAVAIL_MAX_PAGES=1
```

### Final Config Parity Validation

After a final clean rebuild, both manual ingestion and Airflow ingestion used two search scopes:

```text
france_travail:data_engineer:any_location:a1963ca104ff
france_travail:analytics_engineer:any_location:1f82d1a8fbc0
```

Manual batch:

```text
batch_id: eb516a38-89f4-4682-a450-b6de810e315e
records_loaded: 64
requests_made: 2
```

Airflow batch:

```text
batch_id: 390e3648-13f7-4f0b-a22a-316fcd59c079
records_loaded: 64
requests_made: 2
```

Raw API request validation:

```text
eb516a38-89f4-4682-a450-b6de810e315e | france_travail:data_engineer:any_location:a1963ca104ff      | page=1 | page_size=50 | status=206
eb516a38-89f4-4682-a450-b6de810e315e | france_travail:analytics_engineer:any_location:1f82d1a8fbc0 | page=1 | page_size=50 | status=200
390e3648-13f7-4f0b-a22a-316fcd59c079 | france_travail:data_engineer:any_location:a1963ca104ff      | page=1 | page_size=50 | status=206
390e3648-13f7-4f0b-a22a-316fcd59c079 | france_travail:analytics_engineer:any_location:1f82d1a8fbc0 | page=1 | page_size=50 | status=200
```

### Result

```text
PASS
```

---

## Clean Live Ingestion Result

Command:

```bash
python -m src.pipeline.run_france_travail_ingestion
```

### Result

```json
{
  "batch_id": "eb516a38-89f4-4682-a450-b6de810e315e",
  "status": "success",
  "requests_made": 2,
  "successful_requests": 2,
  "failed_requests": 0,
  "records_loaded": 64,
  "error_message": null
}
```

### Result

```text
PASS
```

---

## Raw Table Counts

### Final Validated Batch Results

| Metric | Manual Batch | Airflow Batch |
|---|---:|---:|
| Batch ID | `eb516a38-89f4-4682-a450-b6de810e315e` | `390e3648-13f7-4f0b-a22a-316fcd59c079` |
| Records loaded | 64 | 64 |
| Requests made | 2 | 2 |
| Failed requests | 0 | 0 |

### Final Request Scope Validation

| Batch | Search scope | Page | Page size | HTTP status |
|---|---|---:|---:|---:|
| Manual | `france_travail:data_engineer:any_location:a1963ca104ff` | 1 | 50 | 206 |
| Manual | `france_travail:analytics_engineer:any_location:1f82d1a8fbc0` | 1 | 50 | 200 |
| Airflow | `france_travail:data_engineer:any_location:a1963ca104ff` | 1 | 50 | 206 |
| Airflow | `france_travail:analytics_engineer:any_location:1f82d1a8fbc0` | 1 | 50 | 200 |

### Notes

The final raw job posting total was not explicitly re-queried after the final Airflow run, but the two successful batches report 64 records each. Therefore, the expected final raw job posting total is 128 rows.

The final `wh_job_posting_current` count is expected to remain 64 current jobs because the same live search scopes were loaded twice during validation. Snapshot rows are expected to include both observations after the Airflow `dbt_build`.

---

## dbt Build Result

Command:

```bash
dbt build --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar
```

### Manual dbt Build Result

```text
Completed successfully
Done. PASS=144 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=144
```

### Summary

```text
PASS: 144
WARN: 0
ERROR: 0
SKIP: 0
NO-OP: 0
TOTAL: 144
```

### Non-Blocking Warning

The following dbt warning was observed:

```text
Configuration paths exist in your dbt_project.yml file which do not apply to any resources.
There are 1 unused configuration paths:
- seeds.job_market_radar
```

This does not block Task 013B. It should be cleaned up during Task 014 final polish.

---

## Data Quality Result

Command:

```bash
python -m src.pipeline.run_data_quality_checks
```

### Result

```text
Data quality checks completed successfully.
```

The data quality runner executed dbt parse and dbt build over the selected raw sources, staging models, warehouse models, marts, and tests.

### Summary

```text
PASS=144 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=144
```

### Non-Blocking Warnings

The data quality runner surfaced two non-blocking warnings:

```text
MissingArgumentsPropertyInGenericTestDeprecation
```

in:

```text
models/marts/mart_compatibility.yml
```

and:

```text
Configuration paths exist in your dbt_project.yml file which do not apply to any resources.
- seeds.job_market_radar
```

These warnings do not block the clean live baseline. They should be addressed during Task 014 final polish.

### Result

```text
PASS
```

---

## Streamlit Clean Live Validation Result

Command:

```bash
streamlit run streamlit_app/app.py
```

Validated pages:

```text
App / Home
Overview
Relevant Jobs
Skill Radar
Locations
Companies
Weekly Report
Data Freshness
```

### Dashboard Metrics Observed During Clean Live Validation

| Metric | Value |
|---|---:|
| Current jobs | 64 |
| Active jobs | 64 |
| Relevant jobs | 16 |
| High-match jobs | 2 |
| Junior-friendly jobs | 9 |
| Companies | 45 |
| Locations | 43 |
| Average relevance score | 41.2 |
| Latest manual batch ID | `e47a3904-cdf7-46e6-a877-feb58cfacc9f` |
| Manual records loaded | 64 |
| Manual requests made | 2 |
| Snapshot rows at first Streamlit validation | 64 |

### Notes

Streamlit was validated on clean live data before the Airflow config parity fix was added.

The Airflow config parity fix only changed environment propagation for Airflow containers and did not modify Streamlit code or marts. The final clean rebuild after that fix successfully rebuilt marts through both manual dbt and Airflow dbt paths.

Screenshots are intentionally deferred to Task 014 final polish.

### Non-Blocking Warning

Streamlit emitted the following deprecation warning:

```text
Please replace `use_container_width` with `width`.
```

This does not block Task 013B. It should be addressed during Task 014 final polish.

### Result

```text
PASS
```

---

## Airflow Live Validation Result

Commands:

```bash
docker compose exec airflow-webserver airflow dags unpause job_market_radar
docker compose exec airflow-webserver airflow dags trigger job_market_radar --run-id task_013B_final_clean_live_validation
docker compose exec airflow-webserver airflow tasks states-for-dag-run job_market_radar task_013B_final_clean_live_validation
```

### Final DAG State

```text
start: success
ingest_france_travail_raw_jobs: success
dbt_build: success
run_data_quality_checks: success
generate_weekly_report: success
end: success
```

### Detailed Final Task States

```text
start                          success
ingest_france_travail_raw_jobs success
dbt_build                      success
run_data_quality_checks        success
generate_weekly_report         success
end                            success
```

### Retry Note

During the final Airflow validation, `dbt_build` initially entered `up_for_retry`, then completed successfully on retry.

Final DAG state was all tasks successful.

No code change was required after the retry because the final validated state passed.

### Result

```text
PASS
```

---

## Issues Encountered

### 1. Analytical PostgreSQL did not auto-bootstrap schemas/tables after clean volume reset

**Status:** fixed.

**Symptom:** ingestion failed because `raw.raw_load_batches` did not exist.

**Root cause:** project DDL was not mounted into the PostgreSQL initialization directory.

**Fix:** mounted `./sql/ddl` to `/docker-entrypoint-initdb.d:ro` for the analytical PostgreSQL service.

**Validation:** clean rebuild automatically created raw tables.

---

### 2. Manual ingestion and Airflow ingestion used different France Travail runtime config

**Status:** fixed.

**Symptom:** manual ingestion made 2 API requests, while Airflow ingestion initially made only 1.

**Root cause:** Airflow containers did not receive `FRANCE_TRAVAIL_SEARCH_KEYWORDS`, `FRANCE_TRAVAIL_MAX_PAGES`, and `FRANCE_TRAVAIL_PAGE_SIZE`.

**Fix:** added those variables to the shared Airflow environment configuration in `docker-compose.yml`.

**Validation:** final clean rebuild showed both manual and Airflow batches using 2 requests and the same search scopes.

---

### 3. Airflow `dbt_build` entered retry before final success

**Status:** non-blocking.

**Symptom:** during the final Airflow validation, `dbt_build` was temporarily observed as `up_for_retry`.

**Resolution:** after waiting and checking the DAG state again, `dbt_build` and all downstream tasks completed successfully.

**Final state:** all Airflow tasks success.

---

### 4. Non-blocking polish warnings

**Status:** deferred to Task 014.

Observed warnings:

```text
dbt unused config path: seeds.job_market_radar
dbt MissingArgumentsPropertyInGenericTestDeprecation in mart_compatibility.yml
Streamlit use_container_width deprecation warning
```

These warnings do not block Task 013B, but should be cleaned up before final public release.

---

## Final Acceptance Status

```text
PASS
```

Task 013B is accepted.

The repository task plan and the actual implementation history are synchronized.

The project now has a validated clean live-data baseline:

```text
Clean Docker volume reset: PASS
Docker rebuild: PASS
PostgreSQL DDL auto-bootstrap: PASS
Airflow France Travail config parity: PASS
Manual live ingestion: PASS
Manual dbt build: PASS
Manual data quality checks: PASS
Streamlit clean live validation: PASS
Airflow live ingestion: PASS
Airflow dbt build: PASS
Airflow data quality checks: PASS
Airflow weekly report task: PASS
Final Airflow DAG state: PASS
```

The project is ready to move to final public release polish.

---

## Recommended Next Task

```text
Task 014 — Final Polish / Public Release Readiness
```

Recommended Task 014 focus:

```text
clean non-blocking dbt warnings
clean Streamlit deprecation warnings
capture final screenshots
polish README / demo docs
verify GitHub presentation quality
prepare public project narrative
commit final public release version
```
