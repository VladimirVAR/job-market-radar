# Power BI Reporting Layer

## Purpose

This document describes the Power BI reporting layer added on top of the dbt marts.

Power BI provides an interactive dashboard for job market analysis and pipeline monitoring.
It is an optional consumption layer alongside the Streamlit dashboard.

---

## Architecture Position

```text
raw -> staging -> warehouse -> marts -> Power BI (this layer)
                                     -> Streamlit
```

Power BI connects directly to the `marts` schema in PostgreSQL.
It does not read from `raw`, `staging`, or `warehouse` schemas.
All business logic and scoring remain in dbt.

---

## Connection Details

| Setting  | Value             |
|----------|-------------------|
| Server   | localhost:5433    |
| Database | job_market_radar  |
| Schema   | marts             |
| Mode     | Import            |

No credentials are stored in the repository.
Connection credentials are entered in Power BI Desktop at connect time.

---

## Consumed Marts

| Mart                       | Used by pages               |
|----------------------------|-----------------------------|
| `mart_job_market_overview` | Market Overview             |
| `mart_skill_demand`        | Market Demand               |
| `mart_location_demand`     | Market Demand               |
| `mart_company_demand`      | Market Demand               |
| `mart_relevant_jobs_flat`  | Relevant Jobs               |
| `mart_pipeline_health`     | Pipeline Monitoring         |

`mart_relevant_jobs_flat` is a flat projection of `mart_relevant_jobs` with all PostgreSQL
ARRAY columns converted to comma-separated text. This is required because the NpgSQL
connector used by Power BI does not support PostgreSQL ARRAY types natively.

`mart_pipeline_health` aggregates freshness and batch history per source, adding health
classification and a human-readable monitoring message.

---

## Dashboard Pages

### Market Overview

Executive summary of the active job market.

Metrics: active job count, company count, location count, relevant job count,
high-match job count, junior-friendly job count, average relevance score.

### Market Demand

Demand signals by company, skill, and location.

Visuals: top hiring companies by job count, top skills by job count,
top locations by job count.

### Relevant Jobs

Actionable shortlist of job postings ranked by candidate-fit score and application priority.

Source: `mart_relevant_jobs_flat`.

Slicers: application priority, candidate fit band, source.

**Note on numeric fields in detail tables:**
`candidate_fit_score` and similar score columns must be set to "Do not summarize"
in Power BI field settings. Power BI defaults numeric fields to Sum aggregation,
which produces incorrect results when the field is used as a row-level value
in a detail table, not an aggregate.

### Pipeline Monitoring

Operational visibility for the ingestion pipeline.

Source: `mart_pipeline_health`.

Displays: last successful load timestamps, total/failed/running batch counts,
current job count by source, freshness status, source health status,
and monitoring messages.

---

## Screenshots

The current Power BI dashboard layout is documented through screenshots:

- [Market Overview](screenshots/powerbi_market_overview.png)
- [Market Demand](screenshots/powerbi_market_demand.png)
- [Relevant Jobs](screenshots/powerbi_relevant_jobs.png)
- [Pipeline Monitoring](screenshots/powerbi_pipeline_monitoring.png)

---

## Local .pbix File

The `.pbix` file is kept outside the repository and is not committed to Git.

Reasons:
- `.pbix` is a binary file and is not diff-friendly.
- Power BI report files frequently change on save even without user edits.
- The file may embed cached data.

The repository documents the connection parameters and consumed marts so that
the report can be rebuilt from scratch or reconnected to a refreshed database.

---

## Refresh Flow

1. Run the ingestion pipeline so new data lands in the raw schema.
2. Run `dbt build` so marts are up to date.
3. Open Power BI Desktop and open the `.pbix` file.
4. Click "Refresh" to import the latest data from PostgreSQL.

If running outside the Airflow DAG, the manual sequence is:

```text
python src/pipeline/run_adzuna_ingestion.py
python src/pipeline/run_france_travail_ingestion.py
dbt build --project-dir dbt_job_market_radar
```

---

## Known Limitations

### Location data quality

`location_name` in the marts currently mixes city names, department-like labels,
numeric INSEE or postal codes, and unknown values. The Power BI MVP filters
out numeric-only values and unknown labels for readability.

Proper location normalization is a planned data modeling improvement and will
require a dedicated dbt model change when implemented.

### Power BI numeric field aggregation

Power BI applies Sum aggregation to numeric columns by default. Score columns
used as row-level identifiers (such as `candidate_fit_score`) must be manually
set to "Do not summarize" in the report field settings. This is a Power BI
behavior, not a data modeling issue.
