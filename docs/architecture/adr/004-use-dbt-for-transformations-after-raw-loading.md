# ADR-004: Use dbt for Transformations After Raw Loading

## Status

Accepted

## Context

Job Market Radar needs to transform raw API payloads into staging, warehouse, and marts.

The project should demonstrate modern ELT practices and clear transformation lineage.

## Decision

Use dbt for all transformations after raw loading.

Python loads raw data.

dbt builds:

```text
staging -> warehouse -> marts
```

## Reasoning

dbt is a good fit because it provides:

- SQL-based transformations
- explicit model dependencies
- tests
- documentation
- lineage graph
- reproducible builds
- clear separation between ingestion and transformation

## Consequences

Positive:

- strong engineering value
- clean transformation logic
- better documentation
- easier testing
- clear lineage

Negative:

- requires dbt project setup
- some transformations may be easier in Python but should be kept in SQL/dbt for transparency
- adds another tool to maintain

## Alternatives Considered

### Transform everything in Python

Rejected because it would hide analytical logic inside scripts and reduce dbt engineering value.

### Transform directly in Streamlit

Rejected because the dashboard should be a consumption layer only.

### Use only raw SQL scripts

Rejected because dbt provides better structure, tests, docs, and lineage.

## Engineering Note

Using dbt clearly shows that the project follows modern analytics engineering and ELT practices.
