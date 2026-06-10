# Task 006 Report: Create dbt Project

## Status

Implemented as dbt foundation package.

## Role

dbt Transformation Engineer / dbt Engineer.

## Goal

Prepare the dbt foundation so Task 007 can build staging models from existing raw PostgreSQL tables.

## Current Project Context

The previous ingestion work has already produced raw tables and sample raw data.
The dbt project must connect to the same local PostgreSQL database and declare raw tables as dbt sources.

Expected existing raw tables:

```text
raw.raw_load_batches
raw.raw_api_requests
raw.raw_france_travail_job_postings
```

## Implemented Files

```text
dbt_job_market_radar/
  .gitignore
  README.md
  dbt_project.yml
  profiles.yml.example
  macros/
    generate_schema_name.sql
  analyses/
    .gitkeep
  models/
    sources/
      raw_sources.yml
    staging/
      france_travail/
        .gitkeep
    warehouse/
      .gitkeep
    marts/
      .gitkeep
  tests/
    .gitkeep
  seeds/
    .gitkeep
  snapshots/
    .gitkeep
```

## Key Decisions

### 1. PostgreSQL profile example

`profiles.yml.example` uses the `postgres` dbt adapter and reads connection settings from environment variables:

```text
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

The real `profiles.yml` is intentionally not included and should not be committed.

### 2. Raw tables are declared as dbt sources

Defined in:

```text
dbt_job_market_radar/models/sources/raw_sources.yml
```

Sources:

```text
source('raw', 'raw_load_batches')
source('raw', 'raw_api_requests')
source('raw', 'raw_france_travail_job_postings')
```

### 3. source() and ref() boundary

Rule preserved:

```text
raw/external tables -> source()
dbt model dependencies -> ref()
```

Task 007 should start from:

```sql
from {{ source('raw', 'raw_france_travail_job_postings') }}
```

### 4. Schema naming

A custom `generate_schema_name` macro is included so dbt creates models directly in:

```text
staging
warehouse
marts
```

instead of default names such as `public_staging`.

### 5. Source-level tests

Basic tests were added to source definitions for critical raw identifiers and lineage fields:

- `batch_id`
- `request_id`
- `raw_job_posting_id`
- `source_job_key`
- `raw_payload_json`
- `payload_hash`

## Commands to Run Locally

Install dbt PostgreSQL adapter:

```bash
pip install dbt-postgres
```

Create local dbt profile:

```bash
mkdir -p ~/.dbt
cp dbt_job_market_radar/profiles.yml.example ~/.dbt/profiles.yml
```

Run validation:

```bash
dbt debug --project-dir dbt_job_market_radar
dbt parse --project-dir dbt_job_market_radar
dbt build --project-dir dbt_job_market_radar
```

## What Could Not Be Executed Here

`dbt debug` and `dbt parse` were not executed in this environment because the `dbt` CLI is not installed here and the local PostgreSQL service from the user's machine is not available inside this sandbox.

The files are ready to copy into the repository and validate locally.

## Handoff to Task 007

Task 007 can now create:

```text
dbt_job_market_radar/models/staging/france_travail/stg_france_travail_job_postings.sql
dbt_job_market_radar/models/staging/france_travail/stg_france_travail_job_postings.yml
```

The staging model should read raw data with:

```sql
from {{ source('raw', 'raw_france_travail_job_postings') }}
```

and preserve raw lineage columns:

```text
batch_id
request_id
raw_job_posting_id
source_name
source_job_id
source_job_key
search_scope_key
payload_hash
```
