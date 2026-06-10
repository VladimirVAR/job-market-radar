select *
from {{ ref('mart_company_demand') }}
where job_count < 0
   or distinct_locations < 0
   or relevant_job_count < 0
   or relevant_job_count > job_count
   or junior_friendly_job_count < 0
   or junior_friendly_job_count > job_count
