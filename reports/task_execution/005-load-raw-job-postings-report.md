# Task 005 Report: Load Raw Job Postings

## Role

Source / Ingestion Engineer

## Scope

Implemented raw loading logic that connects the France Travail API client from Task 004 to PostgreSQL raw tables.

Main command:

```bash
python -m src.pipeline.run_france_travail_ingestion
```

This task intentionally stops at the raw layer. It does **not** run dbt, does **not** build staging models, does **not** extract skills, and does **not** calculate relevance scores.

## Task Objective

Task 005 turns the API client output into raw database rows:

```text
FranceTravailClient
  -> batch_loader
  -> request_loader
  -> raw_job_loader
  -> raw PostgreSQL tables
```

Expected database effect for one pipeline run:

```text
1 row in raw.raw_load_batches
N rows in raw.raw_api_requests
N rows in raw.raw_france_travail_job_postings
```

## Files Implemented

```text
src/common/__init__.py
src/common/config.py
src/common/database.py
src/common/logging.py
src/common/hashing.py
src/common/dates.py
src/common/exceptions.py

src/loaders/__init__.py
src/loaders/batch_loader.py
src/loaders/request_loader.py
src/loaders/raw_job_loader.py

src/pipeline/__init__.py
src/pipeline/run_france_travail_ingestion.py

data/sample/france_travail_sample_response.json
```

The France Travail source-specific files from Task 004 are included as dependencies:

```text
src/ingestion/france_travail/auth.py
src/ingestion/france_travail/client.py
src/ingestion/france_travail/request_builder.py
src/ingestion/france_travail/parser.py
```

## What Was Done

### `src/loaders/batch_loader.py`

Implemented load-batch lifecycle helpers for `raw.raw_load_batches`.

Functions:

```text
create_load_batch()
mark_batch_finished()
mark_batch_failed()
```

Behavior:

- creates one `batch_id` per pipeline run
- inserts the batch row before any API request is made
- starts with status `running`
- finishes with `success`, `partial_success`, or `failed`
- updates `records_loaded` and `requests_made`
- commits the batch row immediately so the run is auditable even if later steps fail

### `src/loaders/request_loader.py`

Implemented request metadata loading for `raw.raw_api_requests`.

Function:

```text
insert_api_request()
```

Stored fields include:

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

Important behavior:

- every API request/page gets its own `request_id`
- failed API responses are still stored
- sensitive headers are not persisted because the Task 004 client already removes them

### `src/loaders/raw_job_loader.py`

Implemented raw job payload loading for `raw.raw_france_travail_job_postings`.

Functions:

```text
build_source_job_key()
build_payload_hash()
insert_raw_job_postings()
```

Generated keys:

```text
source_job_key = france_travail:{source_job_id}
payload_hash = sha256(canonical_json(raw_payload))
```

Inserted fields include:

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

Important boundary:

The loader does not parse or normalize business fields such as job title, company, contract type, seniority, skills, or relevance score.

### `src/pipeline/run_france_travail_ingestion.py`

Implemented the main Task 005 pipeline entrypoint.

Main command:

```bash
python -m src.pipeline.run_france_travail_ingestion
```

Pipeline flow:

```text
1. read environment config
2. connect to PostgreSQL
3. create one load batch
4. build France Travail search requests
5. call FranceTravailClient for every request
6. store every request metadata row
7. parse raw job payloads from response
8. insert raw job payloads as JSONB
9. update batch status and counts
10. print execution summary as JSON
```

The script returns a summary like:

```json
{
  "batch_id": "...",
  "status": "success",
  "requests_made": 1,
  "successful_requests": 1,
  "failed_requests": 0,
  "records_loaded": 50,
  "error_message": null
}
```

## Configuration

Database variables:

```text
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=job_market_radar
POSTGRES_USER=job_market_radar
POSTGRES_PASSWORD=change_me
```

France Travail API credentials:

```text
FRANCE_TRAVAIL_CLIENT_ID=your_client_id_here
FRANCE_TRAVAIL_CLIENT_SECRET=your_client_secret_here
```

Ingestion configuration:

```text
PIPELINE_TRIGGERED_BY=manual
FRANCE_TRAVAIL_SEARCH_KEYWORDS=data engineer,analytics engineer
FRANCE_TRAVAIL_LOCATIONS=
FRANCE_TRAVAIL_CONTRACT_TYPES=
FRANCE_TRAVAIL_REMOTE_VALUES=
FRANCE_TRAVAIL_MAX_PAGES=1
FRANCE_TRAVAIL_PAGE_SIZE=50
```

Optional local sample mode:

```text
FRANCE_TRAVAIL_SAMPLE_MODE=true
FRANCE_TRAVAIL_SAMPLE_FILE=data/sample/france_travail_sample_response.json
```

Sample mode is included only to test raw loading locally without API credentials. It still uses the same batch, request, and raw job loaders.

## Dependency Note

The database helper expects `psycopg2` to be installed.

Recommended requirement:

```text
psycopg2-binary
```

The Task 004 API client also requires:

```text
requests
```

## Validation Performed Here

Static Python compilation was executed successfully:

```bash
python -m py_compile $(find src -name '*.py')
```

A lightweight import/request-building check was executed successfully:

```text
- pipeline imports correctly
- request builder creates paginated requests
- source_job_key generation returns france_travail:{source_job_id}
- payload hash is stable for equivalent JSON key ordering
```

A real database load was not executed in this environment because no running PostgreSQL service and no real France Travail credentials are available here.

## Acceptance Criteria Status

| Acceptance criterion | Status |
|---|---|
| Running `python -m src.pipeline.run_france_travail_ingestion` creates one new batch | Implemented |
| API request metadata is stored | Implemented |
| Raw job posting payloads are stored as JSONB | Implemented |
| `batch_id` links all rows from the same run | Implemented |
| `request_id` links job postings to API requests | Implemented |
| `source_job_key` is populated | Implemented |
| `payload_hash` is populated | Implemented |
| Batch status is updated to `success`, `failed`, or `partial_success` | Implemented |
| No business transformations are performed in Python | Implemented |

## Important Design Boundaries

Python ingestion owns:

```text
API calls
batch creation
request metadata storage
raw JSONB payload loading
technical hashes and lineage keys
```

Python ingestion does not own:

```text
staging transformations
warehouse snapshots
skill extraction
seniority inference
relevance scoring
Streamlit dashboard metrics
```

## How to Run

From the repository root:

```bash
python -m src.pipeline.run_france_travail_ingestion
```

For a local sample-mode test after PostgreSQL/raw schema exists:

```bash
export FRANCE_TRAVAIL_SAMPLE_MODE=true
python -m src.pipeline.run_france_travail_ingestion
```

For real API ingestion:

```bash
export FRANCE_TRAVAIL_CLIENT_ID="your_client_id"
export FRANCE_TRAVAIL_CLIENT_SECRET="your_client_secret"
python -m src.pipeline.run_france_travail_ingestion
```

## Handoff to Task 006

Task 005 completes the raw loading boundary.

The next role/task can start dbt setup and transformations from these raw tables:

```text
raw.raw_load_batches
raw.raw_api_requests
raw.raw_france_travail_job_postings
```

Task 006 should define these as dbt sources and start the `raw -> staging` transformation layer.
