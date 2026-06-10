# Data Model

## Purpose

This document defines the proposed data model for Job Market Radar.

The model follows the architecture:

```text
raw -> staging -> warehouse -> marts
```

Every table or model must have a clearly defined grain.

---

## Naming Conventions

General rules:

- Use English names.
- Use `snake_case`.
- Prefix raw tables with `raw_`.
- Prefix staging models with `stg_`.
- Prefix warehouse models with `wh_`.
- Prefix marts with `mart_`.
- Use clear technical keys such as `batch_id`, `request_id`, `source_job_key`, and `canonical_job_key`.

---

# Raw Schema

The raw schema preserves source data and ingestion metadata.

## `raw.raw_load_batches`

**Grain:** one row per pipeline execution.

### Purpose

Tracks each ingestion run.

### Columns

| Column | Description |
|---|---|
| `batch_id` | Unique pipeline run identifier |
| `source_name` | Source system name, for example `france_travail` |
| `pipeline_name` | Name of the pipeline |
| `started_at` | Pipeline start timestamp |
| `finished_at` | Pipeline finish timestamp |
| `status` | Batch status: `running`, `success`, `failed`, `partial_success` |
| `triggered_by` | Trigger source, for example `manual` or `airflow` |
| `records_loaded` | Number of raw job records loaded |
| `requests_made` | Number of API requests made |
| `error_message` | Error message if the run failed |
| `created_at` | Metadata creation timestamp |

---

## `raw.raw_api_requests`

**Grain:** one row per API request, page, or search parameter set.

### Purpose

Stores request metadata for reproducibility, debugging, and lineage.

### Columns

| Column | Description |
|---|---|
| `request_id` | Unique API request identifier |
| `batch_id` | Related load batch |
| `source_name` | Source system name |
| `endpoint` | API endpoint |
| `http_method` | HTTP method |
| `request_url` | Full request URL if safe to store |
| `request_params_json` | Request parameters as JSONB |
| `search_scope_key` | Comparable search scope identifier |
| `page_number` | API page number |
| `page_size` | Requested page size |
| `response_status_code` | HTTP response status |
| `response_time_ms` | Response time in milliseconds |
| `response_headers_json` | Response headers as JSONB, excluding secrets |
| `started_at` | Request start timestamp |
| `finished_at` | Request finish timestamp |
| `error_message` | Error message if request failed |
| `created_at` | Metadata creation timestamp |

---

## `raw.raw_france_travail_job_postings`

**Grain:** one raw job posting payload per source job per request per batch.

### Purpose

Stores raw France Travail job posting payloads as returned by the API.

### Columns

| Column | Description |
|---|---|
| `raw_job_posting_id` | Unique raw row identifier |
| `batch_id` | Related load batch |
| `request_id` | Related API request |
| `source_name` | Always `france_travail` for this table |
| `source_job_id` | Source-specific job id |
| `source_job_key` | Stable source-level key, for example `france_travail:{id}` |
| `search_scope_key` | Search scope that returned the job |
| `raw_payload_json` | Raw API job payload as JSONB |
| `payload_hash` | Hash of the raw payload |
| `ingested_at` | Timestamp when the row was ingested |
| `created_at` | Metadata creation timestamp |

---

# Staging Schema

The staging schema converts raw data into typed, source-specific models.

## `staging.stg_france_travail_job_postings`

**Grain:** one cleaned France Travail job posting per source job per batch.

### Purpose

Parses the raw France Travail payload into typed columns.

### Columns

| Column | Description |
|---|---|
| `batch_id` | Related load batch |
| `request_id` | Related API request |
| `raw_job_posting_id` | Related raw payload row |
| `source_name` | Source system name |
| `source_job_id` | Source-specific job id |
| `source_job_key` | Stable source-level job key |
| `search_scope_key` | Search scope that returned the job |
| `job_title` | Job title from source |
| `company_name` | Company name from source |
| `location_raw` | Raw location text |
| `city` | Parsed city if available |
| `region` | Parsed region if available |
| `country` | Parsed country |
| `contract_type` | Normalized contract type |
| `work_mode` | Normalized work mode |
| `seniority_level` | Inferred seniority level |
| `description_text` | Job description text |
| `published_at` | Source publication timestamp |
| `updated_at` | Source update timestamp if available |
| `retrieved_at` | Ingestion timestamp |
| `source_url` | URL to original job posting |
| `payload_hash` | Hash of raw payload |

---

# Warehouse Schema

The warehouse schema contains canonical analytical models.

## `warehouse.wh_job_posting_snapshots`

**Grain:** one canonical job posting observation per source job per batch.

### Purpose

Stores historical observations of job postings across pipeline runs.

### Columns

| Column | Description |
|---|---|
| `job_snapshot_id` | Unique snapshot row identifier |
| `batch_id` | Related load batch |
| `source_name` | Source system name |
| `source_job_id` | Source-specific job id |
| `source_job_key` | Stable source-level job key |
| `canonical_job_key` | Canonical job key |
| `search_scope_key` | Search scope that returned the job |
| `job_title` | Original job title |
| `normalized_job_title` | Normalized job title |
| `company_name` | Company name |
| `company_key` | Normalized company key |
| `location_key` | Normalized location key |
| `city` | City |
| `region` | Region |
| `country` | Country |
| `contract_type` | Contract type |
| `work_mode` | Work mode |
| `seniority_level` | Seniority level |
| `description_text` | Job description |
| `published_at` | Source publication timestamp |
| `updated_at` | Source update timestamp |
| `retrieved_at` | Ingestion timestamp |
| `source_url` | Source URL |
| `payload_hash` | Raw payload hash |
| `raw_job_posting_id` | Related raw row |
| `is_seen_in_batch` | Whether the job was observed in the batch |
| `created_at` | Model creation timestamp |

### MVP Key Strategy

For MVP:

```text
canonical_job_key = source_job_key
```

Future multi-source matching can introduce a more advanced canonical key.

---

## `warehouse.wh_job_posting_current`

**Grain:** one row per latest known canonical job posting.

### Purpose

Exposes the latest known state of every job posting.

### Columns

| Column | Description |
|---|---|
| `canonical_job_key` | Canonical job key |
| `source_name` | Source system name |
| `source_job_key` | Source-level job key |
| `latest_batch_id` | Latest batch where the job was evaluated |
| `first_seen_at` | First observed timestamp |
| `last_seen_at` | Last observed timestamp |
| `is_active` | Whether job is active in the latest comparable scope |
| `missing_since_batch_id` | Batch where the job first became missing |
| `job_title` | Latest job title |
| `normalized_job_title` | Latest normalized job title |
| `company_name` | Company name |
| `company_key` | Company key |
| `location_key` | Location key |
| `city` | City |
| `region` | Region |
| `country` | Country |
| `contract_type` | Contract type |
| `work_mode` | Work mode |
| `seniority_level` | Seniority level |
| `description_text` | Latest job description |
| `published_at` | Source publication timestamp |
| `updated_at` | Source update timestamp |
| `source_url` | Source URL |
| `payload_hash` | Latest raw payload hash |

---

## `warehouse.wh_skills`

**Grain:** one row per normalized skill.

### Purpose

Stores the normalized skill dictionary used for skill extraction.

### Columns

| Column | Description |
|---|---|
| `skill_key` | Stable normalized skill key |
| `skill_name` | Display skill name |
| `skill_category` | Skill category |
| `is_candidate_skill` | Whether this skill is part of the MVP candidate profile |
| `is_growth_skill` | Whether this skill is a target growth skill |
| `created_at` | Metadata creation timestamp |

---

## `warehouse.wh_job_posting_skills`

**Grain:** one row per detected skill per job snapshot.

### Purpose

Stores detected skills for each job snapshot.

### Columns

| Column | Description |
|---|---|
| `job_snapshot_id` | Related job snapshot |
| `canonical_job_key` | Related canonical job |
| `batch_id` | Related batch |
| `skill_key` | Detected skill key |
| `skill_name` | Detected skill name |
| `match_source` | Matching method, for example `dictionary_rule` |
| `match_confidence` | Confidence score |

---

## `warehouse.wh_candidate_profile_versions`

**Grain:** one row per candidate profile version.

### Purpose

Stores candidate profile versions used in relevance scoring.

### Columns

| Column | Description |
|---|---|
| `candidate_profile_version_id` | Profile version id |
| `profile_name` | Profile name |
| `valid_from` | Start date |
| `valid_to` | End date |
| `is_current` | Whether the profile version is current |
| `profile_json` | Candidate profile definition |
| `created_at` | Metadata creation timestamp |

---

## `warehouse.wh_skill_dictionary_versions`

**Grain:** one row per skill dictionary version.

### Purpose

Stores skill dictionary versions for reproducibility.

### Columns

| Column | Description |
|---|---|
| `skill_dictionary_version_id` | Dictionary version id |
| `valid_from` | Start date |
| `valid_to` | End date |
| `is_current` | Whether the dictionary version is current |
| `dictionary_json` | Skill dictionary definition |
| `created_at` | Metadata creation timestamp |

---

# Marts Schema

Marts are product-facing models consumed by Streamlit and reports.

## `marts.mart_relevant_jobs`

**Grain:** one current active job posting enriched with relevance score.

### Purpose

Shows the best job opportunities for the candidate.

### Columns

| Column | Description |
|---|---|
| `canonical_job_key` | Canonical job key |
| `job_title` | Job title |
| `company_name` | Company name |
| `city` | City |
| `region` | Region |
| `country` | Country |
| `contract_type` | Contract type |
| `work_mode` | Work mode |
| `seniority_level` | Seniority level |
| `source_name` | Source name |
| `source_url` | Job URL |
| `published_at` | Publication timestamp |
| `last_seen_at` | Last observed timestamp |
| `matched_candidate_skills` | Candidate skills found in job |
| `missing_growth_skills` | Growth skills required by the job |
| `required_skills_count` | Total detected skills |
| `matched_skills_count` | Number of matched candidate skills |
| `relevance_score` | Relevance score from 0 to 100 |
| `relevance_reason` | Human-readable explanation |
| `is_junior_friendly` | Junior-friendly flag |

---

## `marts.mart_skill_demand`

**Grain:** one skill per market period, location, and source.

### Purpose

Tracks market demand for each skill.

### Columns

| Column | Description |
|---|---|
| `market_period` | Reporting period |
| `source_name` | Source name |
| `country` | Country |
| `region` | Region |
| `city` | City |
| `skill_key` | Skill key |
| `skill_name` | Skill name |
| `skill_category` | Skill category |
| `job_count` | Number of jobs requiring the skill |
| `active_job_count` | Number of active jobs requiring the skill |
| `share_of_jobs` | Share of jobs requiring the skill |

---

## `marts.mart_missing_skills`

**Grain:** one missing or growth skill per market period.

### Purpose

Shows which skills the candidate should consider learning next.

### Columns

| Column | Description |
|---|---|
| `market_period` | Reporting period |
| `skill_key` | Skill key |
| `skill_name` | Skill name |
| `skill_category` | Skill category |
| `job_count` | Number of relevant jobs mentioning the skill |
| `share_of_relevant_jobs` | Share of relevant jobs mentioning the skill |
| `priority_level` | Learning priority level |

---

## `marts.mart_location_activity`

**Grain:** one location per market period.

### Purpose

Shows job market activity by location.

### Columns

| Column | Description |
|---|---|
| `market_period` | Reporting period |
| `country` | Country |
| `region` | Region |
| `city` | City |
| `active_job_count` | Active job count |
| `new_job_count` | New job count |
| `junior_friendly_job_count` | Junior-friendly job count |
| `avg_relevance_score` | Average relevance score |

---

## `marts.mart_company_activity`

**Grain:** one company per market period.

### Purpose

Shows which companies are active in the target job market.

### Columns

| Column | Description |
|---|---|
| `market_period` | Reporting period |
| `company_key` | Company key |
| `company_name` | Company name |
| `active_job_count` | Active job count |
| `new_job_count` | New job count |
| `repeated_posting_count` | Repeated posting count |
| `avg_relevance_score` | Average relevance score |

---

## `marts.mart_weekly_market_summary`

**Grain:** one week per market segment.

### Purpose

Provides a weekly summary of job market changes.

### Columns

| Column | Description |
|---|---|
| `week_start_date` | Week start date |
| `source_name` | Source name |
| `country` | Country |
| `region` | Region |
| `city` | City |
| `total_active_jobs` | Total active jobs |
| `new_jobs` | New jobs |
| `closed_or_missing_jobs` | Jobs no longer observed |
| `junior_friendly_jobs` | Junior-friendly jobs |
| `top_skills` | Top demanded skills |
| `top_missing_skills` | Top candidate growth skills |
| `top_companies` | Most active companies |
| `avg_relevance_score` | Average relevance score |

---

## Data Model Summary

The model is designed to preserve raw data, support historical analysis, expose current state, and produce dashboard-ready analytical outputs.

The most important design rules are:

- raw data is never overwritten
- every table has a defined grain
- every job can be traced back to the raw payload
- current state is derived from snapshots
- Streamlit consumes marts, not raw data
