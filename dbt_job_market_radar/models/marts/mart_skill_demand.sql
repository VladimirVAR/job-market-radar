{{ config(materialized='view') }}

-- Grain: one row per skill.
-- Purpose: skill demand summary for the Streamlit Skill Radar page.
-- MVP simplification: rule-based skill matching uses job title + description from current postings.

with current_jobs as (

    select
        canonical_job_key,
        source_name,
        last_seen_at,
        coalesce(is_current_version, true) as is_active,
        lower(
            coalesce(job_title, '') || ' ' ||
            coalesce(normalized_job_title, '') || ' ' ||
            coalesce(description_text, '')
        ) as searchable_text
    from {{ ref('wh_job_posting_current') }}
    where coalesce(is_current_version, true) = true

),

skill_dictionary as (

    select *
    from (
        values
            ('python', 'programming', '(^|[^a-z0-9])python([^a-z0-9]|$)'),
            ('sql', 'database', '(^|[^a-z0-9])sql([^a-z0-9]|$)'),
            ('dbt', 'transformation', '(^|[^a-z0-9])dbt([^a-z0-9]|$)'),
            ('airflow', 'orchestration', 'airflow'),
            ('docker', 'devops', 'docker'),
            ('postgresql', 'database', 'postgres|postgresql'),
            ('aws', 'cloud', '(^|[^a-z0-9])(aws|amazon web services)([^a-z0-9]|$)'),
            ('spark', 'big_data', 'spark|pyspark'),
            ('snowflake', 'warehouse', 'snowflake'),
            ('bigquery', 'warehouse', 'bigquery|big query'),
            ('data warehouse', 'warehouse', 'data[ -]?warehouse|data warehousing|(^|[^a-z0-9])dwh([^a-z0-9]|$)'),
            ('etl', 'data_engineering', '(^|[^a-z0-9])etl([^a-z0-9]|$)'),
            ('elt', 'data_engineering', '(^|[^a-z0-9])elt([^a-z0-9]|$)'),
            ('power_bi', 'bi', '(^|[^a-z0-9])(power\s*bi|powerbi)([^a-z0-9]|$)'),
            ('azure', 'cloud', '(^|[^a-z0-9])azure([^a-z0-9]|$)'),
            ('gcp', 'cloud', '(^|[^a-z0-9])gcp([^a-z0-9]|$)|google cloud')
    ) as skills(skill_name, skill_category, skill_pattern)

),

detected_skills as (

    select
        s.skill_name,
        s.skill_category,
        j.canonical_job_key,
        j.source_name,
        j.last_seen_at
    from current_jobs j
    cross join skill_dictionary s
    where j.searchable_text ~* s.skill_pattern

),

total_jobs as (

    select count(distinct canonical_job_key) as total_job_count
    from current_jobs

)

select
    s.skill_name,
    s.skill_category,
    count(distinct d.canonical_job_key) as matching_job_count,
    t.total_job_count,
    case
        when t.total_job_count = 0 then 0::numeric
        else count(distinct d.canonical_job_key)::numeric / t.total_job_count
    end as share_of_jobs,
    max(d.last_seen_at) as last_seen_at,
    current_timestamp as generated_at
from skill_dictionary s
cross join total_jobs t
left join detected_skills d
    on s.skill_name = d.skill_name
   and s.skill_category = d.skill_category
group by
    s.skill_name,
    s.skill_category,
    t.total_job_count
