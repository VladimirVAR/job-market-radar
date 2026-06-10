select *
from {{ ref('mart_location_demand') }}
where job_count < 0
   or share_of_jobs < 0
   or share_of_jobs > 1
   or distinct_companies < 0
   or junior_friendly_job_count < 0
   or junior_friendly_job_count > job_count
