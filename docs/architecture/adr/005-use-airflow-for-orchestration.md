# ADR-005: Use Airflow for Orchestration

## Status

Accepted

## Context

The project needs a repeatable pipeline that runs ingestion, transformations, validation, and reporting in the correct order.

## Decision

Use Airflow as the orchestration layer.

The MVP DAG should be simple:

```text
start
  -> create_load_batch_and_ingest_france_travail
  -> dbt_build
  -> run_data_quality_checks
  -> generate_weekly_report
  -> end
```

## Reasoning

Airflow is useful because it:

- demonstrates orchestration skills
- makes task dependencies explicit
- supports retries
- supports scheduling
- provides task logs
- is widely used in Data Engineering

## Consequences

Positive:

- realistic pipeline orchestration
- good engineering value
- clear task dependencies
- repeatable execution

Negative:

- adds local setup complexity
- may be heavier than needed for a small project
- requires careful Docker configuration

## Alternatives Considered

### Cron

Rejected because it has lower engineering value and weaker dependency visibility.

### Manual script execution only

Rejected because it does not demonstrate orchestration.

### Prefect/Dagster

Valid alternatives, but Airflow is more commonly recognized and fits the learning goal.

## Engineering Note

Airflow should orchestrate tasks, not contain business transformation logic.
