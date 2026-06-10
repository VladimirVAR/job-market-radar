# Data Flow

## Purpose

This document describes how data moves through Job Market Radar from public job APIs to dashboard-ready analytical outputs.

The required architecture baseline is:

```text
sources -> raw -> staging -> warehouse -> marts -> dashboard / reports
```

---

## End-to-End Flow

```text
[1] Airflow DAG starts
    |
    v
[2] Python ingestion creates a load batch
    |
    v
[3] Python builds API requests for configured search scopes
    |
    v
[4] Python calls France Travail API
    |
    v
[5] Python stores API request metadata
    |
    v
[6] Python stores raw job posting payloads as JSONB
    |
    v
[7] dbt builds staging models
    |
    v
[8] dbt builds warehouse snapshot and current-state models
    |
    v
[9] dbt builds marts
    |
    v
[10] Data quality checks run
    |
    v
[11] Streamlit reads marts
    |
    v
[12] Markdown reports are generated
```

---

## Source Layer

### MVP Source

- France Travail API Offres d'emploi

### Future Sources

- Adzuna API
- The Muse API

### Excluded from MVP

- LinkedIn scraping
- Indeed scraping
- Any source that violates website Terms of Service

---

## Raw Flow

The raw layer is loaded by Python.

For every pipeline run:

1. A row is created in `raw.raw_load_batches`.
2. For every API request or API page, a row is created in `raw.raw_api_requests`.
3. For every returned job posting, a row is created in `raw.raw_france_travail_job_postings`.
4. Raw job posting payloads are stored as JSONB.
5. Each raw row keeps `batch_id`, `request_id`, `source_job_id`, `source_job_key`, and `search_scope_key`.

Raw data should not be overwritten or transformed in place.

---

## Staging Flow

The staging layer is built by dbt.

Staging models:

- parse JSON fields
- cast data types
- normalize column names
- standardize source-specific values
- extract useful raw fields into typed columns
- keep lineage back to raw rows

Example:

```text
raw.raw_france_travail_job_postings
  -> staging.stg_france_travail_job_postings
```

---

## Warehouse Flow

The warehouse layer is built by dbt.

Warehouse models create canonical analytical structures:

```text
staging.stg_france_travail_job_postings
  -> warehouse.wh_job_posting_snapshots
  -> warehouse.wh_job_posting_current
```

The warehouse layer also supports:

- companies
- locations
- skills
- job-skill bridges
- candidate profile versions
- skill dictionary versions

---

## Marts Flow

The marts layer is built by dbt and consumed by Streamlit.

Marts should be dashboard-ready.

Main marts:

```text
marts.mart_relevant_jobs
marts.mart_skill_demand
marts.mart_missing_skills
marts.mart_location_activity
marts.mart_company_activity
marts.mart_weekly_market_summary
```

---

## Dashboard Flow

Streamlit reads from marts.

Business pages should not query raw or staging tables.

Allowed:

```text
Streamlit -> marts.mart_relevant_jobs
Streamlit -> marts.mart_skill_demand
Streamlit -> marts.mart_weekly_market_summary
```

Avoid:

```text
Streamlit -> raw.raw_france_travail_job_postings
Streamlit calculates relevance_score directly
```

A technical freshness/debug page may read `raw.raw_load_batches`, but business logic should stay in dbt marts.

---

## Batch Flow

Every pipeline run has a `batch_id`.

The `batch_id` is created before API calls start and is carried through:

```text
raw.raw_load_batches.batch_id
  -> raw.raw_api_requests.batch_id
  -> raw.raw_france_travail_job_postings.batch_id
  -> staging models
  -> warehouse snapshots
  -> marts where needed
```

This allows the system to answer:

- Which pipeline run loaded this data?
- Which API request produced this job posting?
- Which raw payload generated this current job?
- Which batch introduced this job?
- When was this job last seen?

---

## Request Metadata Flow

Every API call should be stored in `raw.raw_api_requests`.

The request metadata includes:

- source name
- endpoint
- request parameters
- search scope
- page number
- response status
- response time
- error message if applicable

This is required for debugging, reproducibility, and lineage.

---

## Search Scope Flow

`search_scope_key` identifies a comparable search configuration.

Example:

```text
france_travail:data_engineer:france:remote_any
france_travail:etl_developer:paris:remote_any
```

It is important because disappearing jobs can only be interpreted inside the same search scope.

A job missing from a different search scope should not be considered inactive.

---

## Snapshot and Current-State Flow

Snapshots preserve historical observations.

Current-state models expose the latest known state.

```text
warehouse.wh_job_posting_snapshots
  -> warehouse.wh_job_posting_current
```

If a job appears in multiple batches, it has multiple snapshot rows.

If a job is not observed in the latest comparable search scope, it may be marked as inactive.

---

## Skill Extraction Flow

Skill extraction is done after staging.

MVP approach:

```text
warehouse.wh_job_posting_snapshots
  + warehouse.wh_skill_dictionary_versions
  -> warehouse.wh_job_posting_skills
```

The MVP uses rule-based dictionary matching.

This keeps the logic transparent and explainable.

---

## Relevance Scoring Flow

Relevance scoring is done in marts, not in Streamlit.

```text
warehouse.wh_job_posting_current
  + warehouse.wh_job_posting_skills
  + warehouse.wh_candidate_profile_versions
  -> marts.mart_relevant_jobs
```

The mart should include:

- matched skills
- missing skills
- relevance score
- relevance reason
- junior-friendly indicator

---

## Validation Flow

Validation should happen at multiple points:

```text
raw validation
  -> staging validation
  -> warehouse validation
  -> marts validation
```

Examples:

- raw payload is not null
- source job id is not null
- one current row per canonical job key
- relevance score is between 0 and 100
- marts are not empty after a successful run

Airflow task success does not guarantee data correctness.

A separate validation step should exist in the pipeline.

---

## Summary

The data flow is intentionally simple and explicit.

Python loads raw data.

dbt transforms data.

Airflow orchestrates.

Streamlit consumes marts.

This separation keeps the project understandable, testable, and demo-friendly.
