select *
from {{ ref('mart_job_market_overview') }}
where total_current_job_postings < 0
   or active_job_count < 0
   or inactive_job_count < 0
   or distinct_companies < 0
   or distinct_locations < 0
   or jobs_with_company_present < 0
   or jobs_with_location_present < 0
   or jobs_with_contract_type_present < 0
   or jobs_with_work_mode_present < 0
   or relevant_job_count < 0
   or high_match_job_count < 0
   or junior_friendly_job_count < 0
