# Validation Summary

## Purpose

This document summarizes the validation approach for Job Market Radar.

The main principle is:

```text
Airflow success is not enough.
```

A pipeline can execute successfully and still produce incomplete, duplicated, stale, or analytically unsafe data.

---

## Successful Pipeline Definition

For this project, a successful pipeline run means:

1. Ingestion completed.
2. Raw load batch was created and marked correctly.
3. Raw API request metadata exists.
4. Raw job posting payloads were stored.
5. dbt build completed successfully.
6. dbt tests passed.
7. Custom data quality checks passed.
8. Dashboard marts are available.
9. Streamlit can read the prepared marts.

---

## Validation Layers

Validation happens across:

```text
raw -> staging -> warehouse -> marts -> dashboard readiness
```

The goal is not to validate everything in the MVP. The goal is to protect the most important assumptions: lineage, completeness, uniqueness, freshness, and dashboard correctness.

---

## Raw Validation

Raw checks protect ingestion correctness.

Examples:

- latest batch exists
- latest batch has a valid status
- raw API requests exist for the latest batch
- raw job payloads exist for the latest successful batch
- `batch_id` is not null
- `request_id` is not null
- `source_job_id` is not null
- `source_job_key` is not null
- `raw_payload_json` is not null
- `payload_hash` is not null

Why it matters:

> If raw data is incomplete or untraceable, downstream transformations may produce misleading outputs.

---

## Staging Validation

Staging checks protect parsed and typed source-specific data.

Examples:

- `source_job_key` is not null
- `batch_id` is not null
- `request_id` is not null
- `raw_job_posting_id` is not null
- `job_title` is not null where practical
- `payload_hash` is not null
- controlled fields use expected values where practical

Why it matters:

> Staging is the first transformation layer. It must preserve lineage and expose clean fields for warehouse modeling.

---

## Warehouse Validation

Warehouse checks protect analytical correctness.

Examples:

- `canonical_job_key` is not null
- current model has one row per `canonical_job_key`
- snapshots link back to raw rows
- current rows come from latest known snapshots
- `first_seen_at <= last_seen_at`
- inactive logic respects comparable `search_scope_key`

Why it matters:

> The warehouse layer supports historical analysis and current-state dashboard views. Duplicate or broken current-state records would damage the dashboard outputs.

---

## Marts Validation

Marts checks protect product-facing outputs.

Examples:

- `relevance_score` is between 0 and 100
- `matched_skills_count <= required_skills_count`
- active job counts are not negative
- weekly summary grain is respected
- marts are not empty after successful ingestion
- data freshness mart reflects latest known pipeline status

Why it matters:

> Marts are consumed by Streamlit and reports. They are the last analytical layer before users see the data.

---

## dbt Tests

dbt tests are used for structural and model-level validation.

Expected coverage includes:

- not-null tests on core keys
- uniqueness tests where model grain requires it
- accepted values where controlled fields exist
- relationship/lineage tests where practical
- custom data tests for mart sanity checks

Validated command:

```bash
dbt build --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar
```

`dbt build` runs models and tests together.

---

## Python Data Quality Runner

Custom checks are run through:

```bash
python -m src.pipeline.run_data_quality_checks
```

This runner is useful for checks that may be easier to express as operational validations across multiple layers or latest-run context.

---

## Airflow Validation Step

The Airflow DAG includes a validation step after dbt build:

```text
dbt_build
  -> run_data_quality_checks
```

This ensures that the pipeline does not stop at "the SQL ran" but also verifies that the outputs are trustworthy enough for the dashboard.

---

## Streamlit Smoke Test

Dashboard readiness can be checked by running:

```bash
streamlit run streamlit_app/app.py
```

Expected result:

- app starts without database connection errors
- business pages can read marts
- data freshness page shows recent pipeline status
- pages do not need to calculate core business metrics directly

---

## Manual Acceptance Checklist

Before a project demo:

- [ ] Latest ingestion completed successfully.
- [ ] `dbt build` completed successfully.
- [ ] Data quality runner passed.
- [ ] Marts are populated.
- [ ] Streamlit app starts.
- [ ] Data Freshness page is understandable.
- [ ] Known limitations are documented.

---

## Summary

Validation is part of the data product, not an afterthought.

The core message:

```text
Airflow shows the workflow ran.
Validation shows whether the resulting data can be trusted.
```
