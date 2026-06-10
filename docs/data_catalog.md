# Data Catalog

## Purpose

This catalog documents the main raw tables, dbt models, and marts used by Job Market Radar.

Each important table or model includes:

- layer
- grain
- purpose
- key columns
- downstream consumers

---

## Raw Layer

### `raw.raw_load_batches`

**Layer:** raw
**Grain:** one row per pipeline execution.

**Purpose:**
Tracks ingestion runs and their operational status.

**Key columns:**

- `batch_id`
- `source_name`
- `pipeline_name`
- `started_at`
- `finished_at`
- `status`
- `triggered_by`
- `records_loaded`
- `requests_made`
- `error_message`

**Downstream consumers:**

- raw lineage checks
- warehouse batch logic
- marts data freshness
- Streamlit data freshness page
- Airflow validation context

---

### `raw.raw_api_requests`

**Layer:** raw
**Grain:** one row per API request, page, or search parameter set.

**Purpose:**
Stores request metadata for reproducibility, debugging, and lineage.

**Key columns:**

- `request_id`
- `batch_id`
- `source_name`
- `endpoint`
- `http_method`
- `request_params_json`
- `search_scope_key`
- `page_number`
- `page_size`
- `response_status_code`
- `response_time_ms`
- `error_message`

**Downstream consumers:**

- raw job posting lineage
- data quality checks
- data freshness reporting
- troubleshooting failed or partial ingestion runs

---

### `raw.raw_france_travail_job_postings`

**Layer:** raw
**Grain:** one raw job posting payload per source job per request per batch.

**Purpose:**
Preserves raw France Travail job posting payloads as returned by the source.

**Key columns:**

- `raw_job_posting_id`
- `batch_id`
- `request_id`
- `source_name`
- `source_job_id`
- `source_job_key`
- `search_scope_key`
- `raw_payload_json`
- `payload_hash`
- `ingested_at`

**Downstream consumers:**

- `staging.stg_france_travail_job_postings`
- source-to-target lineage
- raw payload debugging
- reprocessing when transformation logic changes

---

## Staging Layer

### `staging.stg_france_travail_job_postings`

**Layer:** staging
**Grain:** one cleaned France Travail job posting per source job per batch.

**Purpose:**
Parses raw France Travail JSON payloads into typed, source-specific columns.

**Key columns:**

- `batch_id`
- `request_id`
- `raw_job_posting_id`
- `source_name`
- `source_job_id`
- `source_job_key`
- `search_scope_key`
- `job_title`
- `company_name`
- `location_raw`
- `city`
- `region`
- `country`
- `contract_type`
- `work_mode`
- `seniority_level`
- `description_text`
- `published_at`
- `updated_at`
- `retrieved_at`
- `source_url`
- `payload_hash`

**Downstream consumers:**

- `warehouse.wh_job_posting_snapshots`
- staging tests
- lineage validation

---

## Warehouse Layer

### `warehouse.wh_job_posting_snapshots`

**Layer:** warehouse
**Grain:** one canonical job posting observation per source job per batch.

**Purpose:**
Stores historical observations of job postings across pipeline runs.

**Key columns:**

- `job_snapshot_id`
- `batch_id`
- `source_name`
- `source_job_id`
- `source_job_key`
- `canonical_job_key`
- `search_scope_key`
- `job_title`
- `normalized_job_title`
- `company_name`
- `company_key`
- `location_key`
- `city`
- `region`
- `country`
- `contract_type`
- `work_mode`
- `seniority_level`
- `description_text`
- `published_at`
- `updated_at`
- `retrieved_at`
- `source_url`
- `payload_hash`
- `raw_job_posting_id`
- `is_seen_in_batch`
- `created_at`

**Downstream consumers:**

- `warehouse.wh_job_posting_current`
- skill extraction models
- weekly market summaries
- historical analysis
- data quality checks

---

### `warehouse.wh_job_posting_current`

**Layer:** warehouse
**Grain:** one row per latest known canonical job posting.

**Purpose:**
Exposes the latest known state of each job posting.

**Key columns:**

- `canonical_job_key`
- `source_name`
- `source_job_key`
- `source_job_id`
- `latest_raw_job_posting_id`
- `latest_batch_id`
- `latest_request_id`
- `latest_search_scope_key`
- `first_seen_at`
- `last_seen_at`
- `observation_count`
- `is_current_version`
- `job_title`
- `normalized_job_title`
- `company_name`
- `company_key`
- `location_raw`
- `location_key`
- `city`
- `region`
- `country`
- `contract_type`
- `work_mode`
- `seniority_level`
- `description_text`
- `published_at`
- `updated_at`
- `retrieved_at`
- `source_url`
- `payload_hash`

**Downstream consumers:**

- `marts.mart_relevant_jobs`
- `marts.mart_job_postings_current`
- `marts.mart_location_activity`
- `marts.mart_company_activity`
- dashboard current-job pages

---

## Future Warehouse Extensions

The following warehouse concepts are useful future extensions but are not implemented as separate warehouse models in the current MVP:

- `warehouse.wh_skills`
- `warehouse.wh_job_posting_skills`

In the current MVP, skill extraction and relevance logic are implemented in the marts layer using rule-based SQL logic. Future versions may promote skills into dedicated warehouse models if the project needs richer skill taxonomy, cross-source normalization, or more advanced matching.


## Marts Layer

### `marts.mart_job_postings_current`

**Layer:** marts
**Grain:** one dashboard-ready current job posting.

**Purpose:**
Provides a clean current job list for exploration and dashboard pages.

**Key columns:**

- `canonical_job_key`
- `job_title`
- `company_name`
- `city`
- `region`
- `country`
- `contract_type`
- `work_mode`
- `seniority_level`
- `is_active`
- `source_url`
- `last_seen_at`

**Downstream consumers:**

- Streamlit overview
- job exploration pages
- reports

---

### `marts.mart_job_market_overview`

**Layer:** marts
**Grain:** one market overview row or market segment row depending on implementation.

**Purpose:**
Provides high-level KPI values for the dashboard overview.

**Key columns may include:**

- active job count
- new job count
- average relevance score
- top skills
- top cities
- latest batch timestamp

**Downstream consumers:**

- Streamlit overview page
- project review summary

---

### `marts.mart_relevant_jobs`

**Layer:** marts
**Grain:** one current active job posting enriched with relevance score.

**Purpose:**
Shows best matching job opportunities for the candidate profile.

**Key columns:**

- `canonical_job_key`
- `job_title`
- `company_name`
- `city`
- `region`
- `country`
- `contract_type`
- `work_mode`
- `seniority_level`
- `source_url`
- `published_at`
- `last_seen_at`
- `matched_candidate_skills`
- `missing_growth_skills`
- `required_skills_count`
- `matched_skills_count`
- `relevance_score`
- `relevance_reason`
- `is_junior_friendly`

**Downstream consumers:**

- Streamlit Relevant Jobs page
- project demo
- technical review query

---

### `marts.mart_skill_demand`

**Layer:** marts
**Grain:** one skill per market period, source, and location segment.

**Purpose:**
Shows demand for skills in the target market.

**Key columns:**

- `market_period`
- `source_name`
- `country`
- `region`
- `city`
- `skill_key`
- `skill_name`
- `skill_category`
- `job_count`
- `active_job_count`
- `share_of_jobs`

**Downstream consumers:**

- Streamlit Skill Radar page
- missing skill analysis
- weekly report

---

### `marts.mart_missing_skills`

**Layer:** marts
**Grain:** one missing or growth skill per market period.

**Purpose:**
Highlights skills that appear in relevant jobs but are not part of the current candidate profile.

**Key columns:**

- `market_period`
- `skill_key`
- `skill_name`
- `skill_category`
- `job_count`
- `share_of_relevant_jobs`
- `priority_level`

**Downstream consumers:**

- Streamlit Skill Radar page
- learning roadmap discussion
- technical review demo

---

### `marts.mart_location_activity`

**Layer:** marts
**Grain:** one location per market period.

**Purpose:**
Shows where relevant job market activity is concentrated.

**Key columns:**

- `market_period`
- `country`
- `region`
- `city`
- `active_job_count`
- `new_job_count`
- `junior_friendly_job_count`
- `avg_relevance_score`

**Downstream consumers:**

- Streamlit Locations page
- weekly report
- project demo

---

### `marts.mart_company_activity`

**Layer:** marts
**Grain:** one company per market period.

**Purpose:**
Shows companies that repeatedly post relevant roles.

**Key columns:**

- `market_period`
- `company_key`
- `company_name`
- `active_job_count`
- `new_job_count`
- `repeated_posting_count`
- `avg_relevance_score`

**Downstream consumers:**

- Streamlit Companies page
- candidate targeting strategy
- weekly report

---

### `marts.mart_weekly_market_summary`

**Layer:** marts
**Grain:** one week per market segment.

**Purpose:**
Summarizes weekly job market changes.

**Key columns:**

- `week_start_date`
- `source_name`
- `country`
- `region`
- `city`
- `total_active_jobs`
- `new_jobs`
- `closed_or_missing_jobs`
- `junior_friendly_jobs`
- `top_skills`
- `top_missing_skills`
- `top_companies`
- `avg_relevance_score`

**Downstream consumers:**

- Streamlit Weekly Report page
- future generated Markdown reports
- technical review demo

---

### `marts.mart_data_freshness`

**Layer:** marts
**Grain:** one freshness/status row per latest source or pipeline segment depending on implementation.

**Purpose:**
Shows whether dashboard data is based on a recent successful run.

**Key columns may include:**

- latest batch id
- latest batch status
- latest run timestamp
- records loaded
- requests made
- latest dbt build context if available

**Downstream consumers:**

- Streamlit Data Freshness page
- validation summary
- demo reliability checks

---

## Catalog Summary

The model is designed around four principles:

1. Raw data is preserved before transformation.
2. Every important table has a clear grain.
3. Lineage is carried from marts back to raw records.
4. Streamlit consumes dashboard-ready marts instead of calculating business metrics in the UI.
