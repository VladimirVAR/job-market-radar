{{ config(materialized='view') }}

-- Grain: one row per company bucket.
-- Purpose: company distribution for the Streamlit Companies page.
-- Missing companies are intentionally grouped into an `unknown` bucket.

with jobs as (

    select
        canonical_job_key,
        coalesce(nullif(company_name, ''), 'unknown') as company_name,
        coalesce(nullif(city, ''), nullif(region, ''), nullif(country, ''), 'unknown') as location_name,
        relevance_score,
        is_junior_friendly,
        last_seen_at
    from {{ ref('mart_job_postings_current') }}
    where coalesce(is_active, true) = true

)

select
    company_name,
    count(*) as job_count,
    count(distinct location_name) as distinct_locations,
    avg(relevance_score) as avg_relevance_score,
    count(*) filter (where relevance_score >= 60) as relevant_job_count,
    count(*) filter (where is_junior_friendly = true) as junior_friendly_job_count,
    max(last_seen_at) as last_seen_at,
    current_timestamp as generated_at
from jobs
group by company_name
