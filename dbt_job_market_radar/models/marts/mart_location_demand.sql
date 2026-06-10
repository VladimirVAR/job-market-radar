{{ config(materialized='view') }}

-- Grain: one row per dashboard location bucket.
-- Purpose: location distribution for the Streamlit Locations page.
-- Missing locations are intentionally grouped into an `unknown` bucket.

with jobs as (

    select
        canonical_job_key,
        coalesce(nullif(city, ''), nullif(region, ''), nullif(country, ''), 'unknown') as location_name,
        company_name,
        relevance_score,
        is_junior_friendly,
        last_seen_at
    from {{ ref('mart_job_postings_current') }}
    where coalesce(is_active, true) = true

),

totals as (

    select count(*) as total_job_count
    from jobs

)

select
    location_name,
    count(*) as job_count,
    case
        when max(t.total_job_count) = 0 then 0::numeric
        else count(*)::numeric / max(t.total_job_count)
    end as share_of_jobs,
    count(distinct nullif(company_name, 'unknown')) as distinct_companies,
    avg(relevance_score) as avg_relevance_score,
    count(*) filter (where is_junior_friendly = true) as junior_friendly_job_count,
    max(last_seen_at) as last_seen_at,
    current_timestamp as generated_at
from jobs
cross join totals t
group by location_name
