select *
from {{ ref('mart_weekly_market_summary') }}
where total_active_jobs < 0
   or new_jobs < 0
   or closed_or_missing_jobs < 0
   or relevant_job_count < 0
   or high_match_job_count < 0
   or junior_friendly_jobs < 0
