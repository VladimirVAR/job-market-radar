# Job Market Radar Demo Guide

## 1. Demo Goal

The goal of the demo is to present Job Market Radar as a small but complete Data Engineering data product.

The demo should show that the project is more than a dashboard. It has:

- source ingestion
- raw preservation
- batch tracking
- dbt transformations
- warehouse modeling
- dashboard-ready marts
- data quality checks
- Airflow orchestration
- Streamlit presentation

The strongest message:

> This project turns noisy job-search data into an analytical system that helps a Data Engineering candidate identify relevant jobs, demanded skills, and skill gaps.

---

## 2. What to Show First

Start with the README.

Show:

1. Project summary
2. Architecture diagram
3. Pipeline flow
4. Dashboard summary
5. Validation and limitations

Keep the introduction short. The viewer should understand the project in the first 2 minutes.

Suggested opening:

> Job search for junior Data Engineering roles is noisy. I built Job Market Radar to collect job postings from public APIs, preserve the raw data, transform it into analytical models, and expose relevant opportunities and skill signals through marts and a Streamlit dashboard.

---

## 3. Architecture Walkthrough

Show the architecture flow:

```text
France Travail / sample source
  -> raw PostgreSQL tables
  -> dbt staging models
  -> dbt warehouse models
  -> dbt marts
  -> data quality checks
  -> Airflow orchestration
  -> Streamlit dashboard
```

Explain each layer briefly:

- Python owns API interaction and raw loading.
- PostgreSQL stores raw data, metadata, dbt models, and marts.
- dbt owns transformations.
- Airflow orchestrates the pipeline.
- Streamlit reads prepared marts.

Key talking point:

> I intentionally separated ingestion, transformation, orchestration, validation, and presentation so each tool has a clear responsibility.

---

## 4. Pipeline Walkthrough

Show or explain the pipeline run sequence:

```text
start
  -> ingest_france_travail_raw_jobs
  -> dbt_build
  -> run_data_quality_checks
  -> generate_weekly_report placeholder
  -> end
```

Explain:

- Ingestion creates a load batch.
- API request metadata is stored.
- Raw job postings are preserved as JSONB.
- dbt builds staging, warehouse, and marts.
- validation checks run after transformations.
- Streamlit consumes the resulting marts.

Key talking point:

> Airflow coordinates the workflow, but it does not contain business transformation logic.

---

## 5. dbt Layers Walkthrough

Show the dbt project structure:

```text
models/
  sources/
  staging/
  warehouse/
  marts/
```

Explain:

### Sources

Raw PostgreSQL tables are declared as dbt sources.

### Staging

Staging parses raw France Travail JSON into typed columns.

### Warehouse

Warehouse models create historical snapshots and current-state job models.

### Marts

Marts expose dashboard-ready outputs such as relevant jobs, skill demand, missing skills, companies, locations, and weekly summaries.

Key talking point:

> The dashboard does not calculate core metrics. Those are prepared in dbt marts, where they can be tested, documented, and reused.

---

## 6. Data Quality Walkthrough

Show the validation strategy.

Explain that a successful Airflow task is not enough.

A successful pipeline means:

- ingestion completed
- dbt build completed
- data quality checks passed
- dashboard marts are available

Mention checks such as:

- latest batch exists
- raw payloads are not null
- source job keys are not null
- current model has one row per canonical job key
- relevance scores are between 0 and 100
- marts are not empty after successful ingestion

Command to show:

```bash
python -m src.pipeline.run_data_quality_checks
```

Key talking point:

> The quality checks protect the difference between code that ran and data that is trustworthy enough to analyze.

---

## 7. Airflow DAG Walkthrough

Show the Airflow DAG if available.

Explain:

- manual trigger is supported
- task dependencies are explicit
- logs are visible per task
- validation runs after dbt build
- report generation is currently a placeholder

Manual trigger command:

```bash
airflow dags trigger job_market_radar
```

If Airflow runs in Docker, use the Airflow UI or execute the command inside the appropriate Airflow container.

Key talking point:

> I kept the DAG simple because the MVP goal is a clear, explainable batch pipeline rather than complex orchestration.

---

## 8. Streamlit Dashboard Walkthrough

Run:

```bash
streamlit run streamlit_app/app.py
```

Suggested page order:

1. Overview
2. Relevant Jobs
3. Skill Radar
4. Locations
5. Companies
6. Weekly Report
7. Data Freshness

Explain:

- Overview shows high-level market signals.
- Relevant Jobs shows jobs ranked by Candidate Fit Score and application priority.
- Relevant Jobs keeps the main table focused and moves explanations, matched skills, growth-skill gaps, reason codes, flags, and component scores into a details section.
- Skill Radar shows demanded and missing skills.
- Locations and Companies show market activity.
- Weekly Report summarizes changes.
- Data Freshness shows whether the data is recent and reliable.

Key talking point:

> The dashboard is intentionally simple. The point is not visual complexity; the point is that it sits on top of modeled, tested marts. Streamlit does not calculate Candidate Fit Score; it displays fields prepared and tested in dbt.

---

## 9. Key Talking Points

Use these during a technical review:

### Raw preservation

> I store raw API responses as JSONB so I can debug, reprocess, and preserve source truth.

### Batch tracking

> Every pipeline run creates a batch_id, which gives operational lineage across raw, staging, warehouse, and marts.

### dbt transformations

> Python stops after raw loading. dbt owns staging, warehouse, marts, tests, and transformation lineage.

### Snapshot/current-state modeling

> Job postings change over time, so I model both historical observations and latest known state.

### Marts before dashboard

> Streamlit consumes marts only. This keeps business logic out of the UI.

### Validation

> Airflow success is not enough; I added quality checks that protect lineage, uniqueness, freshness, and dashboard correctness.

### Honest MVP scope

> This is a local MVP, not a production hiring platform.

---

## 10. Known Limitations

Be explicit:

- The MVP uses France Travail / sample data only.
- Live API mode may require valid credentials.
- Local demo data may be small.
- Skill extraction is rule-based.
- Candidate Fit Score and relevance scoring are simple and explainable, not ML-based.
- Weekly history is limited until more scheduled runs accumulate.
- Streamlit UI is intentionally simple.
- `generate_weekly_report` is currently a placeholder.
- Deployment is not included in MVP.
- No LinkedIn or Indeed scraping is used.

---

## 11. Future Roadmap

Mention realistic next steps:

- Add Adzuna or The Muse as additional sources.
- Improve skill extraction with better NLP.
- Add richer relevance / Candidate Fit scoring.
- Add longer historical trend tracking.
- Add salary normalization if reliable data exists.
- Add CI checks.
- Add optional hosted deployment.
- Generate weekly Markdown reports automatically.
- Add screenshots for GitHub demo documentation.

---

## 12. Recommended Demo Length

### 3-minute project overview

1. Problem
2. Product idea
3. Architecture diagram
4. Dashboard overview
5. Tech stack
6. Honest limitations

### 10-minute technical walkthrough

1. Problem
2. Architecture
3. Raw ingestion
4. dbt layers
5. Snapshot/current-state logic
6. Marts and dashboard
7. Validation
8. Trade-offs
9. Future improvements

### 20-minute deep-dive version

Add:

- source-to-target mapping
- data catalog
- dbt tests
- Airflow logs
- sample SQL/showcase queries
- code walkthrough of selected modules
