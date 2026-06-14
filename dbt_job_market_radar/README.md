# dbt Job Market Radar

This folder contains the dbt transformation project for Job Market Radar.

dbt owns all transformations after Python raw loading:

```text
raw -> staging -> warehouse -> marts
```

## Current scope

The dbt project now supports the multi-source pipeline used by the public
Job Market Radar project:

```text
France Travail API -> raw.raw_france_travail_job_postings
Adzuna API         -> raw.raw_adzuna_job_postings

raw -> staging -> warehouse -> marts
```

The raw data is loaded by Python ingestion jobs. dbt starts after raw loading
and builds the staging, warehouse, and mart layers.

## Source and ref rules

Use `source()` only for raw/external tables:

```sql
from {{ source('raw', 'raw_france_travail_job_postings') }}
from {{ source('raw', 'raw_adzuna_job_postings') }}
```

Use `ref()` for dependencies between dbt models:

```sql
from {{ ref('stg_france_travail_job_postings') }}
from {{ ref('stg_adzuna_job_postings') }}
```

Do not reference raw tables directly by schema/table name inside dbt models.

## Local setup

Install the PostgreSQL adapter:

```bash
pip install dbt-postgres
```

This repository keeps a project-local dbt profile in `dbt_job_market_radar`.
Run dbt from the repository root with both `--project-dir` and `--profiles-dir`:

```bash
dbt debug --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar
dbt build --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar
```

The profile reads PostgreSQL settings from environment variables when they are
provided:

```text
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
DBT_THREADS
```

For local Windows runs against Docker Desktop, the default profile values use:

```text
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5433
DBT_THREADS=1
```

Inside Docker/Airflow, `docker-compose.yml` overrides the connection to use the
Docker service name instead:

```text
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DBT_THREADS=1
```

## Validation commands

From the repository root:

```bash
dbt debug --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar
dbt parse --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar
dbt build --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar
```

For this local project, `threads: 1` is intentional. The pipeline is small and
mostly linear, and single-threaded dbt runs are easier to debug and more stable
against the local PostgreSQL container.

## Expected raw sources

The following raw tables must already exist in PostgreSQL:

```text
raw.raw_load_batches
raw.raw_api_requests
raw.raw_france_travail_job_postings
raw.raw_adzuna_job_postings
```
