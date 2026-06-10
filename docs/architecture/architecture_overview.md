# Architecture Overview

## Project

**Job Market Radar** is a local Data Engineering data product that helps a junior or career-switcher Data Engineer candidate understand the job market in France and Europe in a structured way.

The system collects job postings from public job APIs, preserves raw API responses, transforms the data into clean analytical layers, extracts skills and market signals, calculates job relevance against a candidate profile, and exposes the results through dashboards and reports.

The MVP uses **France Travail API Offres d'emploi** as the primary source.

Future sources may include:

- Adzuna API
- The Muse API

The MVP explicitly excludes LinkedIn and Indeed scraping.

---

## Architecture Decision

Job Market Radar uses a simple batch-oriented analytical architecture:

```text
sources
  -> raw
  -> staging
  -> warehouse
  -> marts
  -> dashboard / reports
```

The project is designed as a clean local data product, not as an enterprise platform.

The architecture prioritizes:

- raw API preservation
- batch tracking
- request metadata
- reproducible transformations
- lineage from marts back to raw data
- simple local deployment with Docker
- clear technical documentation for public project review

---

## Target Stack

| Area | Tool |
|---|---|
| Ingestion | Python |
| Local database | PostgreSQL |
| Transformation | dbt |
| SQL modeling | SQL |
| Orchestration | Airflow |
| Dashboard | Streamlit |
| Local reproducibility | Docker / docker-compose |
| Documentation | Markdown |

---

## High-Level Architecture

```text
France Travail API
    |
    v
Python ingestion
    |
    v
PostgreSQL raw schema
    |
    v
dbt staging models
    |
    v
dbt warehouse models
    |
    v
dbt marts
    |
    v
Streamlit dashboard / Markdown reports
```

---

## Component Boundaries

### Python

Python owns interaction with external APIs and raw loading.

Python is responsible for:

- API authentication
- request building
- pagination
- retry handling
- basic response validation
- raw JSON preservation
- batch creation
- request metadata storage
- raw payload loading into PostgreSQL

Python does **not** own:

- analytical transformations
- relevance scoring
- dashboard-ready aggregations
- final business metrics

---

### PostgreSQL

PostgreSQL is the local analytical store.

It stores:

- raw API payloads
- ingestion metadata
- dbt staging models
- dbt warehouse models
- dbt marts
- dashboard-ready data

---

### dbt

dbt owns all transformations after raw loading.

dbt is responsible for:

- staging models
- warehouse models
- marts
- data tests
- model documentation
- transformation lineage

dbt should use:

- `source()` for raw/external tables
- `ref()` for dependencies between dbt models

---

### Airflow

Airflow owns orchestration.

Airflow is responsible for:

- task order
- scheduling
- retries
- pipeline execution monitoring
- triggering Python ingestion
- triggering dbt build
- triggering validation checks
- triggering report generation

Airflow should not contain business transformation logic.

---

### Streamlit

Streamlit is only a consumption layer.

Streamlit is responsible for:

- dashboard pages
- filters
- charts
- tables
- exploration UI

Streamlit should read from `marts` only for business pages.

It should not calculate relevance scores or perform core transformations.

---

## Core Architecture Principles

1. Preserve raw API responses before transformation.
2. Track every pipeline run as a load batch.
3. Store API request metadata.
4. Keep lineage from marts back to raw payloads.
5. Use dbt for transformations after raw loading.
6. Use Streamlit only as a consumption layer.
7. Use English names for files, schemas, tables, columns, and code identifiers.
8. Use `snake_case`.
9. Define grain for every table and model.
10. Keep secrets out of Git.
11. Use `.env` and `.env.example`.
12. Document trade-offs honestly.

---

## Repository Structure

```text
job-market-radar/
  README.md
  docker-compose.yml
  .env.example
  .gitignore
  requirements.txt
  Makefile

  src/
    common/
    ingestion/
      france_travail/
    loaders/
    pipeline/
    reporting/

  dags/

  dbt_job_market_radar/
    models/
      sources/
      staging/
      warehouse/
      marts/
    tests/
    macros/

  sql/
    ddl/
    analytics/

  streamlit_app/
    pages/

  docs/
    architecture/
      architecture_overview.md
      data_flow.md
      data_model.md
      source_to_target_contract.md
      adr/

  data/
    sample/

  tasks/
```

---

## MVP Architecture Scope

The MVP includes:

- France Travail API ingestion
- raw JSONB preservation
- batch tracking
- API request metadata
- dbt staging models
- warehouse snapshot model
- current-state model
- rule-based skill extraction
- simple relevance scoring
- basic data quality checks
- Streamlit dashboard
- Markdown documentation

---

## Future Architecture Extensions

Possible future extensions:

- Add Adzuna API
- Add The Muse API
- Add cross-source canonical job matching
- Add better skill taxonomy
- Add candidate profile version comparison
- Add historical market trends
- Add GitHub Actions
- Add optional cloud deployment

These extensions should not be part of the first MVP unless the core pipeline is already stable.

---

## Key Trade-Offs

### PostgreSQL instead of cloud warehouse

PostgreSQL is enough for a small local MVP and keeps the project reproducible.

Trade-off: it does not demonstrate a cloud warehouse such as Snowflake or BigQuery.

---

### Rule-based skill extraction instead of ML

Rule-based extraction is transparent and explainable.

Trade-off: it may miss skills or produce false positives.

---

### Single source in MVP

France Travail API is enough to demonstrate end-to-end engineering.

Trade-off: market coverage is limited until future APIs are added.

---

### Batch architecture instead of streaming

Job postings do not require real-time processing in the MVP.

Trade-off: the system is not designed for low-latency updates.

---

## Final Architecture Position

Job Market Radar should be implemented as a clean batch-oriented local data product.

The system should be simple enough for one person to build, but structured enough to demonstrate professional Data Engineering practices.
