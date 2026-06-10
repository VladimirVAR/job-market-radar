# ADR-003: Track Every Pipeline Run as a Load Batch

## Status

Accepted

## Context

The system runs repeatedly and collects job postings over time.

To understand when data was loaded, how many records were collected, and which run produced which rows, the pipeline needs batch tracking.

## Decision

Create one `batch_id` for every pipeline execution.

Target table:

```text
raw.raw_load_batches
```

The `batch_id` is propagated through raw, staging, warehouse snapshots, and selected marts.

## Reasoning

Batch tracking allows the system to answer:

- When was this data loaded?
- Which run produced this job posting?
- Did the latest run succeed?
- How many records were loaded?
- Which jobs are new?
- Which jobs disappeared from a comparable search scope?

## Consequences

Positive:

- clear operational lineage
- easier debugging
- supports historical analysis
- supports snapshot/current-state logic
- makes pipeline runs auditable

Negative:

- adds metadata tables
- requires all ingestion code to consistently pass `batch_id`
- slightly increases model complexity

## Alternatives Considered

### Use only timestamps

Rejected because timestamps alone are not enough to group a full pipeline execution.

### No batch tracking

Rejected because it would make lineage and historical analysis weak.

## Engineering Note

Batch tracking is one of the clearest ways to show professional pipeline thinking.
