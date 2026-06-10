/*
Purpose:
    Ensure every staging row maps back to exactly one raw job posting row.

Passing behavior:
    This test returns zero rows.

Failing behavior:
    Returns staging rows that cannot be traced back to raw.raw_france_travail_job_postings.
*/

select
    s.raw_job_posting_id,
    s.batch_id,
    s.request_id,
    s.source_name,
    s.source_job_id,
    s.source_job_key
from {{ ref('stg_france_travail_job_postings') }} as s
left join {{ source('raw', 'raw_france_travail_job_postings') }} as r
    on s.raw_job_posting_id = r.raw_job_posting_id
   and s.batch_id = r.batch_id
   and s.request_id = r.request_id
   and s.source_job_key = r.source_job_key
where r.raw_job_posting_id is null
