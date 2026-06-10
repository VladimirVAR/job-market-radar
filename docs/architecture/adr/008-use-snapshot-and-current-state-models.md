# ADR-008: Use Snapshot and Current-State Models

## Status

Accepted

## Context

Job postings change over time. A posting can appear, be updated, disappear, and possibly reappear.

The system needs to support both historical analysis and current dashboard views.

## Decision

Use two warehouse models:

```text
warehouse.wh_job_posting_snapshots
warehouse.wh_job_posting_current
```

Snapshots store historical observations.

Current-state exposes the latest known state.

## Reasoning

This design supports:

- new job detection
- changed job detection
- inactive/missing job detection
- historical analysis
- current dashboard views
- weekly summaries

## Consequences

Positive:

- clear historical tracking
- current views stay simple
- supports weekly change analysis
- supports lineage from current state to raw payloads

Negative:

- more complex than overwriting current rows
- requires careful logic for missing jobs
- inactive status depends on comparable search scopes

## Alternatives Considered

### Overwrite current job table only

Rejected because it loses history.

### Full event sourcing

Rejected because it is too complex for MVP.

### dbt snapshots only

Possible, but custom snapshot models provide more explicit control over search scopes and job lifecycle.

## Important Limitation

A job should only be marked inactive when it is missing from a later batch with the same `search_scope_key`.

Missing from a different search scope does not mean the job disappeared from the source.

## Engineering Note

Snapshot/current-state modeling is a strong demonstration of warehouse design and analytical thinking.
