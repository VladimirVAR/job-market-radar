# Task 011A — Build Analytics Marts

## Role

Analytics / Marts Engineer.

## Goal

Create dashboard-ready analytical marts before Streamlit development.

## Current Context

Tasks 001–010 created the local infrastructure, raw ingestion, dbt foundation, warehouse models, validation checks, and Airflow DAG. Streamlit needs product-facing marts first.

## Required Work

Build marts for market overview, relevant jobs, skill demand, missing skills, location activity, company activity, weekly summary, and data freshness.

This task was inserted before Streamlit because:

```text
Streamlit must consume marts only.
```

## Constraints

- Do not put dashboard business logic in Streamlit.
- Do not make Streamlit calculate relevance scores or skill demand.
- Use dbt marts under `dbt_job_market_radar/models/marts/`.
- Keep mart grains documented.
- Keep MVP logic simple and explainable.

## Deliverables

```text
dbt marts
mart tests
showcase queries
reports/task_execution/011A-build-analytics-marts-report.md
```

## Definition of Done

Task 011A is complete when marts build successfully, are dashboard-ready, have core validation, answer showcase questions, and are documented in a task report.
