{{ config(materialized='view') }}

-- Compatibility mart for Streamlit Task 011 naming.
-- Grain: one company per current market snapshot.

select
    'current' as market_period,
    company_name,
    job_count as active_job_count,
    job_count as new_job_count, -- MVP simplification until weekly history is expanded.
    relevant_job_count,
    junior_friendly_job_count,
    distinct_locations,
    avg_relevance_score,
    last_seen_at,
    generated_at
from {{ ref('mart_company_demand') }}
