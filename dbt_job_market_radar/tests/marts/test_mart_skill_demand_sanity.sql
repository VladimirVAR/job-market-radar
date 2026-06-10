select *
from {{ ref('mart_skill_demand') }}
where matching_job_count < 0
   or total_job_count < 0
   or share_of_jobs < 0
   or share_of_jobs > 1
   or matching_job_count > total_job_count
