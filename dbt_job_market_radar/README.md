# dbt Job Market Radar

This folder contains the dbt transformation project for Job Market Radar.

dbt owns all transformations after Python raw loading:

```text
raw -> staging -> warehouse -> marts
```

## Current scope

Task 006 creates the dbt foundation only. It defines the project structure,
PostgreSQL profile example, schema configuration, and raw source definitions.

Task 007 will build the first staging model:

```text
raw.raw_france_travail_job_postings
  -> staging.stg_france_travail_job_postings
```

## Source and ref rules

Use `source()` only for raw/external tables:

```sql
from {{ source('raw', 'raw_france_travail_job_postings') }}
```

Use `ref()` for dependencies between dbt models:

```sql
from {{ ref('stg_france_travail_job_postings') }}
```

Do not reference raw tables directly by schema/table name inside dbt models.

## Local setup

Install the PostgreSQL adapter:

```bash
pip install dbt-postgres
```

Create your local dbt profile from the committed example:

```bash
mkdir -p ~/.dbt
cp dbt_job_market_radar/profiles.yml.example ~/.dbt/profiles.yml
```

The profile reads PostgreSQL settings from environment variables:

```text
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

## Validation commands

From the repository root:

```bash
dbt debug --project-dir dbt_job_market_radar
dbt parse --project-dir dbt_job_market_radar
dbt build --project-dir dbt_job_market_radar
```

For Task 006, `dbt parse` should succeed after installing dbt. `dbt debug` also
requires the local PostgreSQL database to be running and accessible.

## Expected raw sources

The following raw tables must already exist in PostgreSQL:

```text
raw.raw_load_batches
raw.raw_api_requests
raw.raw_france_travail_job_postings
```
