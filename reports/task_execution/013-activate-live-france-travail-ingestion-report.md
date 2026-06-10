# Task 013 Execution Report — Activate Live France Travail API Ingestion

## Role

Source / Ingestion + Pipeline Validation Engineer

## Task

Task 013 — Activate Live France Travail API Ingestion

## Objective

Validate that the Job Market Radar MVP works with real France Travail job market data, not only with sample-mode data.

The required live-data flow was:

```text
live France Travail API
  -> raw PostgreSQL tables
  -> dbt staging
  -> dbt warehouse
  -> dbt marts
  -> data quality checks
  -> Streamlit dashboard
```

---

## Summary

Task 013 was completed successfully.

The project was switched from sample-mode validation to live France Travail API validation.

Real job postings from France Travail successfully passed through the full local MVP pipeline and appeared in the Streamlit dashboard.

This confirms that the project is no longer only a sample-mode technical demo. The MVP foundation has now been validated with real France Travail job market data.

Final status:

```text
ACCEPTED — Real France Travail job data successfully passed through the full Job Market Radar pipeline and appeared in the Streamlit dashboard.
```

---

## Live-mode Configuration

Local `.env` was configured for live mode.

Important configuration:

```text
FRANCE_TRAVAIL_SAMPLE_MODE=false
FRANCE_TRAVAIL_SEARCH_KEYWORDS=data engineer,analytics engineer
FRANCE_TRAVAIL_LOCATIONS=
FRANCE_TRAVAIL_CONTRACT_TYPES=
FRANCE_TRAVAIL_REMOTE_VALUES=
FRANCE_TRAVAIL_MAX_PAGES=1
FRANCE_TRAVAIL_PAGE_SIZE=50
```

France Travail API credentials were configured locally:

```text
FRANCE_TRAVAIL_CLIENT_ID=configured locally
FRANCE_TRAVAIL_CLIENT_SECRET=configured locally
```

No API secrets were committed to the repository.

---

## France Travail API Access

A France Travail.io application was created and configured.

```text
Application name: Job Market Radar
Authorized API: Offres d'emploi v2
Rate limit shown in France Travail.io: 10 calls / second
```

The selected API matches the MVP source requirement:

```text
Offres d'emploi v2
```

No additional APIs or sources were added during this task.

---

## Live Ingestion Run

The live ingestion command was run from the repository root:

```bash
python -m src.pipeline.run_france_travail_ingestion
```

Successful live run result:

```text
batch_id: 81bb5c6c-d7a9-4ebe-8a10-67f52d28ffee
status: success
requests_made: 2
successful_requests: 2
failed_requests: 0
records_loaded: 64
error_message: null
```

This confirms that the Python ingestion layer:

* authenticated against the live France Travail API
* executed configured live searches
* stored API request metadata
* loaded raw job posting payloads into PostgreSQL
* created a successful live load batch

---

## Raw Table Validation

Raw tables were inspected after the live ingestion run.

Confirmed results:

```text
raw.raw_load_batches:
latest live batch status = success
records_loaded = 64
requests_made = 2

raw.raw_api_requests:
api_request_count for latest live batch = 2

raw.raw_france_travail_job_postings:
row_count for latest live batch = 64
total raw job postings in table = 78
```

The latest live run created:

```text
1 batch row
2 API request rows
64 raw job posting rows
```

Batch/request/raw lineage was preserved through:

```text
batch_id
request_id
source_job_key
search_scope_key
```

---

## Full dbt Build Result

The full dbt build command was run:

```bash
dbt build --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar
```

Result:

```text
Completed successfully
PASS=144
WARN=0
ERROR=0
SKIP=0
TOTAL=144
```

dbt successfully built and tested:

```text
sources
staging
warehouse
marts
custom tests
```

This confirms that live France Travail data is compatible with the current dbt models.

---

## Data Quality Checks

The data quality command was run:

```bash
python -m src.pipeline.run_data_quality_checks
```

### Initial Issue

The first data quality run failed, but the issue was not caused by live data.

Failure reason:

```text
mart tests were being selected,
but mart models were not being built by the data quality runner selector.
```

The failing relations were:

```text
marts.mart_data_freshness
marts.mart_job_postings_current
marts.mart_skill_demand
```

Root cause:

```text
src/pipeline/run_data_quality_checks.py selected:
source:* path:models/staging path:models/warehouse path:tests

This included mart tests through path:tests,
but did not build path:models/marts first.
```

### Compatibility Fix Applied

The dbt selector in `src/pipeline/run_data_quality_checks.py` was updated.

Before:

```text
source:* path:models/staging path:models/warehouse path:tests
```

After:

```text
source:* path:models/staging path:models/warehouse path:models/marts path:tests
```

### Final Data Quality Result

After the selector fix, the data quality run completed successfully:

```text
Data quality checks completed successfully.
PASS=144
WARN=0
ERROR=0
SKIP=0
TOTAL=144
```

This confirms that the validation runner now correctly validates the full path:

```text
raw -> staging -> warehouse -> marts
```

---

## Streamlit Dashboard Validation

Streamlit was run with:

```bash
streamlit run streamlit_app/app.py
```

The dashboard connected successfully to PostgreSQL and displayed live data from marts.

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

Observed live dashboard metrics:

```text
Active jobs: 66
Relevant jobs: 18
Junior-friendly jobs: 10
Average relevance: 42.5
Companies: 47
Locations: 43
```

Data Freshness page confirmed the latest live batch:

```text
latest batch: 81bb5c6c-d7a9-4ebe-8a10-67f52d28ffee
records loaded: 64
requests made: 2
snapshot rows: 78
current jobs: 66
```

The dashboard displayed:

* live job postings
* skill demand
* location distribution
* company distribution
* weekly report metrics
* latest batch freshness

No blocking Streamlit runtime errors were observed.

---

## Airflow Validation

Airflow live run was not executed during this task.

Reason:

```text
Manual live validation confirmed the full data path from live France Travail API to Streamlit dashboard.
Airflow orchestration had already been implemented and validated in previous MVP tasks.
```

Recommendation:

```text
Run an optional Airflow live validation later if the team wants orchestration-level confirmation using live credentials inside the Airflow container environment.
```

This is not considered a blocker for Task 013 acceptance.

---

## Files Changed

Modified file:

```text
src/pipeline/run_data_quality_checks.py
```

Reason:

```text
The data quality runner needed to build marts before running mart-level tests.
```

New report file:

```text
reports/task_execution/013-activate-live-france-travail-ingestion-report.md
```

No `.env` file was committed.

No secrets were committed.

No dashboard logic was changed.

No dbt business logic was changed.

No relevance scoring logic was changed.

No new data source was added.

---

## Issues and Observations

### Resolved Issue: Windows Environment Variables

Initial local run did not detect France Travail credentials because the `.env` file was not automatically loaded into the Windows CMD environment.

Resolution:

```text
Credentials were exported manually into the CMD session using set commands.
```

Recommendation:

```text
Consider adding explicit .env loading through python-dotenv or documenting the Windows run procedure clearly.
```

### Resolved Issue: Data Quality Selector

Data Quality initially failed because mart tests were executed without building mart models.

Resolution:

```text
Added path:models/marts to the dbt selector in run_data_quality_checks.py.
```

### Non-blocking dbt Warnings

dbt showed non-blocking warnings:

```text
MissingArgumentsPropertyInGenericTestDeprecation
unused configuration path: seeds.job_market_radar
```

These warnings did not block Task 013 and can be handled during Final Polish.

### Security Note

France Travail API credentials were used locally and must remain out of Git and public documentation.

Recommendation:

```text
Rotate the France Travail client secret after the live validation session if the secret was exposed during troubleshooting.
```

---

## Data Interpretation Note

The latest live batch loaded 64 records, while the total raw table contained 78 job posting rows and the dashboard showed 66 current jobs.

This is expected in the current local development database because earlier sample/test runs may still be present and warehouse current-state models deduplicate job postings by current keys.

Before final screenshots or public public project presentation, consider performing a clean live-only validation run to avoid mixing sample/test records with live data.

---

## Acceptance Criteria

Confirmed:

```text
live API credentials configured locally
FRANCE_TRAVAIL_SAMPLE_MODE=false
live ingestion ran without sample data
raw.raw_load_batches received a new successful live batch
raw.raw_api_requests contains live request metadata
raw.raw_france_travail_job_postings contains real France Travail job postings
dbt build succeeds on live data
data quality checks pass after selector compatibility fix
marts contain dashboard-ready data
Streamlit displays real job market data
Data Freshness reflects the latest live run
issues and limitations were documented honestly
```

Task 013 acceptance criteria are met.

---

## Recommended Next Steps

Recommended next task:

```text
Task 014 — Final Polish / Public Release Readiness
```

Before final public polish, recommended optional checks:

1. Run Airflow live validation with live credentials inside the Airflow environment.
2. Perform a clean live-only run before taking final screenshots.
3. Rotate the France Travail client secret if it was exposed during local troubleshooting.
4. Address non-blocking dbt warnings during polish.
5. Update documentation if the Windows `.env` loading procedure needs clarification.
