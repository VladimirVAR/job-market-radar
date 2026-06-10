# Scoring Contract

## Purpose

This document defines the technical contract for Candidate Fit Score v1.

The goal is to keep scoring logic explicit, testable, and separated from the Streamlit UI.

## Source mart

Candidate Fit Score v1 is exposed through:

```text
marts.mart_relevant_jobs
```

## Calculation ownership

Scoring is calculated in:

```text
dbt marts
```

Specifically, the Candidate Fit fields are prepared upstream before Streamlit reads them.

## Display ownership

Scoring is displayed in:

```text
streamlit_app/pages/2_relevant_jobs.py
```

Streamlit may:

- read Candidate Fit fields from `marts.mart_relevant_jobs`;
- filter by `application_priority`;
- filter by `candidate_fit_band`;
- sort by `candidate_fit_score`;
- display `candidate_fit_reason`;
- format arrays/lists for readability.

Streamlit must not:

- calculate `candidate_fit_score`;
- calculate `application_priority`;
- calculate `candidate_fit_band`;
- duplicate dbt scoring logic;
- query `raw`, `staging`, or `warehouse` tables for business logic.

## Marts-only dashboard rule

Business dashboard pages must read only from:

```text
marts.*
```

Allowed example:

```sql
select * from marts.mart_relevant_jobs;
```

Not allowed:

```sql
select * from raw.raw_france_travail_job_postings;
```

Not allowed:

```text
Streamlit reads raw JSON and calculates candidate fit.
```

## Required output fields

`marts.mart_relevant_jobs` must expose:

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

Recommended transparency fields:

```text
role_fit_score
skill_fit_score
seniority_fit_score
contract_fit_score
location_fit_score
growth_value_score
negative_signal_penalty
```

Backward-compatible fields preserved from earlier relevance logic:

```text
relevance_score
relevance_bucket
relevance_reason
is_junior_friendly
```

## Score range

`candidate_fit_score` must be:

```text
0 <= candidate_fit_score <= 100
```

The field must be not null for rows in `marts.mart_relevant_jobs`.

## Accepted candidate_fit_band values

```text
strong_match
good_match
possible_match
weak_match
low_priority
```

## Accepted application_priority values

```text
apply_now
good_candidate
stretch_opportunity
learning_signal
low_priority
```

## Reason code fields

Positive reason codes are stored in:

```text
positive_reason_codes
```

Negative reason codes are stored in:

```text
negative_reason_codes
```

The human-readable explanation is stored in:

```text
candidate_fit_reason
```

`candidate_fit_reason` must be not null and not empty.

## Data quality expectations

Validation should cover:

```text
candidate_fit_score is not null
candidate_fit_score between 0 and 100
candidate_fit_band is not null
candidate_fit_band uses accepted values
application_priority is not null
application_priority uses accepted values
candidate_fit_reason is not null and not empty
candidate fit boolean flags are not null
component scores are within expected bounds
```

These checks should live in dbt YAML tests and/or custom dbt SQL tests. They should not be implemented in Streamlit.

## Contract limitation

Candidate Fit Score v1 is deterministic and rule-based. It is not a machine learning recommender and should not be presented as one.
