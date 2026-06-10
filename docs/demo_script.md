# Demo Script

## Purpose

This document provides a spoken demo script for presenting Job Market Radar in a technical project review or walkthrough.

The script is intentionally practical. It should be adapted to the available time.

---

## 1. Opening

> Job search for junior Data Engineering roles is noisy. Job titles vary, skill requirements are inconsistent, and it is hard to understand which roles are realistic for a candidate profile.
>
> I built Job Market Radar as a small Data Engineering data product that collects job postings, preserves raw API data, transforms it into analytical models, extracts market signals, and helps identify relevant jobs and skill gaps.

---

## 2. Product Framing

> The goal is not to build another job board. The goal is to turn job postings into structured analytical data.
>
> The MVP user is a junior or career-switching Data Engineer candidate in France / Europe.
>
> The product answers questions like: which jobs are relevant, which skills are demanded, which skills are missing, which cities are active, and what changed recently.

---

## 3. Architecture Walkthrough

Show the architecture diagram.

> The architecture is a batch-oriented ELT flow:

```text
France Travail / sample source
  -> raw PostgreSQL tables
  -> dbt staging models
  -> dbt warehouse models
  -> dbt marts
  -> Streamlit dashboard
```

> Python handles API access and raw loading. PostgreSQL is the local analytical store. dbt handles transformations and tests. Airflow orchestrates the workflow. Streamlit displays prepared marts.

---

## 4. Ingestion and Raw Preservation

> Every pipeline run creates a load batch. Each API request is tracked separately, and each raw job posting payload is stored as JSONB.
>
> This is important because it preserves the original source response. If I improve transformation logic later, I can reprocess the raw data instead of calling the API again or losing information.

Mention raw tables:

```text
raw.raw_load_batches
raw.raw_api_requests
raw.raw_france_travail_job_postings
```

---

## 5. dbt Transformation Layers

> After raw loading, Python stops. dbt owns all transformations.

Show dbt layers:

```text
sources -> staging -> warehouse -> marts
```

> Staging parses raw JSON into typed fields. Warehouse creates historical snapshots and current-state job models. Marts prepare product-facing outputs for the dashboard.

---

## 6. Warehouse Modeling

> Job postings can change over time, so I do not just overwrite current rows.
>
> I use a snapshot model to preserve observations and a current-state model to expose the latest known state.

Mention:

```text
warehouse.wh_job_posting_snapshots
warehouse.wh_job_posting_current
```

> This supports historical analysis, current dashboard views, and weekly change detection.

Important limitation to mention:

> A job should only be marked inactive when it disappears from a later comparable search scope.

---

## 7. Skill Extraction and Candidate Fit Scoring

> The MVP uses rule-based skill extraction. This is intentionally simple and explainable.
>
> Instead of using ML too early, I use a dictionary/rule approach so the results are transparent and easy to validate.

Explain Candidate Fit Score v1:

> Candidate Fit Score v1 compares live job postings against a fixed Candidate Profile v1 for a junior / career-switching Data Engineer.
>
> The score is deterministic and rule-based. It is not a machine learning recommender and it is not a guarantee that the candidate should apply. It is a first-pass prioritization signal.

Mention practical outputs:

```text
candidate_fit_score
candidate_fit_band
application_priority
matched_candidate_skills
missing_growth_skills
candidate_fit_reason
```

Mention output mart:

```text
marts.mart_relevant_jobs
```

Key talking point:

> Candidate Fit Score is calculated in dbt marts. Streamlit only displays the score, priority, matched skills, missing growth skills, and explanation.

---

## 8. Streamlit Dashboard

Run or show:

```bash
streamlit run streamlit_app/app.py
```

> The dashboard has pages for overview, relevant jobs, skill radar, locations, companies, weekly report, and data freshness.
>
> On the Relevant Jobs page, the main table is intentionally focused on high-signal fields like application priority, Candidate Fit Score, fit band, job title, company, location, contract, work mode, seniority, and the source link. Detailed explanations, matched skills, missing growth skills, reason codes, flags, and component scores are available in a details section.
>
> The important architecture decision is that Streamlit reads from marts only. It does not calculate Candidate Fit Score, relevance, skill demand, or weekly summaries directly.

---

## 9. Data Quality

> I added validation because Airflow success only means tasks completed. It does not prove the data is correct.

Mention examples:

- latest batch exists
- raw payloads are not null
- source job keys are present
- current model has one row per canonical job key
- relevance score is between 0 and 100
- marts are not empty after a successful run

Command:

```bash
python -m src.pipeline.run_data_quality_checks
```

---

## 10. Orchestration

> Airflow orchestrates the full MVP flow: ingestion, dbt build, validation checks, and a weekly report placeholder.

DAG flow:

```text
start
  -> ingest_france_travail_raw_jobs
  -> dbt_build
  -> run_data_quality_checks
  -> generate_weekly_report placeholder
  -> end
```

> The DAG is intentionally simple and does not contain transformation SQL.

---

## 11. Trade-Offs

> I used PostgreSQL instead of a cloud warehouse to keep the MVP reproducible locally and avoid unnecessary cloud setup.
>
> I used rule-based skill extraction instead of ML because explainability matters more at MVP stage.
>
> I used a single source first because the goal was to validate the full data product flow before adding more APIs.
>
> I made Streamlit consume marts only because the dashboard should not hide business logic.

---

## 12. Limitations

> This is a local MVP, not a production platform.

Mention:

- sample-mode data may be small
- live API requires credentials
- rule-based extraction has limitations
- weekly history needs more scheduled runs
- report generation is currently a placeholder
- no LinkedIn/Indeed scraping
- no cloud deployment in MVP

---

## 13. Closing

> The main value of this project is the complete Data Engineering flow: raw preservation, lineage, dbt modeling, validation, orchestration, marts, and dashboard presentation.
>
> Future improvements would include more sources, better skill extraction, richer scoring, historical trend tracking, CI, and optional deployment.
