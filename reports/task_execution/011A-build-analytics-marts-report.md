# Task 011A Execution Report — Build Analytics Marts for Streamlit Dashboard

## Role

Analytics / Marts Engineer

## Task Summary

Implemented the analytics marts layer for the Job Market Radar MVP.

The goal of this task was to create dashboard-ready dbt marts that future Streamlit pages can consume without querying raw, staging, or warehouse models directly for business logic.

## Files Created

### dbt mart SQL models

```text
dbt_job_market_radar/models/marts/mart_job_postings_current.sql
dbt_job_market_radar/models/marts/mart_job_market_overview.sql
dbt_job_market_radar/models/marts/mart_skill_demand.sql
dbt_job_market_radar/models/marts/mart_location_demand.sql
dbt_job_market_radar/models/marts/mart_company_demand.sql
dbt_job_market_radar/models/marts/mart_data_freshness.sql
```

### Compatibility marts for Streamlit Task 011 naming

```text
dbt_job_market_radar/models/marts/mart_relevant_jobs.sql
dbt_job_market_radar/models/marts/mart_missing_skills.sql
dbt_job_market_radar/models/marts/mart_location_activity.sql
dbt_job_market_radar/models/marts/mart_company_activity.sql
dbt_job_market_radar/models/marts/mart_weekly_market_summary.sql
```

These compatibility marts were added because the Streamlit dashboard specification expects names such as `mart_relevant_jobs`, `mart_location_activity`, `mart_company_activity`, and `mart_weekly_market_summary`, while Task 011A recommends names such as `mart_job_postings_current`, `mart_location_demand`, and `mart_company_demand`.

### dbt YAML documentation and tests

```text
dbt_job_market_radar/models/marts/mart_job_postings_current.yml
dbt_job_market_radar/models/marts/mart_job_market_overview.yml
dbt_job_market_radar/models/marts/mart_skill_demand.yml
dbt_job_market_radar/models/marts/mart_location_demand.yml
dbt_job_market_radar/models/marts/mart_company_demand.yml
dbt_job_market_radar/models/marts/mart_data_freshness.yml
dbt_job_market_radar/models/marts/mart_compatibility.yml
```

### Singular dbt tests

```text
dbt_job_market_radar/tests/marts/test_mart_job_postings_current_score_ranges.sql
dbt_job_market_radar/tests/marts/test_mart_job_market_overview_non_negative_counts.sql
dbt_job_market_radar/tests/marts/test_mart_skill_demand_sanity.sql
dbt_job_market_radar/tests/marts/test_mart_location_demand_sanity.sql
dbt_job_market_radar/tests/marts/test_mart_company_demand_sanity.sql
dbt_job_market_radar/tests/marts/test_mart_data_freshness_sanity.sql
dbt_job_market_radar/tests/marts/test_mart_missing_skills_sanity.sql
dbt_job_market_radar/tests/marts/test_mart_weekly_market_summary_sanity.sql
```

### Analytics SQL

```text
sql/analytics/analytics_queries.sql
```

### Execution report

```text
reports/task_execution/011A-build-analytics-marts-report.md
```

## Model Grains

| Model | Grain | Purpose |
|---|---|---|
| `mart_job_postings_current` | One row per current `canonical_job_key` / `source_job_key` | Dashboard-ready job listing with relevance and junior-friendly signals |
| `mart_job_market_overview` | One row for current market snapshot | Overview KPI table |
| `mart_skill_demand` | One row per MVP skill | Skill demand summary |
| `mart_location_demand` | One row per location bucket | Location distribution |
| `mart_company_demand` | One row per company bucket | Company distribution |
| `mart_data_freshness` | One row per source | Pipeline/data freshness |
| `mart_relevant_jobs` | One active current job posting | Compatibility mart for dashboard relevant jobs page |
| `mart_missing_skills` | One missing/growth skill in relevant jobs | Skill gap summary |
| `mart_location_activity` | One location bucket | Compatibility mart for dashboard locations page |
| `mart_company_activity` | One company bucket | Compatibility mart for dashboard companies page |
| `mart_weekly_market_summary` | One row for current reporting week | Lightweight weekly summary for dashboard/reporting |

## Key Metrics Exposed

### Job posting metrics

- `relevance_score`
- `relevance_bucket`
- `matched_candidate_skills`
- `missing_growth_skills`
- `detected_skill_count`
- `matched_candidate_skill_count`
- `missing_growth_skill_count`
- `is_junior_friendly`
- `relevance_reason`

### Overview metrics

- `total_current_job_postings`
- `active_job_count`
- `inactive_job_count`
- `distinct_companies`
- `distinct_locations`
- `relevant_job_count`
- `high_match_job_count`
- `junior_friendly_job_count`
- `avg_relevance_score`

### Skill metrics

- `matching_job_count`
- `total_job_count`
- `share_of_jobs`
- `last_seen_at`

### Location metrics

- `job_count`
- `share_of_jobs`
- `distinct_companies`
- `avg_relevance_score`
- `junior_friendly_job_count`

### Company metrics

- `job_count`
- `distinct_locations`
- `relevant_job_count`
- `junior_friendly_job_count`
- `avg_relevance_score`

### Freshness metrics

- `latest_successful_batch_id`
- `latest_successful_batch_started_at`
- `latest_successful_batch_finished_at`
- `latest_records_loaded`
- `latest_requests_made`
- `current_job_count`
- `snapshot_row_count`
- `freshest_data_timestamp`

## Relevance Score Logic

The MVP relevance score is implemented inside `mart_job_postings_current`.

It uses an explainable rule-based formula:

```text
relevance_score =
    skill_match_score
  + title_domain_score
  + seniority_fit_score
  + work_context_score
  + recency_score
  + data_quality_score
  - hard_penalty_score
```

The score is clamped between 0 and 100.

### Score components

| Component | Max / Role |
|---|---|
| `skill_match_score` | Up to 45 points based on detected candidate skills |
| `title_domain_score` | Up to 25 points based on Data Engineering title/domain signal |
| `seniority_fit_score` | Up to 15 points based on junior/unknown/mid/senior signal |
| `work_context_score` | Up to 5 points based on remote/hybrid/onsite signal |
| `recency_score` | Up to 10 points based on publication/seen recency |
| `data_quality_score` | Up to 10 points based on useful dashboard fields being present |
| `hard_penalty_score` | Penalty for senior/lead/expert or non-data role signals |

## Junior-Friendly Logic

`is_junior_friendly` is true when:

- explicit junior/entry-level/debutant/graduate/alternance/stage/trainee signals are found, or
- warehouse `seniority_level` is `junior`,
- and no hard seniority negative signal is present.

Hard seniority negative signals include:

```text
senior, lead, principal, staff, architect, expert, 5+ years, 7+ years, 5 ans, 7 ans
```

## Skill Demand Logic

`mart_skill_demand` uses rule-based matching over job title, normalized title, and description text.

Target MVP skills:

```text
python
sql
dbt
airflow
docker
postgresql
aws
spark
snowflake
bigquery
data warehouse
etl
elt
```

This intentionally follows the MVP decision to prioritize transparent dictionary/rule matching over NLP or ML.

## Missing Skill Priority Logic

`mart_missing_skills` treats growth skills as missing skills when they appear in relevant jobs but are not part of the MVP candidate core profile.

Current MVP growth skills:

```text
spark
snowflake
bigquery
```

Priority levels:

| Condition | priority_level |
|---|---|
| `job_count >= 5` | `learn_next` |
| `job_count >= 2` | `important` |
| otherwise | `monitor` |

## Weekly Market Summary Logic

`mart_weekly_market_summary` is implemented as a lightweight current-week mart.

It exposes:

- current reporting week
- total active jobs
- relevant jobs
- high-match jobs
- junior-friendly jobs
- top skills
- top missing skills
- top locations
- top companies
- summary text
- `has_enough_history`

Important MVP limitation:

Weekly comparison is not fully implemented yet because this requires enough historical runs and a more mature weekly aggregation layer. The current mart sets `has_enough_history = false` and documents this limitation clearly.

## Tests Added

### YAML tests

Added basic dbt tests for:

- `not_null` keys and display fields
- `unique` grain keys
- accepted values for boolean flags and relevance buckets

### Singular tests

Added sanity tests for:

- relevance score range 0–100
- non-negative overview counts
- skill share between 0 and 1
- location share between 0 and 1
- company counts not negative
- freshness counts not negative
- missing skill share between 0 and 1
- weekly summary counts not negative

## Validation Commands

These are the commands that should be run from the repository root:

```bash
dbt parse --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar
```

```bash
dbt build --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar --select marts
```

```bash
dbt build --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar
```

## Validation Status

Local integration validation was executed after copying the files into the main repository.

Validation commands run from the repository root:

```bash
dbt parse --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar

dbt build --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar --select marts

dbt build --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar

Final local result:
Completed successfully
Done. PASS=144 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=144

## Known Limitations

1. Skill detection is rule-based and may miss synonyms.
2. Relevance scoring is explainable but heuristic, not a machine-learning recommendation model.
3. Weekly comparison is a placeholder until enough historical data is accumulated.
4. Location logic uses a simple city/region/country fallback and does not perform geocoding.
5. Missing skills currently focus on MVP growth skills only: Spark, Snowflake, BigQuery.
6. The marts assume that the warehouse current model exposes fields documented in the existing data model contract.

## Next Recommended Step for Streamlit Engineer

Build the Streamlit dashboard using marts only.

Recommended page-to-mart mapping:

| Streamlit page | Mart |
|---|---|
| Overview | `marts.mart_job_market_overview` |
| Relevant Jobs | `marts.mart_relevant_jobs` |
| Skill Radar | `marts.mart_skill_demand`, `marts.mart_missing_skills` |
| Locations | `marts.mart_location_activity` or `marts.mart_location_demand` |
| Companies | `marts.mart_company_activity` or `marts.mart_company_demand` |
| Weekly Report | `marts.mart_weekly_market_summary` |
| Data Freshness | `marts.mart_data_freshness` |

Streamlit should not calculate relevance score, skill demand, or weekly summaries directly.
