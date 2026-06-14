# Phase 2: Adzuna Source Integration and Airflow Validation

Phase 2 added Adzuna as a second job source alongside France Travail and validated the
Dockerized ELT workflow end to end.

The project now supports two public job APIs, preserves raw responses, normalizes both
sources through dbt, exposes source-level analytics in the dashboard layer, and runs the
pipeline through Airflow in Docker.

---

## Final Validation State

| Metric | Result |
|---|---|
| France Travail current jobs | 64 |
| Adzuna current jobs | 100 |
| Combined relevant jobs mart | 164 |
| dbt build | PASS=187 WARN=0 ERROR=0 SKIP=0 |
| Data quality runner | Pass |
| Airflow DAG tasks passed | 7 / 7 |

Snapshot row counts are higher than current-state counts because manual ingestion and the
Airflow DAG both ran during validation. Each run created a new snapshot batch. The current
warehouse model deduplicates by source job key and represents the latest state.

---

<details>
<summary><strong>Implementation summary</strong></summary>

## What changed

Phase 2 introduced a complete second-source ingestion path for Adzuna and connected it to
the existing layered architecture.

Main changes:

- Added Adzuna raw table DDL.
- Added an Adzuna ingestion package with authentication, request building, API client,
  parser, and package exports.
- Added an Adzuna pipeline runner.
- Added sample Adzuna API data for local validation without live credentials.
- Extended the raw loader so it can write both France Travail and Adzuna job postings.
- Registered Adzuna as a dbt source.
- Added an Adzuna staging model and tests.
- Updated warehouse models to combine both source-specific staging models.
- Updated data tests for multi-source warehouse lineage and accepted source values.
- Exposed `source_name` in dashboard-ready outputs.
- Updated Streamlit pages so source visibility and freshness work with both sources.
- Stabilized the Dockerized Airflow runtime so dbt can run reliably inside the Airflow
  container.
- Updated README and release documentation to describe the implemented Phase 2 state.

## Source coverage

| Source | Status | Notes |
|---|---|---|
| France Travail | Implemented | Existing source from the MVP |
| Adzuna | Implemented in Phase 2 | Added as the second job source |
| The Muse | Future option | Not implemented in Phase 2 |

</details>

---

<details>
<summary><strong>Component changes</strong></summary>

## Ingestion

The new Adzuna ingestion path follows the same general shape as the France Travail
ingestion path.

Implemented components:

- `src/ingestion/adzuna/auth.py`
- `src/ingestion/adzuna/client.py`
- `src/ingestion/adzuna/parser.py`
- `src/ingestion/adzuna/request_builder.py`
- `src/ingestion/adzuna/__init__.py`
- `src/pipeline/run_adzuna_ingestion.py`

The Adzuna API uses query-parameter authentication. Credentials are read from environment
variables and are not stored in repository files.

Sample mode is supported through `ADZUNA_SAMPLE_MODE`, allowing local validation without
depending on live API availability.

## Raw layer

Added:

- `raw.raw_adzuna_job_postings`

The raw layer preserves Adzuna source payloads as JSONB, consistent with the France Travail
raw ingestion approach.

## dbt staging

Added:

- `staging.stg_adzuna_job_postings`

This model normalizes Adzuna-specific JSON fields into the shared staging shape used by
the warehouse layer.

Examples of normalized source fields:

- job title
- company display name
- location display name
- redirect URL
- source job identifier
- source name

## dbt warehouse

Updated:

- `warehouse.wh_job_posting_snapshots`
- `warehouse.wh_job_posting_current`

The warehouse snapshot model now combines France Travail and Adzuna staging models. The
current-state model keeps one latest row per source job key.

Data tests were updated so accepted `source_name` values and lineage checks support both
sources.

## dbt marts

The mart layer continues to consume the warehouse current-state model.

Relevant marts now receive both sources through the shared warehouse layer:

- `marts.mart_job_postings_current`
- `marts.mart_relevant_jobs`
- `marts.mart_data_freshness`
- skill, location, company, and weekly summary marts

`marts.mart_data_freshness` has one row per source, so source-level freshness can be
monitored independently.

## Airflow

The DAG now runs both ingestion tasks before dbt transformation and data quality checks.

Expected flow:

```text
start
  -> [ingest_france_travail_raw_jobs, ingest_adzuna_raw_jobs]
  -> dbt_build
  -> run_data_quality_checks
  -> generate_weekly_report
  -> end
```

The Airflow image was also stabilized so it can run dbt correctly inside Docker.

Key runtime improvements:

- git is installed in the Airflow image.
- dbt runs from a dedicated virtual environment.
- dbt commands use explicit project, profiles, target, and log paths.
- service container names are not hardcoded, reducing local Docker naming conflicts.

## Streamlit

Updated pages and data access so source-level information is visible in the dashboard
layer.

Main improvements:

- Relevant Jobs page can display and filter by source.
- Data Freshness page displays per-source freshness metrics.
- Database access uses the shared project configuration path.

</details>

---

<details>
<summary><strong>Validation details</strong></summary>

## Live Adzuna validation

During live-source validation, Adzuna was run with live API credentials and loaded 200 raw
job records into the Adzuna raw table.

That validation confirmed:

- live Adzuna API access works
- the Adzuna raw loader works
- Adzuna staging compiles and tests correctly
- warehouse lineage tests support multiple sources
- dbt build completes successfully with both sources present

## Final Dockerized validation

Final validation was performed from a clean Dockerized runtime.

| Check | Result |
|---|---|
| Application PostgreSQL service | Healthy |
| Raw DDL application | Pass |
| Airflow image build | Clean |
| git inside Airflow container | Available |
| dbt debug inside Airflow container | Pass |
| Manual France Travail ingestion | 64 jobs |
| Manual Adzuna ingestion | 100 jobs |
| Manual dbt build | PASS=187 WARN=0 ERROR=0 SKIP=0 |
| Manual data quality runner | Pass |
| Airflow DAG end to end | 7 / 7 tasks |

## Airflow DAG task results

| Task | Result |
|---|---|
| start | success |
| ingest_france_travail_raw_jobs | success |
| ingest_adzuna_raw_jobs | success |
| dbt_build | success |
| run_data_quality_checks | success |
| generate_weekly_report | success |
| end | success |

## Final data state

| Table or mart | Count |
|---|---|
| warehouse.wh_job_posting_current, France Travail | 64 rows |
| warehouse.wh_job_posting_current, Adzuna | 100 rows |
| marts.mart_relevant_jobs | 164 rows |
| warehouse.wh_job_posting_snapshots, France Travail | 128 rows |
| warehouse.wh_job_posting_snapshots, Adzuna | 200 rows |

The current-state and mart counts are the main validation signal for the dashboard layer.
The snapshot counts are expected to be larger because multiple ingestion runs were kept as
historical observations.

</details>

---

<details>
<summary><strong>Open limitations</strong></summary>

- Streamlit UI browser validation was not repeated during the final Phase 2 validation.
  The code path and mart outputs were verified, but a live browser check is still
  recommended.
- Live API mode requires valid France Travail and Adzuna credentials in `.env`.
- Dataset size depends on API availability, rate limits, and configured page counts.
- Skill extraction remains rule-based and may miss synonyms or produce false positives.
- Candidate Fit Score remains rule-based and deterministic. It is not a machine learning
  recommendation model.
- Candidate Profile v1 is hardcoded for the MVP and does not yet support multiple users or
  UI-based configuration.
- Deployment is not in scope for this local MVP.
- No LinkedIn or Indeed scraping is used.

</details>
