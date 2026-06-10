# ADR-001: Use PostgreSQL as the Local Analytical Store

## Status

Accepted

## Context

Job Market Radar needs a local database to store raw API responses, metadata, dbt models, analytical marts, and dashboard-ready outputs.

The project is a MVP public release built by one person. It must be reproducible locally and easy to run with Docker.

## Decision

Use PostgreSQL as the local analytical store.

## Reasoning

PostgreSQL is a strong fit for this MVP because it:

- runs easily in Docker
- supports relational modeling
- supports JSONB for raw API payloads
- works well with Python
- works well with dbt
- is familiar to many Data Engineering teams
- is simple enough for local reproducibility

## Consequences

Positive:

- simple local setup
- no cloud account required
- easy to inspect data manually
- good support for raw JSONB payloads
- good enough for local MVP-scale analytical workloads

Negative:

- does not demonstrate Snowflake, BigQuery, or Redshift
- is not optimized for large analytical workloads
- does not represent a modern cloud warehouse architecture

## Alternatives Considered

### Snowflake

Rejected for MVP because it adds cloud setup, credentials, billing, and deployment complexity.

### BigQuery

Rejected for MVP because it requires GCP setup and adds unnecessary complexity for a local local data product.

### SQLite

Rejected because it is too limited for this project, especially for schemas, dbt workflows, and JSONB-style raw preservation.

## MVP Note

PostgreSQL is acceptable for the MVP because the goal is to keep the system reproducible locally while demonstrating architecture, modeling, lineage, dbt transformations, and validation rather than cloud scale.
