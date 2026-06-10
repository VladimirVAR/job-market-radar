# Task 013 — Activate Live France Travail API Ingestion

## Role

Source / Ingestion Engineer with Data Quality support.

## Goal

Validate live France Travail API ingestion end-to-end.

## Current Context

Tasks 001–012 completed the technical MVP. Sample-mode validation was not enough for final release confidence.

## Required Work

Run live mode with credentials configured locally and sample mode disabled.

Expected commands:

```bash
python -m src.pipeline.run_france_travail_ingestion
dbt build --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar
python -m src.pipeline.run_data_quality_checks
streamlit run streamlit_app/app.py
```

Required local live-mode values:

```text
FRANCE_TRAVAIL_SAMPLE_MODE=false
FRANCE_TRAVAIL_CLIENT_ID=configured locally
FRANCE_TRAVAIL_CLIENT_SECRET=configured locally
FRANCE_TRAVAIL_SEARCH_KEYWORDS=data engineer,analytics engineer
FRANCE_TRAVAIL_MAX_PAGES=1
FRANCE_TRAVAIL_PAGE_SIZE=50
```

## Constraints

- Do not commit `.env`.
- Do not commit secrets.
- Do not remove sample mode.
- Do not redesign ingestion.
- Fix only blockers for live validation.

## Deliverables

```text
live ingestion validation
dbt build on live data
data quality validation
Streamlit live dashboard validation
reports/task_execution/013-activate-live-france-travail-ingestion-report.md
```

## Definition of Done

Task 013 is complete when live ingestion, dbt build, data quality, and Streamlit validation succeed or blockers are documented, and the report exists.
