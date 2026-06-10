# Task 004: Build France Travail API Client

## Goal

Build the Python client for France Travail API Offres d'emploi.

The client should isolate all source-specific API logic from the rest of the project.

---

## Context

France Travail is the primary MVP source.

The ingestion layer must collect job postings and preserve raw API responses before transformation.

---

## Deliverables

Implement files under:

```text
src/ingestion/france_travail/
```

Expected files:

```text
auth.py
client.py
request_builder.py
parser.py
```

---

## Responsibilities

### `auth.py`

Responsible for:

- reading credentials from environment variables
- obtaining API access token if required
- avoiding hardcoded secrets

### `request_builder.py`

Responsible for:

- defining search parameters
- building request params
- creating stable `search_scope_key`
- supporting pagination parameters

### `client.py`

Responsible for:

- sending HTTP requests
- retrying temporary failures
- returning response payloads
- returning response metadata
- measuring response time

### `parser.py`

Responsible for:

- identifying job records inside the API response
- extracting source job id
- returning raw job payloads without deep transformation

---

## Acceptance Criteria

- Client reads credentials from environment variables.
- No secrets are committed.
- Client can make a test request to France Travail API.
- Client supports pagination or is designed to support it.
- Client returns raw response payload and request metadata.
- Client does not perform analytical transformations.
- Errors are handled clearly.
- API-specific logic stays under `src/ingestion/france_travail/`.

---

## Implementation Notes

The client should not load data into the database directly.

Database loading belongs to `src/loaders/`.

The client should return data structures that loaders can persist.

---

## Dependencies

Task 003.

---

## Next Task

Task 005: Load Raw Job Postings.
