{{ config(materialized='view') }}

-- Grain: one row for the current market snapshot.
-- Purpose: high-level KPI table for the Streamlit Overview page.

with jobs as (

    select *
    from {{ ref('mart_job_postings_current') }}

),

active_jobs as (

    select *
    from jobs
    where coalesce(is_active, true) = true

)

select
    'current_market_snapshot' as overview_key,
    count(*) as total_current_job_postings,
    count(*) filter (where coalesce(is_active, true) = true) as active_job_count,
    count(*) filter (where coalesce(is_active, true) = false) as inactive_job_count,
    count(distinct nullif(company_name, 'unknown')) as distinct_companies,
    count(distinct nullif(coalesce(city, region, country), 'unknown')) as distinct_locations,
    min(first_seen_at) as earliest_first_seen_at,
    max(last_seen_at) as latest_last_seen_at,
    count(*) filter (where company_name is not null and company_name <> 'unknown') as jobs_with_company_present,
    count(*) filter (where coalesce(city, region, country) is not null and coalesce(city, region, country) <> 'unknown') as jobs_with_location_present,
    count(*) filter (where contract_type is not null) as jobs_with_contract_type_present,
    count(*) filter (where work_mode is not null and work_mode <> 'unknown') as jobs_with_work_mode_present,
    count(*) filter (where relevance_score >= 60 and coalesce(is_active, true) = true) as relevant_job_count,
    count(*) filter (where relevance_score >= 80 and coalesce(is_active, true) = true) as high_match_job_count,
    count(*) filter (where is_junior_friendly = true and coalesce(is_active, true) = true) as junior_friendly_job_count,
    avg(relevance_score) filter (where coalesce(is_active, true) = true) as avg_relevance_score,
    current_timestamp as generated_at
from jobs
