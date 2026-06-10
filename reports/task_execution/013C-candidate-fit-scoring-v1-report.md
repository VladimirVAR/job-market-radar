# Task 013C — Candidate Fit Scoring v1 Report

## Part A — Analytics / dbt Engineer

## 1. Task purpose

Task 013C adds candidate-specific scoring to Job Market Radar.

The previous MVP could describe the live job market and expose generic relevance signals. This Part A implementation updates the mart layer so the product can answer a more candidate-specific question:

```text
Which jobs are most relevant for this candidate, and why?
```

This implementation keeps the logic in dbt marts. Streamlit should display the fields only and must not calculate candidate scoring logic.

## 2. Scope completed in Part A

Implemented Candidate Fit Score v1 in:

```text
dbt_job_market_radar/models/marts/mart_relevant_jobs.sql
```

Updated mart documentation/tests in:

```text
dbt_job_market_radar/models/marts/mart_compatibility.yml
dbt_job_market_radar/models/marts/mart_job_postings_current.yml
dbt_job_market_radar/tests/marts/test_mart_relevant_jobs_candidate_fit_contract.sql
```

Created the Part A task/report artifacts:

```text
tasks/013C-define-and-implement-candidate-fit-scoring-v1.md
reports/task_execution/013C-candidate-fit-scoring-v1-report.md
```

No Streamlit, README, product documentation wording, or backlog updates were performed in Part A. Those belong to Part B / documentation ownership.

## 3. Existing mart logic reused

The implementation reuses existing fields from `mart_job_postings_current` through `mart_relevant_jobs`:

```text
relevance_score
relevance_bucket
relevance_reason
matched_candidate_skills
missing_growth_skills
is_junior_friendly
detected_skills
contract_type
work_mode
city
region
country
seniority_level
```

This avoids duplicating the previous relevance model and maps the existing MVP marts into the new Candidate Fit Score contract.

## 4. Candidate Profile v1 used by scoring

Current / target candidate skills are represented by the existing `matched_candidate_skills` output, produced upstream from rule-based skill matching.

Candidate Profile v1 conceptually includes:

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

Growth skills are represented by `missing_growth_skills`:

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

Note: the current upstream 011A implementation detects a subset of growth skills. Part A consumes what is available and keeps the contract ready for expanded growth skill detection later.

## 5. Scoring dimensions implemented

Candidate Fit Score v1 is implemented as a bounded, explainable rule-based score.

Implemented component fields:

```text
role_fit_score
skill_fit_score
seniority_fit_score
contract_fit_score
location_fit_score
growth_value_score
negative_signal_penalty
candidate_fit_score
```

Formula:

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

Component caps:

| Component | Max points |
|---|---:|
| `role_fit_score` | 25 |
| `skill_fit_score` | 30 |
| `seniority_fit_score` | 20 |
| `contract_fit_score` | 10 |
| `location_fit_score` | 5 |
| `growth_value_score` | 10 |
| `negative_signal_penalty` | 30 |

## 6. Role-fit logic

Added flags:

```text
is_strong_target_role
is_acceptable_adjacent_role
```

Strong target role signals include:

```text
data engineer
data engineering
ingénieur data
etl developer
développeur etl
data integration
analytics engineer
data pipeline
pipeline developer
data warehouse developer
elt / etl
data warehouse
```

Acceptable adjacent role signals include:

```text
bi developer
bi engineer
business intelligence
data analyst
analyste data
data analyst bi
sql developer
reporting engineer
analytics reporting
reporting analyst
```

Low-priority role signals are excluded from strong/adjacent classification when they do not contain data-related indicators.

## 7. Seniority risk logic

Added:

```text
is_seniority_risk
```

Positive junior-friendly signals include:

```text
junior
débutant / debutant
entry-level
0-2 years / 0 à 2 ans
première expérience / first experience
formation possible
reconversion
graduate
alternance
stage
trainee
```

Negative seniority signals include:

```text
senior
lead
principal
staff
architect / architecte
manager
expert
5+ years / 5 ans
7+ years / 7 ans
10+ years / 10 ans
```

The logic is intentionally rule-based and explainable. It is not expected to be perfect in MVP.

## 8. Growth / learning signal logic

Added:

```text
is_learning_signal
```

A job can be marked as a learning signal when it contains growth skills but is not currently a strong application target because of score, seniority risk, or role-fit limitations.

Growth skills add limited value through:

```text
growth_value_score
```

This is capped at 10 points so growth skills cannot overpower poor role fit or seniority risk.

## 9. Score band logic

Added:

```text
candidate_fit_band
```

Bands:

| Score range | Band |
|---:|---|
| 80-100 | `strong_match` |
| 65-79 | `good_match` |
| 50-64 | `possible_match` |
| 35-49 | `weak_match` |
| 0-34 | `low_priority` |

## 10. Application priority logic

Added:

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

Mapping:

```text
apply_now:
  candidate_fit_score >= 80
  and is_seniority_risk = false
  and is_strong_target_role = true

good_candidate:
  candidate_fit_score >= 65
  and not apply_now

stretch_opportunity:
  candidate_fit_score >= 50
  and useful role/skill fit exists
  and seniority risk or multiple growth-skill gaps exist

learning_signal:
  growth skills exist
  and the job is not strong enough as an application target

low_priority:
  fallback
```

## 11. Reason codes and explanation

Added:

```text
positive_reason_codes
negative_reason_codes
candidate_fit_reason
```

Example positive reason codes:

```text
target_role
acceptable_adjacent_role
candidate_skill_match
junior_friendly
remote_or_france_location
growth_skill_signal
candidate_friendly_contract
```

Example negative reason codes:

```text
seniority_risk
low_role_fit
missing_core_skills
freelance_or_expert_contract
not_target_role
```

`candidate_fit_reason` is deterministic and built in SQL with simple `case when` / `concat_ws` logic.

## 12. Field contract exposed by `marts.mart_relevant_jobs`

New required fields exposed:

```text
candidate_fit_score
candidate_fit_band
application_priority
positive_reason_codes
negative_reason_codes
candidate_fit_reason
is_strong_target_role
is_acceptable_adjacent_role
is_seniority_risk
is_stretch_opportunity
is_learning_signal
```

New optional transparency fields exposed:

```text
role_fit_score
skill_fit_score
seniority_fit_score
contract_fit_score
location_fit_score
growth_value_score
negative_signal_penalty
```

Existing fields preserved:

```text
relevance_score
relevance_bucket
relevance_reason
matched_candidate_skills
missing_growth_skills
is_junior_friendly
```

## 13. Tests added

Updated YAML tests:

```text
candidate_fit_score not_null
candidate_fit_band not_null + accepted_values
application_priority not_null + accepted_values
candidate_fit_reason not_null
candidate fit boolean flags not_null
component score fields not_null
```

Added custom sanity test:

```text
dbt_job_market_radar/tests/marts/test_mart_relevant_jobs_candidate_fit_contract.sql
```

This checks:

```text
candidate_fit_score between 0 and 100
component score bounds
candidate_fit_band accepted values
application_priority accepted values
candidate_fit_reason not null / not empty
```

## 14. Files changed

Modified in Part A:

```text
dbt_job_market_radar/models/marts/mart_relevant_jobs.sql
dbt_job_market_radar/models/marts/mart_compatibility.yml
dbt_job_market_radar/models/marts/mart_job_postings_current.yml
```

Created in Part A:

```text
dbt_job_market_radar/tests/marts/test_mart_relevant_jobs_candidate_fit_contract.sql
reports/task_execution/013C-candidate-fit-scoring-v1-report.md
tasks/013C-define-and-implement-candidate-fit-scoring-v1.md
```

Note: `mart_job_postings_current.yml` was also updated to align generic `accepted_values` tests with the dbt 1.11 `arguments:` format and keep the full dbt build clean.

## 15. Validation commands

The following commands were run locally from the repository root:

```bash
dbt parse --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar --no-partial-parse
```

Targeted Candidate Fit / marts build:

```bash
dbt build --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar --select mart_relevant_jobs+
```

Full dbt build:

```bash
dbt build --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar
```

## 16. Validation status

Local validation completed successfully.

Parse result:

```text
dbt parse --no-partial-parse completed successfully.
```

Targeted build result:

```text
dbt build --select mart_relevant_jobs+
Completed successfully
PASS=37 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=37
```

Full build result:

```text
dbt build
Completed successfully
PASS=163 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=163
```

Candidate Fit Score v1 is now validated at the dbt layer. The full dbt build confirms that the new scoring logic, mart documentation/tests, and custom Candidate Fit contract test do not break the existing raw, staging, warehouse, and marts pipeline.

Temporary YAML parsing/deprecation issues encountered during validation were resolved by moving `accepted_values` test values under the dbt 1.11-compatible `arguments:` property.

## 17. Known limitations

1. The score is rule-based and deterministic, not ML-based.
2. It depends on text quality from France Travail postings.
3. It currently consumes detected skill arrays from upstream marts; if upstream skill extraction misses growth skills, Candidate Fit Score cannot recover them.
4. French/English seniority wording coverage is useful but incomplete.
5. The score should be treated as first-pass prioritization, not as a final decision about applying.
6. Growth skills intentionally add limited points and should not make a poor role look like a strong target.
7. Part A does not update Streamlit, README, product docs, or backlog.

## 18. Recommended next step

Part A is complete and ready for handoff.

Recommended handoff to Part B:

```text
Streamlit Engineer + Data Quality Engineer + Documentation Engineer
```

Part B should:

```text
1. Display candidate_fit_score, candidate_fit_band, application_priority and candidate_fit_reason in Relevant Jobs.
2. Add Streamlit filters for application_priority and candidate_fit_band.
3. Ensure data quality checks cover score bounds and accepted labels.
4. Document Candidate Profile v1 and Candidate Fit Score v1 honestly.
5. Keep Candidate Fit Score calculation out of Streamlit.
```

Final Part A status:

```text
Candidate-specific scoring in dbt marts: complete
Targeted dbt build: passed
Full dbt build: passed
Ready for Part B: yes
```
