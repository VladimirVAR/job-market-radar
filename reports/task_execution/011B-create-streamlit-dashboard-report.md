# Task 011B Execution Report — Create Streamlit Dashboard

## Role

Streamlit Dashboard Engineer

## Task

Implement the MVP Streamlit dashboard for the Job Market Radar project using the analytics marts prepared by dbt.

## Architectural Boundary

Streamlit is implemented as a consumption layer only.

Business pages read from `marts.*` models only.

The dashboard does not:

- read raw JSON payloads
- query `raw.*`, `staging.*`, or `warehouse.*` for business pages
- calculate relevance scores
- extract skills
- calculate missing skills
- calculate weekly summaries
- duplicate dbt business logic

## Implemented Files

```text
streamlit_app/app.py
streamlit_app/db.py
streamlit_app/pages/1_overview.py
streamlit_app/pages/2_relevant_jobs.py
streamlit_app/pages/3_skill_radar.py
streamlit_app/pages/4_locations.py
streamlit_app/pages/5_companies.py
streamlit_app/pages/6_weekly_report.py
streamlit_app/pages/7_data_freshness.py
```

## Mart Dependencies

The dashboard uses the following marts:

```text
marts.mart_job_market_overview
marts.mart_relevant_jobs
marts.mart_skill_demand
marts.mart_missing_skills
marts.mart_location_activity
marts.mart_company_activity
marts.mart_weekly_market_summary
marts.mart_data_freshness
```

## Page Summary

### Overview

Shows high-level KPIs, top demanded skills, and top locations.

### Relevant Jobs

Shows a filterable job table with:

- job title
- company
- location
- contract type
- work mode
- seniority level
- relevance score
- matched candidate skills
- missing growth skills
- relevance reason
- source URL

Filters include city, work mode, seniority, contract type, minimum relevance score, junior-friendly flag, and skill text search.

### Skill Radar

Shows skill demand and missing/growth skills using marts prepared by dbt.

### Locations

Shows job distribution and average relevance by location.

### Companies

Shows active companies and average relevance by company.

### Weekly Report

Shows the current weekly market summary. Historical week-over-week comparison is treated as a known MVP limitation when `has_enough_history` is false.

### Data Freshness

Shows latest pipeline/data status from `marts.mart_data_freshness`.

## Database Connection

The dashboard reads PostgreSQL connection settings from environment variables:

```text
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

No credentials are hardcoded.

## Guardrails

`streamlit_app/db.py` includes a query boundary check that rejects dashboard queries referencing:

```text
raw.
staging.
warehouse.
```

It also requires queries to explicitly reference `marts.*`.

## Validation Commands

From repository root:

```bash
streamlit run streamlit_app/app.py
```

Recommended SQL checks:

```sql
select * from marts.mart_job_market_overview;
select * from marts.mart_relevant_jobs limit 10;
select * from marts.mart_skill_demand;
select * from marts.mart_data_freshness;
```

## Notes

The implementation prioritizes demo clarity over visual complexity.

The dashboard is intentionally thin. Any new business metric should be added upstream in dbt marts before being displayed in Streamlit.


## Local Integration Validation

Local validation was executed after integrating the dashboard files into the main repository.

Validation steps completed:

```bash
python -c "import streamlit, sqlalchemy, psycopg2, pandas; print('streamlit deps ok')"
```

```bash
python -m py_compile streamlit_app/app.py streamlit_app/db.py streamlit_app/pages/1_overview.py streamlit_app/pages/2_relevant_jobs.py streamlit_app/pages/3_skill_radar.py streamlit_app/pages/4_locations.py streamlit_app/pages/5_companies.py streamlit_app/pages/6_weekly_report.py streamlit_app/pages/7_data_freshness.py
```

```bash
streamlit run streamlit_app/app.py
```

Validated pages:

* app
* overview
* relevant jobs
* skill radar
* locations
* companies
* weekly report
* data freshness

Integration fixes applied:

* Added `SQLAlchemy>=2.0.0` to `requirements.txt`.
* Updated Streamlit pages to match the current mart column names.
* Fixed Data Freshness UUID rendering for `st.metric`.
* Converted UUID values before displaying the freshness details dataframe.

Final result:

The Streamlit dashboard starts successfully, connects to PostgreSQL, reads from `marts.*`, and all MVP pages render without blocking runtime errors.

Known non-blocking warning:

Streamlit currently warns that `use_container_width` should eventually be replaced by `width`. This is a future compatibility cleanup and does not block Task 011B acceptance.


## Handoff

Next role: Documentation / Demo Engineer.

Recommended next task:

```text
Task 012 — Write Demo Docs
```
