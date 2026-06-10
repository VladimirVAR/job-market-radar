# Task 003: Create Raw Schema

## Goal

Create the PostgreSQL raw schema and raw metadata tables.

The raw layer must preserve source API responses and track every pipeline run.

---

## Context

The project requires:

- raw API response preservation
- load batch tracking
- API request metadata
- lineage from raw to marts

---

## Deliverables

Create SQL files:

```text
sql/ddl/001_create_schemas.sql
sql/ddl/002_create_raw_tables.sql
```

Create schemas:

```sql
raw
staging
warehouse
marts
```

Create raw tables:

```text
raw.raw_load_batches
raw.raw_api_requests
raw.raw_france_travail_job_postings
```

---

## Table: `raw.raw_load_batches`

**Grain:** one row per pipeline execution.

Required columns:

```text
batch_id
source_name
pipeline_name
started_at
finished_at
status
triggered_by
records_loaded
requests_made
error_message
created_at
```

---

## Table: `raw.raw_api_requests`

**Grain:** one row per API request/page/search parameter set.

Required columns:

```text
request_id
batch_id
source_name
endpoint
http_method
request_url
request_params_json
search_scope_key
page_number
page_size
response_status_code
response_time_ms
response_headers_json
started_at
finished_at
error_message
created_at
```

---

## Table: `raw.raw_france_travail_job_postings`

**Grain:** one raw job payload per source job per request per batch.

Required columns:

```text
raw_job_posting_id
batch_id
request_id
source_name
source_job_id
source_job_key
search_scope_key
raw_payload_json
payload_hash
ingested_at
created_at
```

---

## Acceptance Criteria

- All required schemas are created.
- Raw tables are created successfully in PostgreSQL.
- Primary keys are defined.
- Foreign keys are defined where practical.
- JSON fields use JSONB.
- Timestamp fields use appropriate timestamp types.
- `source_job_key` is not null.
- `raw_payload_json` is not null.
- SQL files can be rerun safely or documented as one-time DDL.

---

## Implementation Notes

Recommended key strategy:

```text
source_job_key = france_travail:{source_job_id}
```

Do not transform business fields in raw tables.

---

## Dependencies

Task 002.

---

## Next Task

Task 004: Build France Travail API Client.
