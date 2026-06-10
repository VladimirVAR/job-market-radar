# ADR-002: Preserve Raw API Responses as JSONB

## Status

Accepted

## Context

The system collects job postings from public APIs. Source payloads may change over time, and transformation logic may need to be improved later.

If only transformed fields are stored, the original source response is lost.

## Decision

Store every raw job posting payload as JSONB in the raw layer.

Target table:

```text
raw.raw_france_travail_job_postings
```

Main column:

```text
raw_payload_json
```

## Reasoning

Raw preservation allows the system to:

- reprocess data later
- debug transformation errors
- inspect source-level changes
- preserve source truth
- support lineage from marts back to raw payloads
- demonstrate professional ELT design

## Consequences

Positive:

- better reproducibility
- stronger debugging
- more credible data engineering architecture
- easier future transformation changes

Negative:

- larger storage footprint
- raw tables are less user-friendly
- requires clear separation between raw and analytical layers

## Alternatives Considered

### Store only parsed fields

Rejected because it would lose the original API response.

### Store raw payloads as files only

Rejected for MVP because PostgreSQL JSONB keeps the data close to metadata and dbt transformations.

## Engineering Note

Raw preservation is a strong technical review point because it shows that the system is designed for traceability, not just immediate visualization.
