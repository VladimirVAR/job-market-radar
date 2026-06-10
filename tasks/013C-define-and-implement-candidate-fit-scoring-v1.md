# Task 013C Assignment — Define and Implement Candidate Fit Scoring v1

## Role Ownership

Primary owner:

```text
Data Architect / Tech Lead
```

Implementation owners:

```text
Part A — Analytics / dbt Engineer
Part B — Streamlit Engineer + Data Quality Engineer + Documentation Engineer
```

This task may be executed by multiple roles, but it must be treated as one coordinated product correction before final public release polish.

---

## Task Name

```text
Task 013C — Define and Implement Candidate Fit Scoring v1
```

---

## Why This Task Exists

The project has already completed:

```text
Technical MVP foundation
Live France Travail API validation
Clean reproducible live baseline
Airflow live validation
```

The current system can ingest real France Travail job postings, transform them through dbt, validate them, orchestrate the pipeline with Airflow, and display results in Streamlit.

However, the current relevance score still feels too generic.

The product direction is now shifting from:

```text
generic job market analytics
```

to:

```text
candidate-specific job market radar
```

The goal is not to build a complex recommendation system.

The goal is to make the existing MVP more useful for a real junior / career-switching Data Engineer candidate while preserving the current architecture.

---

## Current Project Status

Completed tasks:

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
```

Current validated flow:

```text
live France Travail API
  -> raw PostgreSQL tables
  -> dbt staging
  -> dbt warehouse
  -> dbt marts
  -> data quality checks
  -> Airflow orchestration
  -> Streamlit dashboard
```

Current product status:

```text
Technical foundation: complete
Live-data validation: complete
Clean reproducible baseline: complete
Final public release polish: pending
Candidate-specific scoring: pending
```

---

## Core Architectural Principle

Candidate Fit Score logic must live in the data/modeling layer.

Allowed:

```text
dbt marts calculate candidate fit fields
Streamlit displays and filters candidate fit fields
Data quality validates candidate fit fields
Docs explain candidate fit logic
```

Not allowed:

```text
Streamlit calculates candidate_fit_score
Streamlit contains hidden business scoring logic
new data sources
machine learning recommender
embeddings
profile editor UI
multi-user profile support
major mart redesign
```

---

# Candidate Fit Scoring Contract v1

## Candidate Profile v1

Candidate Profile v1 represents a career-switching junior Data Engineer candidate in France / Europe.

### Current / Target Skills

The candidate profile should include:

```text
Python
SQL
PostgreSQL
Docker
dbt
Airflow
AWS basics
Data Engineering fundamentals
Data warehouse / ELT concepts
Data quality
```

### Growth Skills

Growth skills should be tracked as learning signals, but should not automatically make a job a strong application target.

```text
Spark
Kafka
Snowflake
BigQuery
Azure
GCP
Terraform
Kubernetes
CI/CD
```

---

## Target Role Logic

### Strong Target Roles

Examples:

```text
Data Engineer
Junior Data Engineer
ETL Developer
Data Integration Developer
Analytics Engineer
Data Pipeline Developer
Data Warehouse Developer
Ingénieur Data
Développeur ETL
```

### Acceptable Adjacent Roles

Examples:

```text
BI Developer
Data Analyst with SQL/Python/dbt
SQL Developer with data warehouse responsibilities
Analytics / Reporting Engineer
BI Engineer
Data Analyst BI
```

### Low-Priority / Excluded Role Signals

Examples:

```text
pure backend developer
pure frontend developer
generic software engineer
senior architect
principal engineer
team lead
engineering manager
non-data-heavy developer role
```

The goal is not to delete these jobs from the data. The goal is to rank them lower or mark them as low priority.

---

## Scoring Dimensions

Candidate Fit Score v1 should be rule-based and explainable.

Recommended dimensions:

```text
role_fit
skill_fit
seniority_fit
contract_fit
location_fit
growth_value
negative_signals
```

Recommended score structure:

```text
role_fit: up to 25 points
skill_fit: up to 30 points
seniority_fit: up to 20 points
contract_fit: up to 10 points
location_fit: up to 5 points
growth_value: up to 10 points
negative_signals: penalty up to -30 points
```

Final score:

```text
candidate_fit_score = greatest(0, least(100, positive_points - negative_penalty))
```

The exact SQL implementation may adjust the internal point distribution slightly if needed, but the score must remain explainable and bounded between 0 and 100.

---

## Score Bands

Use these bands consistently:

```text
80-100: strong_match
65-79: good_match
50-64: possible_match
35-49: weak_match
0-34: low_priority
```

---

## Application Priority Labels

Use these practical labels:

```text
apply_now
good_candidate
stretch_opportunity
learning_signal
low_priority
```

### apply_now

Strong fit across role, skills, seniority, and practical constraints.

### good_candidate

Good fit, but may need manual review or has some missing skills.

### stretch_opportunity

Potentially worth applying despite seniority or skill gaps.

### learning_signal

Not an ideal application target now, but useful for identifying market-demanded growth skills.

### low_priority

Unlikely to be worth attention now.

---

## Required Output Fields

Preferred target mart:

```text
marts.mart_relevant_jobs
```

Required fields:

```text
candidate_fit_score
candidate_fit_band
application_priority
matched_candidate_skills
missing_growth_skills
positive_reason_codes
negative_reason_codes
candidate_fit_reason
is_strong_target_role
is_acceptable_adjacent_role
is_seniority_risk
is_stretch_opportunity
is_learning_signal
```

Recommended optional component fields for transparency:

```text
role_fit_score
skill_fit_score
seniority_fit_score
contract_fit_score
location_fit_score
growth_value_score
negative_signal_penalty
```

If existing fields already provide similar values, do not duplicate unnecessarily. Map existing fields into the new naming contract where practical.

---

## Candidate Fit Reason

Each scored job should expose a short human-readable explanation.

Examples:

```text
Strong match because the job mentions Python, SQL, Airflow and data pipelines, has acceptable seniority, and is located in France.
```

```text
Learning signal because the role is senior-level and requires Spark/Kafka/Kubernetes, but it highlights recurring growth skills in the target market.
```

The explanation does not need to be perfect. It must be clear, deterministic, and demo-friendly.

---

# Part A — Analytics / dbt Engineer Assignment

## Role

You are the **Analytics / dbt Engineer** for Task 013C.

Your responsibility is to implement Candidate Fit Score v1 in dbt marts.

You are not responsible for Streamlit UI polish or final documentation wording, but you must expose a clean data contract for those downstream roles.

---

## Part A Goal

Update the mart layer so candidate-specific fit fields are available for dashboard consumption.

Primary target model:

```text
dbt_job_market_radar/models/marts/mart_relevant_jobs.sql
```

Secondary model if needed:

```text
dbt_job_market_radar/models/marts/mart_job_postings_current.sql
```

Do not move scoring into Streamlit.

---

## Part A Required Work

### 1. Inspect Existing Mart Logic

Review current models:

```text
dbt_job_market_radar/models/marts/mart_relevant_jobs.sql
dbt_job_market_radar/models/marts/mart_job_postings_current.sql
dbt_job_market_radar/models/marts/mart_skill_demand.sql
dbt_job_market_radar/models/marts/mart_missing_skills.sql
```

Identify existing relevance fields such as:

```text
relevance_score
relevance_bucket
matched_candidate_skills
missing_growth_skills
is_junior_friendly
relevance_reason
```

Reuse existing logic where possible.

Do not duplicate fields unnecessarily.

---

### 2. Implement Candidate Fit Components

Add candidate-specific component logic.

Recommended components:

```text
role_fit_score
skill_fit_score
seniority_fit_score
contract_fit_score
location_fit_score
growth_value_score
negative_signal_penalty
```

The implementation should use SQL-friendly rule-based matching against available fields such as:

```text
job_title
normalized_job_title
description_text
contract_type
work_mode
city
region
country
seniority_level
```

Use lowercase normalized text fields where practical.

---

### 3. Implement Target Role Flags

Add flags:

```text
is_strong_target_role
is_acceptable_adjacent_role
```

Recommended logic:

* strong target role if title/description contains data engineering / ETL / analytics engineering / warehouse / pipeline indicators;
* acceptable adjacent role if title/description contains BI / data analyst / SQL developer / reporting engineer indicators;
* low-priority technical roles should not be marked as strong target roles.

---

### 4. Implement Seniority Risk Logic

Add:

```text
is_seniority_risk
```

Positive junior-friendly terms may include:

```text
junior
débutant
debutant
0-2 years
0 à 2 ans
première expérience
first experience
formation possible
reconversion
```

Negative seniority terms may include:

```text
senior
lead
principal
architect
architecte
manager
expert
5+ years
5 ans
7 ans
10 ans
```

This does not need to be perfect. It must be explainable and documented.

---

### 5. Implement Growth / Learning Signal Logic

Add:

```text
is_learning_signal
```

A job may be a learning signal when:

* it contains useful growth skills;
* it is not an ideal application target;
* it exposes market-demanded skills worth tracking.

Growth skills:

```text
spark
kafka
snowflake
bigquery
azure
gcp
terraform
kubernetes
ci/cd
```

Growth skills should add limited points. They should not overpower poor role fit or major seniority risk.

---

### 6. Implement Final Candidate Fit Score

Add:

```text
candidate_fit_score
```

Score must be:

```text
integer or numeric
between 0 and 100
```

Recommended formula:

```text
candidate_fit_score =
  greatest(
    0,
    least(
      100,
      role_fit_score
      + skill_fit_score
      + seniority_fit_score
      + contract_fit_score
      + location_fit_score
      + growth_value_score
      - negative_signal_penalty
    )
  )
```

---

### 7. Implement Score Band

Add:

```text
candidate_fit_band
```

Bands:

```text
80-100: strong_match
65-79: good_match
50-64: possible_match
35-49: weak_match
0-34: low_priority
```

---

### 8. Implement Application Priority

Add:

```text
application_priority
```

Labels:

```text
apply_now
good_candidate
stretch_opportunity
learning_signal
low_priority
```

Recommended mapping:

```text
apply_now:
  candidate_fit_score >= 80
  and is_seniority_risk = false
  and is_strong_target_role = true

good_candidate:
  candidate_fit_score >= 65
  and application is not apply_now

stretch_opportunity:
  candidate_fit_score >= 50
  and candidate has useful skill/role fit
  and either seniority risk or notable missing growth skills exist

learning_signal:
  useful growth skills exist
  but candidate_fit_score is not strong enough for application priority

low_priority:
  default fallback
```

---

### 9. Implement Reason Codes and Explanation

Add:

```text
positive_reason_codes
negative_reason_codes
candidate_fit_reason
```

Reason codes can be strings or arrays depending on the current project style.

Examples:

```text
target_role
candidate_skill_match
junior_friendly
remote_or_france_location
growth_skill_signal
seniority_risk
low_role_fit
missing_core_skills
```

`candidate_fit_reason` should be short and human-readable.

It may be constructed with `case when` logic.

---

### 10. Update Mart YAML Documentation

Update relevant YAML file, likely:

```text
dbt_job_market_radar/models/marts/mart_compatibility.yml
```

or the YAML file documenting `mart_relevant_jobs`.

Document all new fields.

Add tests where appropriate:

```text
not_null candidate_fit_score
not_null candidate_fit_band
not_null application_priority
accepted_values candidate_fit_band
accepted_values application_priority
```

---

### 11. Add Lightweight Custom Tests if Needed

Suggested custom tests:

```text
candidate_fit_score between 0 and 100
candidate_fit_reason is not null for active relevant jobs
application_priority has accepted values
candidate_fit_band has accepted values
```

Do not overbuild.

Prefer simple dbt generic tests where possible.

---

## Part A Validation Commands

Run:

```bash
dbt parse --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar
```

Run targeted build:

```bash
dbt build --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar --select mart_relevant_jobs+
```

Run full build:

```bash
dbt build --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar
```

Expected:

```text
Completed successfully
```

---

## Part A Deliverables

Expected modified files:

```text
dbt_job_market_radar/models/marts/mart_relevant_jobs.sql
dbt_job_market_radar/models/marts/*.yml
```

Possible new or modified files:

```text
dbt_job_market_radar/tests/marts/
```

Expected report section:

```text
reports/task_execution/013C-candidate-fit-scoring-v1-report.md
```

Part A section must include:

* scoring dimensions implemented;
* field contract;
* score band logic;
* application priority logic;
* files changed;
* validation commands run;
* known limitations.

---

# Part B — Streamlit / Data Quality / Documentation Assignment

## Role

You are the **Streamlit + Data Quality + Documentation Engineer** for Task 013C.

Your responsibility is to consume and validate the new Candidate Fit Score v1 outputs.

You must not calculate Candidate Fit Score in Streamlit.

---

## Part B Goal

Update presentation, validation, and documentation so Candidate Fit Score v1 is visible, understandable, and safely checked.

---

## Part B Required Work

### 1. Streamlit Update

Update existing Relevant Jobs page:

```text
streamlit_app/pages/2_relevant_jobs.py
```

Show the following fields if present:

```text
candidate_fit_score
candidate_fit_band
application_priority
matched_candidate_skills
missing_growth_skills
candidate_fit_reason
is_seniority_risk
is_stretch_opportunity
is_learning_signal
```

Do not add a new dashboard page unless absolutely necessary.

Recommended UI behavior:

* sort by `candidate_fit_score` descending by default;
* add filter for `application_priority`;
* add filter for `candidate_fit_band`;
* display `candidate_fit_reason` in the table;
* keep existing source URL / job title / company / location fields.

If candidate fit fields are not available, the page should degrade gracefully and show existing relevance fields.

---

### 2. Streamlit Contract Constraint

Streamlit must continue to query only:

```text
marts.*
```

Do not query:

```text
raw.*
staging.*
warehouse.*
```

Do not calculate candidate score in Python.

Only display fields from marts.

---

### 3. Data Quality Checks

Add or verify lightweight checks:

```text
candidate_fit_score between 0 and 100
candidate_fit_band uses accepted values
application_priority uses accepted values
candidate_fit_reason is not null for scored jobs
```

If these are already handled in dbt YAML/custom tests from Part A, do not duplicate unnecessarily.

Ensure:

```bash
python -m src.pipeline.run_data_quality_checks
```

still passes.

---

### 4. Documentation Updates

Create or update:

```text
docs/product/candidate_profile_v1.md
docs/product/relevance_scoring_v1.md
docs/architecture/scoring_contract.md
docs/limitations_and_future_work.md
README.md
```

Documentation must explain:

1. What Candidate Fit Score means.
2. What it does not mean.
3. Why it is rule-based.
4. Candidate Profile v1.
5. Scoring dimensions.
6. Score bands.
7. Application priority labels.
8. Known limitations.
9. Future improvements.

Do not overclaim.

Recommended wording:

```text
Candidate Fit Score is a transparent first-pass signal for a career-switching junior Data Engineer candidate. It is rule-based and explainable. It is not a machine learning recommendation model.
```

---

### 5. Report Update

Create or update:

```text
reports/task_execution/013C-candidate-fit-scoring-v1-report.md
```

Part B section must include:

* Streamlit files updated;
* fields displayed;
* validation checks added or confirmed;
* docs created/updated;
* commands run;
* known limitations.

---

## Part B Validation Commands

Run:

```bash
python -m py_compile streamlit_app/app.py streamlit_app/db.py streamlit_app/pages/2_relevant_jobs.py
```

Run Streamlit:

```bash
streamlit run streamlit_app/app.py
```

Validate pages:

```text
Overview
Relevant Jobs
Skill Radar
Data Freshness
```

Run Data Quality:

```bash
python -m src.pipeline.run_data_quality_checks
```

Optional final full dbt check:

```bash
dbt build --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar
```

---

## Task 013C Report

Create:

```text
reports/task_execution/013C-candidate-fit-scoring-v1-report.md
```

The report must include:

1. Task purpose.
2. Roles involved.
3. Candidate Profile v1 summary.
4. Scoring contract summary.
5. New mart fields.
6. Streamlit changes.
7. Data quality changes.
8. Documentation changes.
9. Validation commands run.
10. Before/after product value.
11. Known limitations.
12. Final acceptance status.
13. Recommended next task.

---

## Expected Files Created / Modified

Expected new file:

```text
tasks/013C-define-and-implement-candidate-fit-scoring-v1.md
```

Expected new docs:

```text
docs/product/candidate_profile_v1.md
docs/product/relevance_scoring_v1.md
docs/architecture/scoring_contract.md
```

Expected new report:

```text
reports/task_execution/013C-candidate-fit-scoring-v1-report.md
```

Expected modified files:

```text
tasks/backlog.md
README.md
docs/limitations_and_future_work.md
dbt_job_market_radar/models/marts/mart_relevant_jobs.sql
dbt_job_market_radar/models/marts/*.yml
streamlit_app/pages/2_relevant_jobs.py
```

Possible modified files:

```text
dbt_job_market_radar/tests/marts/
```

No `.env` file should be committed.

No secrets should be committed.

No new source should be added.

---

## Backlog Update Requirement

Update:

```text
tasks/backlog.md
```

Current sequence should become:

```text
001 -> 002 -> 003 -> 004 -> 005 -> 006 -> 007 -> 008 -> 009 -> 010 -> 011A -> 011B -> 012 -> 013 -> 013B -> 013C -> 014
```

Add Task 013C between clean live baseline and final polish.

Task 013C status after completion:

```text
Candidate-specific scoring: complete
Final public release polish: pending
```

---

## Acceptance Criteria

Task 013C is accepted when:

1. Candidate Profile v1 is defined.
2. Candidate Fit Score v1 is documented.
3. Scoring dimensions are implemented or clearly mapped to existing mart logic.
4. Score bands are implemented.
5. Application priority labels are implemented.
6. `marts.mart_relevant_jobs` exposes candidate-specific scoring outputs.
7. Streamlit displays candidate fit fields without calculating them.
8. Data Quality validates score range and accepted labels.
9. README/demo wording explains the score honestly.
10. Existing live-data pipeline still works.
11. Existing marts-only dashboard contract is preserved.
12. No new source or major architecture change is introduced.
13. Task report exists.

---

## Definition of Done

Task 013C is complete when Job Market Radar can answer not only:

```text
What does the live job market look like?
```

but also:

```text
Which jobs are most relevant for this candidate, and why?
```

After this task, proceed to:

```text
Task 014 — Final Polish / Public Release Readiness
```
