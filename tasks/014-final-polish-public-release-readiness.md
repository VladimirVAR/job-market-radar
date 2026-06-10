# Task 014 Assignment — Final Polish / Public Release Readiness

## Role

You are the **Release Engineer** for the **Job Market Radar** project.

Your task is to complete:

```text
Task 014 — Final Polish / Public Release Readiness
```

This is the final MVP packaging task.

The goal is not to add major new functionality. The goal is to make the existing live-data MVP clean, understandable, credible, and ready for GitHub / public release / technical review.

---

## Current Project Status

The project has completed:

```text
001 — Create repository structure
002 — Create Docker Compose environment
003 — Create raw schema
004 — Build France Travail API client
005 — Load raw job postings
006 — Create dbt project
007 — Build staging models
008 — Build warehouse snapshots/current models
009 — Build validation checks
010 — Create Airflow DAG
011A — Build analytics marts
011B — Create Streamlit dashboard
012 — Write demo documentation
013 — Activate live France Travail API ingestion
013B — Project plan reconciliation and clean live baseline
013C — Candidate Fit Scoring v1
```

Current validated capabilities:

```text
live France Travail API ingestion
raw PostgreSQL storage
dbt staging / warehouse / marts
data quality checks
Airflow orchestration
Streamlit dashboard
Candidate Fit Score v1
clean live baseline
documentation package
```

Current project state:

```text
Technical MVP foundation: complete
Live-data validation: complete
Clean reproducible baseline: complete
Candidate-specific scoring: complete
Final public release polish: pending
```

---

## Important Prerequisite

Task 013C should be committed before starting Task 014.

Expected commit message:

```text
Complete Task 013C candidate fit scoring v1
```

Before starting Task 014, run:

```bash
git status
```

Expected:

```text
nothing to commit, working tree clean
```

Do not mix Task 013C changes with Task 014 changes.

---

## Goal

Prepare Job Market Radar as a clean public-release-ready MVP.

The final project should clearly demonstrate:

```text
A local Data Engineering MVP that ingests live France Travail job postings,
models them through dbt, validates data quality, orchestrates the workflow with Airflow,
and exposes candidate-specific job insights in Streamlit.
```

The final demo should answer:

```text
What does the live Data Engineering job market look like?
Which jobs are most relevant for this candidate?
Why are they relevant?
Can the pipeline be trusted?
Can the project be reproduced locally?
```

---

## Scope

### In Scope

Task 014 includes:

```text
warning cleanup
small UI readability polish
final screenshots
README polish
demo documentation polish
final validation commands
Git hygiene
public-release-readiness report
```

### Out of Scope

Do not add:

```text
new data sources
new dashboard pages unless absolutely necessary
machine learning
embeddings
profile editor UI
multi-user support
cloud deployment
major dbt redesign
major scoring changes
new ingestion source
new product feature
```

If a serious issue is discovered, fix only what is necessary to preserve the existing MVP.

---

# Workstream 1 — Warning Cleanup

## Goal

Run the project checks and remove non-blocking warnings where it is safe and low-risk.

Known warning categories to check:

```text
dbt unused configuration paths
dbt generic test deprecation warnings
Streamlit deprecation warnings
Python syntax/runtime warnings
```

Previously observed examples:

```text
unused dbt configuration path: seeds.job_market_radar
Streamlit use_container_width deprecation warning
```

Candidate Fit work may already have resolved some dbt warnings. Do not assume. Re-run checks.

---

## Required Commands

Run:

```bash
dbt build --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar
```

Run:

```bash
python -m src.pipeline.run_data_quality_checks
```

Run:

```bash
python -m py_compile streamlit_app/app.py streamlit_app/db.py streamlit_app/pages/*.py
```

Run Streamlit:

```bash
streamlit run streamlit_app/app.py
```

Record all warnings.

Fix warnings only if:

```text
the fix is simple
the fix is low-risk
the fix does not change core product behavior
the fix improves public release quality
```

Do not chase cosmetic warnings if they require risky rewrites.

---

# Workstream 2 — Streamlit UI Readability Polish

## Goal

Improve dashboard readability without changing core business logic.

Main known issue:

```text
Relevant Jobs table is wide after Candidate Fit fields were added.
```

## Required Updates

Target page:

```text
streamlit_app/pages/2_relevant_jobs.py
```

Recommended improvement:

Keep the main table focused on high-signal columns:

```text
application_priority
candidate_fit_score
candidate_fit_band
job_title
company_name
city
contract_type
work_mode
seniority_level
source_url
```

Move long/detail fields into an expander or detail section if practical:

```text
candidate_fit_reason
matched_candidate_skills
missing_growth_skills
positive_reason_codes
negative_reason_codes
candidate fit flags
component score fields
```

The goal is to make the page more readable for a technical reviewer.

Do not calculate scoring in Streamlit.

Streamlit must continue to consume only:

```text
marts.*
```

---

## Optional UI Polish

If low-risk, improve:

```text
column ordering
label names
metric captions
filter labels
empty-state messages
```

Do not add major UI redesign.

---

# Workstream 3 — Final Screenshots

## Goal

Capture final screenshots for GitHub/demo documentation.

Create or update:

```text
docs/screenshots/
```

Recommended screenshots:

```text
docs/screenshots/airflow_dag_success.png
docs/screenshots/streamlit_overview.png
docs/screenshots/streamlit_relevant_jobs_candidate_fit.png
docs/screenshots/streamlit_skill_radar.png
docs/screenshots/streamlit_locations.png
docs/screenshots/streamlit_companies.png
docs/screenshots/streamlit_weekly_report.png
docs/screenshots/streamlit_data_freshness.png
```

Screenshots should show live-data MVP output, not sample-mode data.

Do not include secrets, API keys, local `.env`, or private credentials in screenshots.

---

# Workstream 4 — README Polish

## Goal

Make the root README clear, public-project-friendly, and honest.

Update:

```text
README.md
```

README should explain:

```text
what the product does
who it is for
why it exists
architecture overview
tech stack
how to run locally
how data flows through the system
how Candidate Fit Score works
what is validated
what screenshots show
known limitations
future improvements
```

README should include or reference final screenshots.

Do not overclaim.

Recommended framing:

```text
Candidate Fit Score is a transparent, rule-based first-pass signal.
It is not a machine learning recommendation model.
```

---

# Workstream 5 — Demo Documentation Polish

Review and update existing docs where needed:

```text
docs/demo_guide.md
docs/demo_script.md
docs/data_catalog.md
docs/data_flow.md
docs/architecture.md
docs/validation_summary.md
docs/local_runbook.md
docs/product/candidate_profile_v1.md
docs/product/relevance_scoring_v1.md
docs/architecture/scoring_contract.md
docs/limitations_and_future_work.md
```

Do not rewrite everything.

Focus on consistency:

```text
task sequence includes 013C and 014
Candidate Fit Score wording is consistent
live-data MVP status is clear
limitations are honest
screenshots are referenced correctly
demo flow matches current UI
```

---

# Workstream 6 — Final Live Pipeline Validation

## Goal

Prove final public release version still works after polish.

Run the full local validation flow.

## Required Validation Commands

From repository root:

```bash
dbt build --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar
```

```bash
python -m src.pipeline.run_data_quality_checks
```

```bash
python -m py_compile streamlit_app/app.py streamlit_app/db.py streamlit_app/pages/*.py
```

```bash
streamlit run streamlit_app/app.py
```

Open and validate:

```text
App / Home
Overview
Relevant Jobs
Skill Radar
Locations
Companies
Weekly Report
Data Freshness
```

## Recommended Airflow Validation

If Airflow is running and credentials are configured inside containers, trigger one final DAG run:

```bash
docker compose exec airflow-webserver airflow dags trigger job_market_radar --run-id task_014_final_validation
```

Then check task states:

```bash
docker compose exec airflow-webserver airflow tasks states-for-dag-run job_market_radar task_014_final_validation
```

Expected final state:

```text
start: success
ingest_france_travail_raw_jobs: success
dbt_build: success
run_data_quality_checks: success
generate_weekly_report: success
end: success
```

If Airflow final validation is skipped, document why.

---

# Workstream 7 — Security and Git Hygiene

## Goal

Ensure the project is safe to publish.

Check:

```text
.env is not committed
API secrets are not committed
dbt target/ is not committed
logs are not committed
cache files are not committed
Docker volumes are not committed
screenshots do not expose secrets
```

Run:

```bash
git status
```

Optional checks:

```bash
git status --ignored
```

Search for accidental secrets before final commit:

```bash
findstr /S /I "FRANCE_TRAVAIL_CLIENT_SECRET FRANCE_TRAVAIL_CLIENT_ID" README.md docs\*.md docs\*.txt tasks\*.md reports\*.md
```

Do not remove safe placeholder references from `.env.example`. Only real secret leakage is a problem.

---

# Workstream 8 — Task Report

Create:

```text
reports/task_execution/014-final-polish-public-release-readiness-report.md
```

The report must include:

```text
task purpose
files changed
warnings found
warnings fixed
warnings intentionally left
Streamlit UI polish summary
screenshots captured
README/docs updates
validation commands run
dbt result
data quality result
Streamlit result
Airflow result if run
security/Git hygiene check
known remaining limitations
final acceptance status
recommended next steps
```

---

# Expected Files Created / Modified

Expected new file:

```text
reports/task_execution/014-final-polish-public-release-readiness-report.md
```

Expected new or updated screenshots:

```text
docs/screenshots/*.png
```

Expected modified files:

```text
README.md
docs/demo_guide.md
docs/demo_script.md
docs/limitations_and_future_work.md
streamlit_app/pages/2_relevant_jobs.py
```

Possible modified files:

```text
streamlit_app/pages/*.py
streamlit_app/db.py
dbt_job_market_radar/dbt_project.yml
dbt_job_market_radar/models/**/*.yml
docs/**/*.md
tasks/backlog.md
```

Do not commit:

```text
.env
dbt_job_market_radar/target/
logs/
cache files
Docker volumes
credentials
```

---

# Acceptance Criteria

Task 014 is accepted when:

```text
dbt build passes
data quality runner passes
Python compile passes
Streamlit renders all key pages
Relevant Jobs page is more readable
Candidate Fit Score is clearly visible
Candidate Fit details are understandable
known safe warnings are cleaned where practical
remaining warnings are documented if any
README is public-release-ready
demo docs are consistent with current MVP
screenshots exist and show live-data MVP
no secrets are committed
final report exists
Git status contains only intended changes before commit
```

---

# Definition of Done

Task 014 is complete when the project is ready to be shown as a release-grade local Data Engineering MVP.

The final project should be understandable to:

```text
technical reviewer
data engineering reviewer
GitHub reviewer
technical reviewer
```

Final project statement:

```text
Job Market Radar is a local live-data Data Engineering MVP that ingests real France Travail job postings, models them through dbt, validates data quality, orchestrates the pipeline with Airflow, and displays candidate-specific job insights in Streamlit.
```

---

# Recommended Commit Message

After validation and review:

```bash
git add ...
git commit -m "Complete Task 014 final public release polish"
```
