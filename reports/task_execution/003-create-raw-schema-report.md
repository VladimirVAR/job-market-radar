# Task 003 Report — Create Raw Schema

## 1. Task Summary

**Task:** Task 003 — Create Raw Schema
**Responsible role:** Data Modeling Engineer
**Project:** Job Market Radar
**Target database:** PostgreSQL
**Status:** Completed locally / ready for review

The goal of this task was to create the initial PostgreSQL database structure required for raw ingestion.

The raw layer must support:

- pipeline batch tracking
- API request metadata tracking
- raw API response preservation
- lineage from raw data to downstream dbt models
- reproducibility through SQL DDL files

The task required implementing the following files:

```text
sql/ddl/001_create_schemas.sql
sql/ddl/002_create_raw_tables.sql
```

This follows the project rule that the repository must remain the source of truth and raw schemas/tables should be defined in SQL files, not created manually only through DBeaver.

---

## 2. Files Changed

```text
sql/ddl/001_create_schemas.sql
sql/ddl/002_create_raw_tables.sql
```

### `001_create_schemas.sql`

Creates the required project schemas:

```text
raw
staging
warehouse
marts
```

Also enables:

```sql
create extension if not exists pgcrypto;
```

This is used to support UUID generation through `gen_random_uuid()`.

### `002_create_raw_tables.sql`

Creates the initial raw-layer tables:

```text
raw.raw_load_batches
raw.raw_api_requests
raw.raw_france_travail_job_postings
```

The file also defines:

- primary keys
- foreign keys
- check constraints
- JSONB columns
- useful indexes

---

## 3. Implemented Schemas

The following schemas were created and validated in DBeaver:

```text
marts
raw
staging
warehouse
```

Validation query used:

```sql
select schema_name
from information_schema.schemata
where schema_name in ('raw', 'staging', 'warehouse', 'marts')
order by schema_name;
```

Validation result:

```text
marts
raw
staging
warehouse
```

---

## 4. Implemented Raw Tables

The following raw tables were created and validated:

```text
raw.raw_api_requests
raw.raw_france_travail_job_postings
raw.raw_load_batches
```

Validation query used:

```sql
select table_schema, table_name
from information_schema.tables
where table_schema = 'raw'
order by table_name;
```

Validation result:

```text
raw | raw_api_requests
raw | raw_france_travail_job_postings
raw | raw_load_batches
```

---

## 5. Table Grain

### `raw.raw_load_batches`

**Grain:** one row per pipeline execution.

Purpose:

```text
Tracks every ingestion pipeline run.
```

This table provides the top-level operational lineage for each ingestion run.

---

### `raw.raw_api_requests`

**Grain:** one row per API request, API page, or search parameter set.

Purpose:

```text
Stores API request metadata for debugging, reproducibility, and lineage.
```

This table links API calls back to a specific `batch_id`.

---

### `raw.raw_france_travail_job_postings`

**Grain:** one raw job posting payload per source job per request per batch.

Purpose:

```text
Preserves raw France Travail job posting payloads exactly as returned by the API.
```

This table stores raw payloads as JSONB and does not parse business fields such as job title, company, contract type, or description. Parsed business fields belong to staging/dbt later.

---

## 6. Primary Key Validation

Primary keys were validated through `information_schema.table_constraints`.

Validation query:

```sql
select
    tc.table_schema,
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type
from information_schema.table_constraints tc
where tc.table_schema = 'raw'
  and tc.constraint_type = 'PRIMARY KEY'
order by tc.table_name;
```

Validation result:

```text
raw | raw_api_requests                  | raw_api_requests_pkey                  | PRIMARY KEY
raw | raw_france_travail_job_postings   | raw_france_travail_job_postings_pkey   | PRIMARY KEY
raw | raw_load_batches                  | raw_load_batches_pkey                  | PRIMARY KEY
```

Status:

```text
Passed
```

---

## 7. Foreign Key Validation

Foreign keys were validated through `information_schema.table_constraints`.

Validation query:

```sql
select
    tc.table_schema,
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type
from information_schema.table_constraints tc
where tc.table_schema = 'raw'
  and tc.constraint_type = 'FOREIGN KEY'
order by tc.table_name, tc.constraint_name;
```

Validation result confirms:

```text
raw.raw_api_requests -> raw.raw_load_batches
raw.raw_france_travail_job_postings -> raw.raw_load_batches
raw.raw_france_travail_job_postings -> raw.raw_api_requests
```

Status:

```text
Passed
```

---

## 8. JSONB Validation

The required raw JSON fields were validated as JSONB.

Validation query:

```sql
select
    table_schema,
    table_name,
    column_name,
    data_type
from information_schema.columns
where table_schema = 'raw'
  and column_name in (
      'request_params_json',
      'response_headers_json',
      'raw_payload_json'
  )
order by table_name, column_name;
```

Validation result:

```text
raw | raw_api_requests                | request_params_json    | jsonb
raw | raw_api_requests                | response_headers_json  | jsonb
raw | raw_france_travail_job_postings | raw_payload_json       | jsonb
```

Status:

```text
Passed
```

---

## 9. Key Design Decisions

### UUID primary keys

All raw tables use UUID primary keys:

```text
batch_id
request_id
raw_job_posting_id
```

Reason:

```text
UUIDs are safe for generated pipeline identifiers and avoid sequence coordination issues.
```

---

### `pgcrypto` extension

The DDL enables:

```sql
create extension if not exists pgcrypto;
```

Reason:

```text
Allows PostgreSQL to generate UUIDs with gen_random_uuid().
```

---

### Batch lineage

`batch_id` is propagated from:

```text
raw.raw_load_batches
  -> raw.raw_api_requests
  -> raw.raw_france_travail_job_postings
```

This supports pipeline observability and downstream lineage.

---

### Request lineage

`request_id` links every raw job posting back to the API request/page/search scope that returned it.

This is important for debugging, reproducibility, and future inactive-job logic.

---

### Search scope support

`search_scope_key` is required in both request and raw job tables.

Reason:

```text
Future job disappearance/inactive logic must compare jobs only inside comparable search scopes.
```

---

### Raw JSON preservation

`raw_payload_json` is stored as JSONB and is not nullable.

Reason:

```text
Raw source truth must be preserved before dbt transformations.
```

---

### No business transformations in raw

The raw layer intentionally does not parse:

```text
job title
company
contract type
description
location
seniority
skills
```

These transformations are deferred to staging/dbt.

---

## 10. Indexes Added

Indexes were added for operational and downstream lookup fields.

### `raw.raw_api_requests`

```text
batch_id
search_scope_key
source_name
response_status_code
```

### `raw.raw_france_travail_job_postings`

```text
batch_id
request_id
source_job_key
search_scope_key
payload_hash
```

These indexes support:

- batch-level filtering
- request-level lineage
- source job lookup
- comparable search scope analysis
- payload change detection

---

## 11. How DDL Was Applied

The DDL was applied manually through PostgreSQL connection in VS Code / DBeaver against the local PostgreSQL database:

```text
job_market_radar
localhost:5432
```

Reason:

```text
The PostgreSQL volume already existed.
```

The task specification notes that files mounted into `/docker-entrypoint-initdb.d` are executed automatically only when PostgreSQL initializes a fresh volume. For an already-running local database, SQL may need to be applied manually through DBeaver or psql.

---

## 12. Acceptance Criteria Review

| Acceptance Criterion | Status |
|---|---:|
| `raw` schema exists | Passed |
| `staging` schema exists | Passed |
| `warehouse` schema exists | Passed |
| `marts` schema exists | Passed |
| `raw.raw_load_batches` exists | Passed |
| `raw.raw_api_requests` exists | Passed |
| `raw.raw_france_travail_job_postings` exists | Passed |
| Primary keys exist | Passed |
| Foreign keys exist where practical | Passed |
| JSON fields use JSONB | Passed |
| Database can be inspected through DBeaver | Passed |
| Raw layer keeps business transformations out | Passed |
| DDL files exist under `sql/ddl/` | Passed locally / should be confirmed in Git |

---

## 13. Known Assumptions / Trade-offs

### 13.1 No unique constraint on raw job postings

No hard unique constraint was added on raw job postings.

Reason:

```text
The raw layer should preserve what the API returns.
If duplicates appear, they should be handled by validation checks or staging deduplication rather than blocking raw ingestion.
```

### 13.2 Raw payload expected as JSON object

A check constraint was added to expect `raw_payload_json` to be a JSON object.

Assumption:

```text
Each row in raw.raw_france_travail_job_postings stores one job posting object.
```

If the API parser later stores a different structure, this constraint may need to be revisited.

### 13.3 Secrets must not be stored

The DDL allows request URLs, parameters, and headers to be stored, but ingestion code must ensure that secrets are not stored in:

```text
request_url
request_params_json
response_headers_json
```

### 13.4 DDL execution mode

For fresh database initialization, the DDL should run automatically through the Docker PostgreSQL init mount.

For the current local database, it was applied manually because the database already existed.

---

## 14. Impact on Next Tasks

Task 003 creates the database foundation required for raw ingestion.

The next implementation tasks can now rely on:

```text
raw.raw_load_batches
raw.raw_api_requests
raw.raw_france_travail_job_postings
```

Task 005 will need to insert into these tables by creating a load batch, storing every request, storing every raw job posting as JSONB, generating `source_job_key`, generating `payload_hash`, and updating batch status/counts after completion.

Future validation checks should verify that latest batches exist, raw requests exist, raw payloads are present, and fields such as `source_job_id`, `source_job_key`, `raw_payload_json`, and `payload_hash` are populated.

---

## 15. Final Status

```text
Task 003 status: Completed locally / ready for Tech Lead review.

Files changed:
- sql/ddl/001_create_schemas.sql
- sql/ddl/002_create_raw_tables.sql

Validation results:
- Required schemas created.
- Required raw tables created.
- Primary keys validated.
- Foreign keys validated.
- JSONB fields validated.

Known issues:
- DDL must be committed to repository if not committed yet.
- Current database was updated manually because the PostgreSQL volume already existed.

Recommended decision:
Accept Task 003 and proceed to the next implementation task.
```
