# Task 011B — Create Streamlit Dashboard

## Role

Streamlit Dashboard Engineer.

## Goal

Create a simple, demo-friendly dashboard that consumes prepared marts.

## Current Context

Task 011A created analytics marts. Streamlit should now present and explore data, not transform it.

## Required Work

Create pages for home, overview, relevant jobs, skill radar, locations, companies, weekly report, and data freshness.

Business pages must read from:

```text
marts.*
```

Business pages must not query:

```text
raw.*
staging.*
warehouse.*
```

## Constraints

- Do not calculate relevance score in Streamlit.
- Do not calculate skill demand in Streamlit.
- Do not duplicate dbt logic in UI code.
- Use environment variables for DB connection.
- Do not commit secrets.
- Keep UI simple and technically clear.

## Deliverables

```text
streamlit_app/
docs/README_STREAMLIT_DASHBOARD.md
reports/task_execution/011B-create-streamlit-dashboard-report.md
```

## Definition of Done

Task 011B is complete when Streamlit runs, all pages render, business pages consume `marts.*` only, guardrails exist, and a task report exists.
