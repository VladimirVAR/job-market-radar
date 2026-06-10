# Task 006: Create dbt Project

## Goal

Create and configure the dbt project for Job Market Radar.

dbt will own all transformations after raw loading.

---

## Context

The architecture requires:

```text
raw -> staging -> warehouse -> marts
```

dbt should read raw tables using `source()` and build all downstream models using `ref()`.

---

## Deliverables

Create:

```text
dbt_job_market_radar/
  dbt_project.yml
  profiles.yml.example
  models/
    sources/
      raw_sources.yml
    staging/
    warehouse/
    marts/
  tests/
  macros/
```

---

## Required dbt Source Definitions

Define raw sources:

```text
raw.raw_load_batches
raw.raw_api_requests
raw.raw_france_travail_job_postings
```

---

## Required Configuration

The dbt project should:

- use PostgreSQL adapter
- define staging models under `staging`
- define warehouse models under `warehouse`
- define marts under `marts`
- use clear materializations
- include documentation blocks where useful

---

## Acceptance Criteria

- `dbt debug` succeeds.
- `dbt parse` succeeds.
- Raw sources are defined in `raw_sources.yml`.
- dbt can connect to local PostgreSQL.
- `profiles.yml.example` is committed, but real `profiles.yml` is not.
- dbt project follows naming conventions.

---

## Implementation Notes

Recommended model organization:

```text
models/
  sources/
  staging/france_travail/
  warehouse/
  marts/
```

Use `source()` only for raw tables.

Use `ref()` for dbt model dependencies.

---

## Dependencies

Task 005.

---

## Next Task

Task 007: Build Staging Models.
