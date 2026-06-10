# Task 009 Execution Report — Build Validation Checks

## Role

Data Quality Engineer

## Task

Task 009 — Build Validation Checks

## Objective

Implement a validation layer that proves pipeline output is trustworthy, not only technically successful.

The task focuses on:

- raw layer completeness
- source key validity
- staging lineage back to raw
- warehouse snapshot lineage back to staging
- current-state uniqueness
- temporal consistency
- Airflow-compatible validation runner

---

## Files Created

```text
docs/validation_contract.md

dbt_job_market_radar/tests/assert_raw_latest_successful_batch_has_records.sql
dbt_job_market_radar/tests/assert_raw_job_postings_have_valid_source_job_key.sql
dbt_job_market_radar/tests/assert_staging_preserves_raw_lineage.sql
dbt_job_market_radar/tests/assert_warehouse_snapshots_preserve_staging_lineage.sql
dbt_job_market_radar/tests/assert_current_has_one_row_per_source_job_key.sql
dbt_job_market_radar/tests/assert_first_seen_before_or_equal_last_seen.sql

src/pipeline/run_data_quality_checks.py
```

---

## Checks Added

### 1. Latest Successful Batch Has Records

File:

```text
dbt_job_market_radar/tests/assert_raw_latest_successful_batch_has_records.sql
```

Validates:

- at least one successful batch exists
- latest successful batch has `records_loaded > 0`

Layer:

```text
raw
```

Severity:

```text
critical
```

---

### 2. Raw Job Postings Have Valid Source Job Key

File:

```text
dbt_job_market_radar/tests/assert_raw_job_postings_have_valid_source_job_key.sql
```

Validates:

```text
source_job_key = source_name || ':' || source_job_id
```

Example:

```text
france_travail:123456
```

Layer:

```text
raw
```

Severity:

```text
critical
```

---

### 3. Staging Preserves Raw Lineage

File:

```text
dbt_job_market_radar/tests/assert_staging_preserves_raw_lineage.sql
```

Validates:

- every row in `staging.stg_france_travail_job_postings`
- maps back to `raw.raw_france_travail_job_postings`

Layer:

```text
staging / lineage
```

Severity:

```text
critical
```

---

### 4. Warehouse Snapshots Preserve Staging Lineage

File:

```text
dbt_job_market_radar/tests/assert_warehouse_snapshots_preserve_staging_lineage.sql
```

Validates:

- every row in `warehouse.wh_job_posting_snapshots`
- maps back to `staging.stg_france_travail_job_postings`

Layer:

```text
warehouse / lineage
```

Severity:

```text
critical
```

---

### 5. Current Has One Row Per Source Job Key

File:

```text
dbt_job_market_radar/tests/assert_current_has_one_row_per_source_job_key.sql
```

Validates current-state grain:

```text
one row per source_job_key
```

Layer:

```text
warehouse
```

Severity:

```text
critical
```

---

### 6. First Seen Is Before Or Equal Last Seen

File:

```text
dbt_job_market_radar/tests/assert_first_seen_before_or_equal_last_seen.sql
```

Validates temporal consistency:

```text
first_seen_at <= last_seen_at
```

Layer:

```text
warehouse
```

Severity:

```text
critical
```

---

## Data Quality Runner

File:

```text
src/pipeline/run_data_quality_checks.py
```

Expected command:

```bash
python -m src.pipeline.run_data_quality_checks
```

Behavior:

1. Runs dbt parse.
2. Runs dbt build with a validation-focused selector.
3. Uses project-local paths.
4. Prints clear success/failure output.
5. Exits with code `0` when checks pass.
6. Exits with non-zero code when checks fail.

Default selector:

```text
source:* path:models/staging path:models/warehouse path:tests
```

The selector can be overridden with:

```text
DBT_QUALITY_SELECT
```

---

## Commands To Run

From the repository root:

```bash
dbt parse --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar
```

```bash
dbt build --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar --select source:* path:models/staging path:models/warehouse path:tests
```

```bash
python -m src.pipeline.run_data_quality_checks
```

---

## Expected Result

Expected dbt result:

```text
PASS
ERROR=0
```

Expected runner result:

```text
Data quality checks completed successfully
exit code 0
```

Expected sample data counts from previous tasks:

```text
raw job postings = 2
staging job postings = 2
warehouse snapshots = 2
warehouse current = 2
```

---

## Manual SQL Validation Queries

```sql
select count(*)
from raw.raw_france_travail_job_postings;

select count(*)
from staging.stg_france_travail_job_postings;

select count(*)
from warehouse.wh_job_posting_snapshots;

select count(*)
from warehouse.wh_job_posting_current;
```

---

## Known Limitations

Task 009 does not implement:

- mart checks
- relevance score checks
- skill demand checks
- Streamlit dashboard logic
- Airflow DAG implementation
- historical row-count anomaly detection
- Great Expectations or external quality framework

These are intentionally out of scope for Task 009.

---

## Changes Not Made

No changes were made to:

```text
dbt_project.yml
existing staging models
existing warehouse models
ingestion pipeline
profiles.yml.example
```

No local secrets or real `profiles.yml` should be committed.

---

## Handoff To Orchestration / DevOps Engineer

Task 010 should add this Airflow step after `dbt_build`:

```text
run_data_quality_checks
```

Expected command:

```bash
python -m src.pipeline.run_data_quality_checks
```

Required DAG order:

```text
start
  -> create_load_batch_and_ingest_france_travail
  -> dbt_build
  -> run_data_quality_checks
  -> generate_weekly_report
  -> end
```

---

## Final Status

Task 009 validation layer is ready to be added to the repository and tested locally.
