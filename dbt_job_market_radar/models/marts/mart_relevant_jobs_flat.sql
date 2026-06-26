{{ config(materialized='view') }}

-- Grain: one row per active job posting.
-- Purpose: flat version of mart_relevant_jobs for Power BI and other BI tools that do not
--          support PostgreSQL ARRAY columns natively. All five array columns are converted
--          to comma-separated text. No filtering or scoring logic lives here; this view
--          is a thin projection over mart_relevant_jobs only.

select
    canonical_job_key,
    source_job_key,
    source_name,
    job_title,
    company_name,
    city,
    region,
    country,
    contract_type,
    work_mode,
    seniority_level,
    source_url,
    job_url,
    published_at,
    first_seen_at,
    last_seen_at,
    array_to_string(detected_skills, ', ')         as detected_skills,
    array_to_string(matched_candidate_skills, ', ') as matched_candidate_skills,
    array_to_string(missing_growth_skills, ', ')    as missing_growth_skills,
    required_skills_count,
    matched_skills_count,
    missing_growth_skill_count,
    relevance_score,
    relevance_bucket,
    relevance_reason,
    is_junior_friendly,
    role_fit_score,
    skill_fit_score,
    seniority_fit_score,
    contract_fit_score,
    location_fit_score,
    growth_value_score,
    negative_signal_penalty,
    candidate_fit_score,
    candidate_fit_band,
    application_priority,
    array_to_string(positive_reason_codes, ', ')   as positive_reason_codes,
    array_to_string(negative_reason_codes, ', ')   as negative_reason_codes,
    candidate_fit_reason,
    is_strong_target_role,
    is_acceptable_adjacent_role,
    is_seniority_risk,
    is_stretch_opportunity,
    is_learning_signal,
    is_active,
    latest_batch_id,
    payload_hash
from {{ ref('mart_relevant_jobs') }}
