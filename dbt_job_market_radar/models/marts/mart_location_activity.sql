{{ config(materialized='view') }}

-- Compatibility mart for Streamlit Task 011 naming.
-- Grain: one location per current market snapshot.

select
    'current' as market_period,
    location_name,
    job_count as active_job_count,
    job_count as new_job_count, -- MVP simplification until weekly history is expanded.
    junior_friendly_job_count,
    avg_relevance_score,
    share_of_jobs,
    distinct_companies,
    last_seen_at,
    generated_at
from {{ ref('mart_location_demand') }}
