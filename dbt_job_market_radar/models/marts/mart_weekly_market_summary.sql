{{ config(materialized='view') }}

-- Grain: one row per current reporting week.
-- Purpose: lightweight weekly summary placeholder backed by marts, not Streamlit logic.
-- MVP simplification: with limited history, WoW comparison is intentionally not calculated here yet.

with overview as (

    select *
    from {{ ref('mart_job_market_overview') }}

),

top_skills as (

    select
        array_agg(skill_name order by matching_job_count desc, skill_name) filter (where matching_job_count > 0) as top_skills
    from {{ ref('mart_skill_demand') }}

),

top_locations as (

    select
        array_agg(location_name order by job_count desc, location_name) filter (where job_count > 0) as top_locations
    from {{ ref('mart_location_demand') }}

),

top_companies as (

    select
        array_agg(company_name order by job_count desc, company_name) filter (where job_count > 0 and company_name <> 'unknown') as top_companies
    from {{ ref('mart_company_demand') }}

),

top_missing_skills as (

    select
        array_agg(skill_name order by job_count desc, skill_name) filter (where job_count > 0) as top_missing_skills
    from {{ ref('mart_missing_skills') }}

)

select
    date_trunc('week', current_date)::date as week_start_date,
    (date_trunc('week', current_date)::date + interval '6 days')::date as week_end_date,
    o.active_job_count as total_active_jobs,
    null::integer as new_jobs, -- Weekly new-job delta requires historical batch comparison; not yet implemented.
    o.inactive_job_count as closed_or_missing_jobs,
    o.relevant_job_count,
    o.high_match_job_count,
    o.junior_friendly_job_count as junior_friendly_jobs,
    o.avg_relevance_score,
    coalesce(s.top_skills[1:5], array[]::text[]) as top_skills,
    coalesce(ms.top_missing_skills[1:5], array[]::text[]) as top_missing_skills,
    coalesce(l.top_locations[1:5], array[]::text[]) as top_locations,
    coalesce(c.top_companies[1:5], array[]::text[]) as top_companies,
    false as has_enough_history,
    concat(
        'Current market snapshot contains ', o.active_job_count,
        ' active job postings, including ', o.relevant_job_count,
        ' relevant jobs and ', o.junior_friendly_job_count,
        ' junior-friendly opportunities. Weekly comparison will become available after more history is collected.'
    ) as summary_text,
    current_timestamp as generated_at
from overview o
cross join top_skills s
cross join top_locations l
cross join top_companies c
cross join top_missing_skills ms
