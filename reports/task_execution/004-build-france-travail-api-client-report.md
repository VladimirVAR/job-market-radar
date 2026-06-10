# Task 004 Report: Build France Travail API Client

## Role

Source / Ingestion Engineer

## Scope

Implemented the source-specific France Travail API client package under:

```text
src/ingestion/france_travail/
```

This task intentionally does **not** load data into PostgreSQL. Database loading belongs to Task 005 under `src/loaders/`.

## Files Implemented

```text
src/ingestion/france_travail/auth.py
src/ingestion/france_travail/client.py
src/ingestion/france_travail/request_builder.py
src/ingestion/france_travail/parser.py
src/ingestion/france_travail/__init__.py
```

## What Was Done

### `auth.py`

Implemented environment-based authentication helpers:

- reads `FRANCE_TRAVAIL_CLIENT_ID` from environment variables
- reads `FRANCE_TRAVAIL_CLIENT_SECRET` from environment variables
- supports optional `FRANCE_TRAVAIL_TOKEN_URL`
- supports optional `FRANCE_TRAVAIL_SCOPE`
- requests an OAuth2 access token using client credentials
- caches the token in memory until shortly before expiration
- avoids hardcoded secrets

### `request_builder.py`

Implemented request-building logic:

- builds France Travail search parameters
- supports the `range` pagination parameter
- validates MVP-safe pagination limits
- creates a stable `search_scope_key`
- excludes pagination from `search_scope_key` so multiple pages belong to the same comparable search scope
- keeps source-specific parameter naming inside France Travail package

### `client.py`

Implemented the HTTP client:

- sends authenticated GET requests
- supports search requests
- supports optional offer-detail request by source job id
- retries temporary failures such as 429 and 5xx responses
- measures response time in milliseconds
- returns raw response payload
- returns request metadata needed by `raw.raw_api_requests`
- removes sensitive headers from metadata
- does not write to the database

### `parser.py`

Implemented conservative response parsing:

- extracts raw job records from `resultats`
- extracts only technical source identifier `source_job_id`
- extracts source URL on a best-effort basis
- returns raw job payloads without analytical transformation
- does not infer skills, seniority, contract normalization, relevance score, or business metrics

## Design Boundaries

Python client owns:

```text
API authentication
request building
pagination support
HTTP request execution
retry handling
response metadata capture
raw job object extraction
```

Python client does **not** own:

```text
PostgreSQL insert logic
batch creation
request row persistence
raw JSONB loading
staging transformations
warehouse snapshots
skill extraction
relevance scoring
dashboard metrics
```

## How This Connects to Task 005

Task 005 should use these outputs as inputs for loaders:

- `FranceTravailApiResponse.to_request_metadata()` -> `raw.raw_api_requests`
- `FranceTravailApiResponse.response_payload` -> parser input
- `parse_raw_job_payloads(response_payload)` -> raw payload records for `raw.raw_france_travail_job_postings`

Task 005 must then generate:

```text
batch_id
request_id
source_job_key = france_travail:{source_job_id}
payload_hash
```

and persist rows into:

```text
raw.raw_load_batches
raw.raw_api_requests
raw.raw_france_travail_job_postings
```

## Example Usage

```python
from src.ingestion.france_travail import FranceTravailClient, parse_raw_job_payloads

client = FranceTravailClient()
response = client.search(params={"motsCles": "data engineer"}, page_number=1, page_size=150)

request_metadata = response.to_request_metadata()
raw_jobs = parse_raw_job_payloads(response.response_payload)
```

## Smoke Test Command

After setting credentials in `.env` or shell environment:

```bash
export FRANCE_TRAVAIL_CLIENT_ID="your_client_id"
export FRANCE_TRAVAIL_CLIENT_SECRET="your_client_secret"
python - <<'PY'
from src.ingestion.france_travail import FranceTravailClient, parse_raw_job_payloads

client = FranceTravailClient()
response = client.search(params={"motsCles": "data engineer"}, page_number=1, page_size=10)
print(response.response_status_code)
print(response.error_message)
print(len(parse_raw_job_payloads(response.response_payload)))
PY
```

## Acceptance Criteria Status

| Acceptance criterion | Status |
|---|---|
| Client reads credentials from environment variables | Done |
| No secrets are committed | Done |
| Client can make a test request with valid credentials | Implemented, not executed here because credentials are not available |
| Client supports pagination or is designed to support it | Done |
| Client returns raw response payload and request metadata | Done |
| Client does not perform analytical transformations | Done |
| Errors are handled clearly | Done |
| API-specific logic stays under `src/ingestion/france_travail/` | Done |

## Notes / Decisions to Validate

- Confirm the active France Travail OAuth scope in the developer console. The default is configurable through `FRANCE_TRAVAIL_SCOPE`.
- Confirm whether MVP should use search response payload only or additionally call offer-detail endpoint per job.
- Confirm the exact configured search scopes before Task 005 wires this client into the batch pipeline.

## Handoff

Ready for Task 005: Load Raw Job Postings.
