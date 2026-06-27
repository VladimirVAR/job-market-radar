select
    w.total_active_jobs,
    w.closed_or_missing_jobs,
    o.total_current_job_postings
from {{ ref('mart_weekly_market_summary') }} w
cross join {{ ref('mart_job_market_overview') }} o
where w.total_active_jobs > o.total_current_job_postings
   or w.total_active_jobs + w.closed_or_missing_jobs <> o.total_current_job_postings
