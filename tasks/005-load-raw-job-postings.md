# Task 005: Load Raw Job Postings

## Goal

Implement raw loading logic for France Travail job postings.

Every pipeline run must create a load batch, store request metadata, and store raw job posting payloads as JSONB.

---

## Context

Raw loading is the boundary between Python ingestion and dbt transformations.

Python should stop after raw tables are loaded.

---

## Deliverables

Implement:

```text
src/loaders/batch_loader.py
src/loaders/request_loader.py
src/loaders/raw_job_loader.py
src/pipeline/run_france_travail_ingestion.py
```

---

## Required Behavior

The ingestion pipeline should:

1. Create a row in `raw.raw_load_batches`.
2. Build configured France Travail API requests.
3. Store every request in `raw.raw_api_requests`.
4. Store every raw job posting in `raw.raw_france_travail_job_postings`.
5. Generate `source_job_key`.
6. Generate `payload_hash`.
7. Update the batch status and counts after completion.
8. Mark the batch as failed if the pipeline fails.

---

## Required Keys

Generate:

```text
source_job_key = france_travail:{source_job_id}
```

Generate a stable payload hash from the raw payload.

---

## Acceptance Criteria

- Running `python -m src.pipeline.run_france_travail_ingestion` creates one new batch.
- API request metadata is stored.
- Raw job posting payloads are stored as JSONB.
- `batch_id` links all rows from the same run.
- `request_id` links job postings to API requests.
- `source_job_key` is populated.
- `payload_hash` is populated.
- Batch status is updated to `success`, `failed`, or `partial_success`.
- No business transformations are performed in Python.

---

## Implementation Notes

Use database transactions where practical.

If the API call succeeds but some rows fail to load, the batch should not be silently marked as fully successful.

---

## Dependencies

Task 004.

---

## Next Task

Task 006: Create dbt Project.
