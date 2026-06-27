{{ config(materialized='view') }}

-- Compatibility mart for Streamlit Task 011 naming.
-- Grain: one missing/growth skill detected in relevant current jobs.
-- MVP interpretation: "missing" means a growth skill mentioned by a relevant job but not in the MVP candidate core profile.

with relevant_jobs as (

    select
        canonical_job_key,
        relevance_score,
        unnest(missing_growth_skills) as skill_name,
        last_seen_at
    from {{ ref('mart_relevant_jobs') }}
    where relevance_score >= 60
      and coalesce(array_length(missing_growth_skills, 1), 0) > 0

),

totals as (

    select count(distinct canonical_job_key) as relevant_job_count
    from {{ ref('mart_relevant_jobs') }}
    where relevance_score >= 60

),

aggregated as (

    select
        skill_name,
        count(distinct canonical_job_key) as job_count,
        avg(relevance_score) as avg_relevance_score,
        max(last_seen_at) as last_seen_at
    from relevant_jobs
    group by skill_name

)

select
    'current' as market_period,
    skill_name,
    case
        when skill_name in ('spark') then 'big_data'
        when skill_name in ('snowflake', 'bigquery') then 'warehouse'
        when skill_name in ('azure', 'gcp') then 'cloud'
        else 'other'
    end as skill_category,
    job_count,
    case
        when t.relevant_job_count = 0 then 0::numeric
        else job_count::numeric / t.relevant_job_count
    end as share_of_relevant_jobs,
    avg_relevance_score,
    case
        when job_count >= 5 then 'learn_next'
        when job_count >= 2 then 'important'
        else 'monitor'
    end as priority_level,
    last_seen_at,
    current_timestamp as generated_at
from aggregated a
cross join totals t
