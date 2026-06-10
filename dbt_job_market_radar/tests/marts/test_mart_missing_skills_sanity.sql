select *
from {{ ref('mart_missing_skills') }}
where job_count < 0
   or share_of_relevant_jobs < 0
   or share_of_relevant_jobs > 1
