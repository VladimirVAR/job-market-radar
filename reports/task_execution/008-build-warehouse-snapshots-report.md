# Task 008 Execution Report — Build Warehouse Snapshots and Current Models

## Role

dbt Engineer / dbt Transformation Engineer

## Task

Task 008 — Build Warehouse Snapshots

## Objective

Create the first warehouse layer from the existing France Travail staging model.

Implemented flow:

```text
staging.stg_france_travail_job_postings
  -> warehouse.wh_job_posting_snapshots
  -> warehouse.wh_job_posting_current
```

## Files Created

```text
dbt_job_market_radar/models/warehouse/wh_job_posting_snapshots.sql
dbt_job_market_radar/models/warehouse/wh_job_posting_snapshots.yml

dbt_job_market_radar/models/warehouse/wh_job_posting_current.sql
dbt_job_market_radar/models/warehouse/wh_job_posting_current.yml
```

## Files Not Modified

No changes were made to:

```text
dbt_project.yml
models/sources/raw_sources.yml
models/staging/france_travail/stg_france_travail_job_postings.sql
models/staging/france_travail/stg_france_travail_job_postings.yml
macros/
profiles.yml.example
```

No marts, dashboard logic, skill extraction, or relevance scoring were added.

---

## Model 1: wh_job_posting_snapshots

### Purpose

Warehouse historical observation model for France Travail job postings.

This is not a dbt snapshot object. It is a SQL warehouse model that preserves one ingested observation per raw job posting row.

### Materialization

```sql
{{ config(materialized='table') }}
```

### Input

```sql
{{ ref('stg_france_travail_job_postings') }}
```

The model does not read raw tables directly.

### Grain

```text
one row per raw_job_posting_id
```

Equivalent:

```text
one row per observed job posting payload loaded from raw ingestion
```

### Lineage Strategy

The model preserves lineage back to raw through:

```text
batch_id
request_id
raw_job_posting_id
source_name
source_job_id
source_job_key
search_scope_key
payload_hash
```

### Compatibility Columns

The implementation includes both:

```text
snapshot_id
job_snapshot_id
```

Both are currently based on `raw_job_posting_id`.

The implementation also includes:

```text
canonical_job_key = source_job_key
```

This keeps the MVP compatible with future cross-source modeling while keeping the current key strategy simple.

---

## Model 2: wh_job_posting_current

### Purpose

Current-state warehouse model exposing the latest known ingested version of each France Travail job posting.

### Materialization

```sql
{{ config(materialized='view') }}
```

### Input

```sql
{{ ref('wh_job_posting_snapshots') }}
```

The model does not read raw or staging directly.

### Grain

```text
one row per source_job_key
```

### Current-State Logic

The latest row per `source_job_key` is selected with:

```sql
row_number() over (
    partition by source_job_key
    order by
        coalesce(updated_at, published_at, retrieved_at) desc nulls last,
        retrieved_at desc nulls last,
        raw_job_posting_id desc
)
```

The selected row becomes the latest known current version.

### Observation Metadata

The model calculates:

```text
first_seen_at
last_seen_at
observation_count
is_current_version
```

### Important Limitation

`wh_job_posting_current` means:

```text
latest known ingested version
```

It does not guarantee that the job is still active on France Travail.

True active/inactive status requires repeated comparable search-scope runs and should be refined in a later task.

---

## dbt Tests Added

### wh_job_posting_snapshots

Tests added:

```text
snapshot_id: not_null, unique
raw_job_posting_id: not_null, unique
batch_id: not_null
request_id: not_null
source_name: not_null, accepted_values ['france_travail']
source_job_id: not_null
source_job_key: not_null
payload_hash: not_null
```

### wh_job_posting_current

Tests added:

```text
source_job_key: not_null, unique
source_name: not_null, accepted_values ['france_travail']
source_job_id: not_null
latest_raw_job_posting_id: not_null
latest_batch_id: not_null
payload_hash: not_null
observation_count: not_null
```

No `job_title not_null` test was added because the source may omit optional business fields.

---

## Documentation Added

Both YAML files document:

- model purpose
- model grain
- source dependency
- important lineage columns
- current-state semantics
- current-state limitation
- nullable business fields

---

## Commands to Run Locally

From repository root:

```bash
dbt parse --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar
```

Build warehouse models:

```bash
dbt build --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar --select warehouse
```

Or specifically:

```bash
dbt build --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar --select wh_job_posting_snapshots wh_job_posting_current
```

---

## Expected Validation SQL

Snapshot count:

```sql
select count(*)
from warehouse.wh_job_posting_snapshots;
```

Expected for current sample:

```text
2
```

Current count:

```sql
select count(*)
from warehouse.wh_job_posting_current;
```

Expected for current sample:

```text
2
```

Inspect current rows:

```sql
select
    source_job_key,
    job_title,
    company_name,
    city,
    contract_type,
    published_at,
    updated_at,
    first_seen_at,
    last_seen_at,
    observation_count,
    is_current_version
from warehouse.wh_job_posting_current
order by source_job_key;
```

Expected:

```text
2 rows from current sample data
is_current_version = true
observation_count >= 1
```

---

## Execution Status in This Environment

The files were created and YAML syntax was validated successfully.

Actual `dbt parse`, `dbt build`, and PostgreSQL row-count validation were not executed in this sandbox because the local project database and dbt runtime are not available here.

Local validation must be run in the user's repository environment.

---

## Known Limitations

1. `wh_job_posting_current` represents the latest known ingested version, not guaranteed active source status.
2. Inactive/disappeared job logic is intentionally not implemented in Task 008.
3. No skill extraction was implemented.
4. No relevance score was implemented.
5. No marts were created.
6. `canonical_job_key` currently equals `source_job_key` for MVP.

---

## Handoff to Task 009

Task 009 can now add validation checks for:

- snapshot uniqueness
- current-state uniqueness
- lineage preservation
- `first_seen_at <= last_seen_at`
- non-empty warehouse models after successful staging build
- consistency between snapshot and current row counts for sample data
