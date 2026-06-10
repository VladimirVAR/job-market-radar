# Task 009: Build Validation Checks

## Goal

Create validation checks across raw, staging, warehouse, and marts.

The goal is to ensure that successful pipeline execution also means data is trustworthy enough for analysis.

---

## Context

Airflow task success does not guarantee data correctness.

A pipeline can run successfully and still load incomplete, duplicated, or invalid data.

---

## Deliverables

Create:

```text
docs/architecture/validation_contract.md
dbt tests
custom SQL checks if needed
src/pipeline/run_data_quality_checks.py
```

---

## Raw Checks

Validate:

```text
latest batch exists
latest batch has valid status
raw API requests exist for latest batch
raw job payloads exist for latest successful batch
source_job_id is not null
source_job_key is not null
raw_payload_json is not null
payload_hash is not null
```

---

## Staging Checks

Validate:

```text
source_job_key is not null
batch_id is not null
request_id is not null
job_title is not null where practical
controlled fields use expected values where practical
```

---

## Warehouse Checks

Validate:

```text
canonical_job_key is not null
one current row per canonical_job_key
snapshots link back to raw rows
current rows come from latest known snapshots
first_seen_at <= last_seen_at
```

---

## Marts Checks

Validate:

```text
relevance_score between 0 and 100
matched_skills_count <= required_skills_count
active job counts are not negative
weekly summary grain is respected
marts are not empty after successful ingestion
```

---

## Acceptance Criteria

- dbt tests exist for key models.
- Custom validation script can be run after `dbt build`.
- Validation failures are visible.
- Validation logic is documented.
- Airflow DAG includes a validation step.
- The validation contract explains that Airflow success is not enough.

---

## Implementation Notes

Do not try to validate everything in the first version.

Focus on checks that protect lineage, uniqueness, freshness, and dashboard correctness.

---

## Dependencies

Task 008.

---

## Next Task

Task 010: Create Airflow DAG.
