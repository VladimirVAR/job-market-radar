# Task 007: Build Staging Models

## Goal

Build dbt staging models for France Travail job postings.

Staging models should parse raw JSON into typed, cleaned, source-specific columns.

---

## Context

The staging layer is the first transformation layer after raw loading.

It should not contain final business metrics.

---

## Deliverables

Create:

```text
dbt_job_market_radar/models/staging/france_travail/stg_france_travail_job_postings.sql
dbt_job_market_radar/models/staging/france_travail/stg_france_travail_job_postings.yml
```

---

## Model: `stg_france_travail_job_postings`

**Grain:** one cleaned France Travail job posting per source job per batch.

Required fields:

```text
batch_id
request_id
raw_job_posting_id
source_name
source_job_id
source_job_key
search_scope_key
job_title
company_name
location_raw
city
region
country
contract_type
work_mode
seniority_level
description_text
published_at
updated_at
retrieved_at
source_url
payload_hash
```

---

## Required Tests

Add dbt tests for:

```text
source_job_key not null
batch_id not null
request_id not null
raw_job_posting_id not null
job_title not null where practical
payload_hash not null
```

---

## Acceptance Criteria

- `dbt build --select staging` succeeds.
- Staging model reads from `source('raw', 'raw_france_travail_job_postings')`.
- JSON fields are parsed into typed columns.
- Field names use English and `snake_case`.
- Model grain is documented.
- Staging model preserves raw lineage columns.

---

## Implementation Notes

Do not over-normalize in staging.

Keep source-specific assumptions documented.

If a field is unreliable or missing from the source, allow nulls and document it.

---

## Dependencies

Task 006.

---

## Next Task

Task 008: Build Warehouse Snapshots.
