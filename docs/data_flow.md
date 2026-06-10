# Data Flow

## Purpose

This document describes how data moves through Job Market Radar from source collection to dashboard-ready analytical outputs.

The baseline flow is:

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
[4] Python calls France Travail API or loads sample data
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
[12] Markdown reports may be generated
```

---

## 1. Source Extraction

The MVP source is France Travail API Offres d'emploi.

The project may also run in sample mode for repeatable local validation.

Future sources may include:

- Adzuna API
- The Muse API

Excluded from MVP:

- LinkedIn scraping
- Indeed scraping
- Any non-compliant scraping

---

## 2. Load Batch Creation

Every pipeline run starts by creating a row in:

```text
raw.raw_load_batches
```

Grain:

```text
one row per pipeline execution
```

The generated `batch_id` is propagated through raw, staging, warehouse, and selected marts.

This allows the project to answer:

- Which run loaded this data?
- How many requests were made?
- How many records were loaded?
- Did the latest run succeed?
- Which jobs were first or last seen in a run?

---

## 3. API Request Tracking

Every API request, page, or search parameter set is stored in:

```text
raw.raw_api_requests
```

Grain:

```text
one row per API request, page, or search parameter set
```

Tracked metadata includes:

- `request_id`
- `batch_id`
- `source_name`
- `endpoint`
- `request_params_json`
- `search_scope_key`
- `page_number`
- `response_status_code`
- `response_time_ms`
- `error_message`

This helps with debugging, reproducibility, and lineage.

---

## 4. Raw Job Loading

Every raw job posting payload is stored in:

```text
raw.raw_france_travail_job_postings
```

Grain:

```text
one raw job posting payload per source job per request per batch
```

Key fields:

- `batch_id`
- `request_id`
- `source_job_id`
- `source_job_key`
- `search_scope_key`
- `raw_payload_json`
- `payload_hash`
- `ingested_at`

The raw payload is stored as JSONB.

Raw rows are not overwritten or transformed in place.

---

## 5. Staging Transformation

dbt builds:

```text
staging.stg_france_travail_job_postings
```

Grain:

```text
one cleaned France Travail job posting per source job per batch
```

Staging responsibilities:

- Parse raw JSON fields.
- Cast values into expected data types.
- Normalize column names.
- Extract job title, company, location, contract type, work mode, seniority, description, and dates.
- Preserve raw lineage columns.

Staging should not calculate final business metrics.

---

## 6. Warehouse Transformation

dbt builds canonical warehouse models:

```text
warehouse.wh_job_posting_snapshots
warehouse.wh_job_posting_current
```

### Snapshots

Grain:

```text
one canonical job posting observation per source job per batch
```

Snapshots allow historical analysis and change detection.

### Current state

Grain:

```text
one row per latest known canonical job posting
```

Current-state models support dashboard pages that need the latest known job status.

---

## 7. Skill Extraction

The MVP uses rule-based skill extraction.

Conceptual flow:

```text
warehouse job postings
  + skill dictionary
  -> detected job skills
```

This approach is intentionally simple and explainable.

Limitations:

- It may miss synonyms.
- It may produce false positives.
- It requires dictionary maintenance.

---

## 8. Relevance Scoring

Relevance scoring is calculated in dbt marts, not in Streamlit.

Conceptual flow:

```text
current jobs
  + detected skills
  + candidate profile
  -> marts.mart_relevant_jobs
```

The mart should expose:

- matched candidate skills
- missing growth skills
- relevance score
- relevance reason
- junior-friendly indicator

---

## 9. Marts

Marts are product-facing analytical outputs.

Important marts:

- `marts.mart_relevant_jobs`
- `marts.mart_skill_demand`
- `marts.mart_missing_skills`
- `marts.mart_location_activity`
- `marts.mart_company_activity`
- `marts.mart_weekly_market_summary`
- `marts.mart_data_freshness`

Marts are the contract between dbt and Streamlit.

---

## 10. Dashboard Consumption

Streamlit reads from marts for business pages.

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
Streamlit calculates skill demand directly
```

This keeps the dashboard simple and makes metrics reusable outside the UI.

---

## 11. Validation Flow

Validation happens across layers:

```text
raw validation
  -> staging validation
  -> warehouse validation
  -> marts validation
```

Examples:

- latest successful batch exists
- raw payload is not null
- source job key is not null
- current model has one row per canonical job key
- relevance score is between 0 and 100
- marts are not empty after a successful run

Airflow task success does not guarantee data correctness, so validation is a separate pipeline step.

---

## Summary

The flow is intentionally explicit:

```text
Python handles extraction and raw loading.
dbt handles transformations and marts.
Airflow handles orchestration.
Streamlit handles presentation.
Validation checks protect trust in the outputs.
```
