# Task 011: Create Streamlit Dashboard

## Goal

Create a demo-friendly Streamlit dashboard that consumes prepared marts.

Streamlit must be a consumption layer only.

---

## Context

The dashboard should help a junior or career-switcher Data Engineer understand the job market.

It should not calculate core business logic directly.

---

## Deliverables

Create:

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

---

## Required Data Sources

Business pages should read from:

```text
marts.mart_relevant_jobs
marts.mart_skill_demand
marts.mart_missing_skills
marts.mart_location_activity
marts.mart_company_activity
marts.mart_weekly_market_summary
```

Technical freshness page may read from:

```text
raw.raw_load_batches
raw.raw_api_requests
```

---

## Required Pages

### Overview

Show:

- total active jobs
- new jobs this week
- average relevance score
- top skills
- top cities

### Relevant Jobs

Show:

- job title
- company
- location
- contract type
- work mode
- relevance score
- matched skills
- missing skills
- relevance reason
- source URL

### Skill Radar

Show:

- most demanded skills
- candidate-matched skills
- missing/growth skills

### Locations

Show:

- active job count by city/region
- average relevance by location

### Companies

Show:

- most active companies
- average relevance by company

### Weekly Report

Show:

- weekly market summary
- top changes
- top skills
- new opportunities

### Data Freshness

Show:

- latest batch status
- latest run timestamp
- records loaded
- API request count

---

## Acceptance Criteria

- Streamlit runs with `streamlit run streamlit_app/app.py`.
- Business pages read only from marts.
- Relevance score is not calculated in Streamlit.
- Skill demand is not calculated in Streamlit.
- Dashboard has filters and sorting.
- Dashboard is understandable for a technical project demo.
- Database connection uses environment variables.
- No secrets are committed.

---

## Implementation Notes

Keep UI simple and clear.

Prioritize demo clarity over visual complexity.

---

## Dependencies

Task 010.

---

## Next Task

Task 012: Write Demo Docs.
