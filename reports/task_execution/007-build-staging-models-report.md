# Task 007 Execution Report — Build Staging Models

## Role

dbt Transformation Engineer

## Task

Task 007 — Build Staging Models

## Objective

Build the first dbt transformation model for France Travail job postings:

```text
raw.raw_france_travail_job_postings
  -> staging.stg_france_travail_job_postings
```

This task is staging-only. No warehouse models, marts, skill extraction, relevance scoring, or dashboard logic were added.

## Created files

```text
dbt_job_market_radar/models/staging/france_travail/stg_france_travail_job_postings.sql
dbt_job_market_radar/models/staging/france_travail/stg_france_travail_job_postings.yml
```

## Model created

### `stg_france_travail_job_postings`

**Expected physical relation:**

```text
staging.stg_france_travail_job_postings
```

**Grain:**

```text
one row per raw.raw_france_travail_job_postings.raw_job_posting_id
```

The model preserves every raw job row from ingestion. It does not deduplicate records. Deduplication and current-state logic remain reserved for warehouse models in Task 008.

## Source usage

The SQL model reads raw data only through dbt `source()`:

```sql
from {{ source('raw', 'raw_france_travail_job_postings') }}
```

No direct reference to `raw.raw_france_travail_job_postings` was used inside the model SQL.

## Required lineage columns preserved

The model preserves:

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

These columns are required for downstream lineage from warehouse and marts back to the raw API payload.

## Business fields parsed

The model parses:

```text
job_title
company_name
location_raw
city
region
country
contract_type
work_mode
seniority_level
description_text
published_at
updated_at
retrieved_at
source_url
```

## JSON path assumptions

The model uses these France Travail-style paths:

```text
job_title:
  raw_payload_json ->> 'intitule'

company_name:
  raw_payload_json -> 'entreprise' ->> 'nom'

location_raw:
  raw_payload_json -> 'lieuTravail' ->> 'libelle'

city:
  raw_payload_json -> 'lieuTravail' ->> 'commune'
  or raw_payload_json -> 'lieuTravail' ->> 'nomCommune'
  or best-effort extraction from lieuTravail.libelle

country:
  raw_payload_json -> 'lieuTravail' ->> 'pays'
  fallback: 'France'

contract_type:
  raw_payload_json ->> 'typeContrat'
  or raw_payload_json ->> 'typeContratLibelle'

work_mode:
  raw_payload_json ->> 'teletravail'

seniority_level:
  raw_payload_json ->> 'experienceLibelle'
  or raw_payload_json ->> 'experienceExige'

description_text:
  raw_payload_json ->> 'description'

published_at:
  raw_payload_json ->> 'dateCreation'

updated_at:
  raw_payload_json ->> 'dateActualisation'

source_url:
  raw_payload_json -> 'origineOffre' ->> 'urlOrigine'
  or raw_payload_json ->> 'urlOrigine'
  or raw_payload_json ->> 'url'
```

## Tests added

The YAML file adds dbt tests for:

```text
raw_job_posting_id not null
raw_job_posting_id unique
batch_id not null
request_id not null
source_name not null
source_name accepted_values: ['france_travail']
source_job_id not null
source_job_key not null
search_scope_key not null
payload_hash not null
```

Optional `job_title not null` and `description_text not null` tests were not added yet because the task instructions say to add them only if the current sample/raw source reliably contains those fields.

## dbt commands to run locally

From the repository root:

```bash
dbt parse --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar
dbt build --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar --select staging
```

Or specifically:

```bash
dbt build --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar --select stg_france_travail_job_postings
```

## Validation SQL to run locally

```sql
select count(*)
from staging.stg_france_travail_job_postings;
```

Expected result for current sample mode:

```text
same row count as raw.raw_france_travail_job_postings
```

The current task assignment says the local sample is likely:

```text
2 rows
```

Inspect parsed fields:

```sql
select
    raw_job_posting_id,
    source_job_key,
    job_title,
    company_name,
    location_raw,
    contract_type,
    published_at,
    source_url
from staging.stg_france_travail_job_postings
limit 20;
```

## Execution status in this environment

Static artifact creation completed.

I could not run `dbt parse` or `dbt build` in this sandbox because it does not have access to the user's local PostgreSQL database and project runtime. The SQL and YAML were prepared to match the task specification and should be validated locally with the commands above.

Static validation performed here:

```text
stg_france_travail_job_postings.yml parsed successfully as YAML.
```

## Changes not made

No changes were made to:

```text
dbt_project.yml
raw_sources.yml
macros
profiles.yml.example
```

No local secrets or real `profiles.yml` were created.

## Known limitations

- `region` is currently returned as `null::text` because the MVP raw France Travail payload may not provide a reliable region field.
- `city` is best-effort and may need improvement after inspecting more real France Travail payloads.
- `work_mode` and `seniority_level` are light staging classifications only; final analytical logic can be refined later in warehouse/marts if needed.
- No deduplication is performed in staging by design.
- No skill extraction or relevance scoring is implemented in this task by design.

## Handoff to Task 008

Task 008 can now build warehouse models from:

```sql
{{ ref('stg_france_travail_job_postings') }}
```

The staging model provides the lineage and typed business fields required for warehouse snapshots.
