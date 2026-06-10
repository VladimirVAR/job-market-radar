# Validation Contract

## Purpose

This document defines what a successful data pipeline output means for Job Market Radar.

A successful technical run does **not** automatically mean the data is correct.

Airflow can mark a task as successful and dbt can build models successfully, while the produced data is still incomplete, duplicated, stale, or impossible to trace back to raw source payloads.

This validation contract protects the trustworthiness of the current MVP layers:

```text
raw -> staging -> warehouse
```

Marts are intentionally not implemented in Task 009. Mart-level validation rules are documented as future checks for later tasks.

---

## Scope

Task 009 validates:

```text
raw.raw_load_batches
raw.raw_api_requests
raw.raw_france_travail_job_postings

staging.stg_france_travail_job_postings

warehouse.wh_job_posting_snapshots
warehouse.wh_job_posting_current
```

The validation layer focuses on:

- latest successful batch completeness
- raw source key validity
- raw-to-staging lineage
- staging-to-warehouse lineage
- current-state uniqueness
- temporal consistency
- readiness for Airflow quality gates

---

## Quality Principle

The quality gate answers this question:

```text
Did the pipeline produce complete and trustworthy data?
```

The answer is not based only on whether code executed without errors.

The answer depends on whether:

- a successful batch exists
- the latest successful batch loaded records
- raw job postings have stable source keys
- downstream rows can be traced back to raw rows
- warehouse snapshots preserve staging lineage
- the current-state model has one row per source job key
- current-state timestamps are logically consistent

---

## Raw Layer Validation

### Raw layer grain

#### `raw.raw_load_batches`

Grain:

```text
one row per pipeline execution
```

#### `raw.raw_api_requests`

Grain:

```text
one row per API request, page, or search parameter set
```

#### `raw.raw_france_travail_job_postings`

Grain:

```text
one raw job posting payload per source job per request per batch
```

---

### Raw checks

| Check | Severity | Reason |
|---|---|---|
| latest successful batch exists | critical | Without a successful batch, there is no trusted pipeline output |
| latest successful batch has records | critical | A successful batch with zero loaded records is suspicious for MVP sample mode |
| `source_job_key` is not null | critical | Source-level identity is required downstream |
| `source_job_key = source_name || ':' || source_job_id` | critical | Enforces stable MVP key convention |
| `raw_payload_json` is not null | critical | Raw source preservation is required |
| `payload_hash` is not null | critical | Change detection and snapshot logic depend on it |
| raw rows link to a request and batch | critical | Operational lineage depends on request and batch metadata |

---

## Staging Layer Validation

### Staging grain

#### `staging.stg_france_travail_job_postings`

Grain:

```text
one cleaned France Travail job posting per source job per batch
```

---

### Staging checks

| Check | Severity | Reason |
|---|---|---|
| `batch_id` is not null | critical | Required for batch lineage |
| `request_id` is not null | critical | Required for API request lineage |
| `raw_job_posting_id` is not null | critical | Required for raw payload traceability |
| `source_job_key` is not null | critical | Required for job identity |
| `job_title` is not null where practical | warning/critical depending on source reliability | Empty titles make the output weak for analysis |
| every staging row maps back to raw | critical | Staging must preserve raw lineage |

---

## Warehouse Layer Validation

### Warehouse grains

#### `warehouse.wh_job_posting_snapshots`

Grain:

```text
one canonical job posting observation per source job per batch
```

#### `warehouse.wh_job_posting_current`

Grain:

```text
one row per latest known source job key / canonical job key
```

For the MVP:

```text
canonical_job_key = source_job_key
```

---

### Warehouse checks

| Check | Severity | Reason |
|---|---|---|
| every snapshot maps back to staging | critical | Warehouse must preserve transformation lineage |
| every snapshot preserves `raw_job_posting_id` | critical | Needed to trace warehouse rows to raw payloads |
| current-state has one row per `source_job_key` | critical | Current model must respect its grain |
| `first_seen_at <= last_seen_at` | critical | Temporal logic must be consistent |
| `canonical_job_key` is not null | critical | Required for downstream marts |
| current rows come from latest known snapshots | warning/critical later | Protects current-state logic |

---

## Lineage Contract

Every analytical job posting row should be traceable through this chain:

```text
warehouse.wh_job_posting_current
  -> warehouse.wh_job_posting_snapshots
  -> staging.stg_france_travail_job_postings
  -> raw.raw_france_travail_job_postings
  -> raw.raw_api_requests
  -> raw.raw_load_batches
```

Task 009 directly validates the most important parts:

```text
staging -> raw
warehouse snapshots -> staging
current-state uniqueness
```

Future tasks can extend this to marts:

```text
marts -> warehouse -> staging -> raw
```

---

## Current-State Logic Contract

The current-state model must not produce duplicate current rows.

Required invariant:

```text
one row per source_job_key
```

The model must also preserve basic temporal consistency:

```text
first_seen_at <= last_seen_at
```

A job should only be marked inactive when it is missing from a later comparable search scope. This is documented as an architectural rule, but Task 009 does not fully validate inactive lifecycle behavior yet.

---

## Freshness Contract

For Task 009, freshness is represented by the latest successful batch.

Minimum expectation:

```text
there is at least one successful batch
the latest successful batch loaded at least one raw job posting
```

Future improvement:

- validate maximum allowed age of latest successful batch
- compare latest batch row count against historical average
- detect sudden drops in request count or loaded record count

---

## Mart Validation Rules For Future Tasks

Marts are outside Task 009 scope.

When marts are implemented, add checks for:

| Mart check | Severity |
|---|---|
| `relevance_score between 0 and 100` | critical |
| `matched_skills_count <= required_skills_count` | critical |
| active job counts are not negative | critical |
| weekly summary grain is respected | critical |
| marts are not empty after successful ingestion | warning/critical depending on context |
| top skills are not all null or unknown | warning |
| junior-friendly results are not dominated by senior-only jobs | warning |

---

## Implementation Method

Task 009 uses:

```text
dbt custom SQL data tests
Python runner around dbt validation command
Airflow-compatible command entrypoint
```

The expected command is:

```bash
python -m src.pipeline.run_data_quality_checks
```

The runner uses project-local paths:

```bash
dbt_job_market_radar
```

It must not use local absolute paths such as:

```text
C:\Users\...
```

---

## Failure Handling

### Critical validation failure

If a critical validation check fails:

```text
run_data_quality_checks exits with non-zero code
Airflow should mark the quality gate task as failed
downstream report generation should not be trusted
```

### Warning validation issue

Warnings should be documented or logged but should not necessarily stop the MVP pipeline.

Task 009 mostly implements critical checks.

---

## Known Limitations

Task 009 intentionally does not validate everything.

Known limitations:

- no mart validation yet because marts are not implemented
- no relevance score validation yet because relevance scoring is not implemented
- no historical row-count baseline yet
- no advanced inactive job lifecycle validation yet
- no cross-source deduplication validation because MVP uses only France Travail
- no Great Expectations or external quality framework in MVP

These limitations are acceptable because this task protects the most important early invariants:

```text
batch completeness
key validity
lineage
current-state uniqueness
temporal consistency
```

---

## Acceptance Criteria Mapping

Task 009 is complete when:

- this validation contract exists
- custom dbt data tests exist under `dbt_job_market_radar/tests/`
- tests return zero rows when passing
- raw, staging, warehouse, lineage, and current-state checks are covered
- `src/pipeline/run_data_quality_checks.py` exists
- the runner uses relative project-local paths
- `dbt parse` succeeds
- `dbt build` succeeds
- `python -m src.pipeline.run_data_quality_checks` succeeds
- no secrets or local profiles are committed
