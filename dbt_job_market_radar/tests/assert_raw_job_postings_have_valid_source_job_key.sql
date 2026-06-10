/*
Purpose:
    Ensure raw job postings follow the MVP source job key convention.

Expected convention:
    source_job_key = source_name || ':' || source_job_id

Example:
    france_travail:123456

Passing behavior:
    This test returns zero rows.
*/

select
    raw_job_posting_id,
    batch_id,
    request_id,
    source_name,
    source_job_id,
    source_job_key
from {{ source('raw', 'raw_france_travail_job_postings') }}
where source_name is null
   or source_job_id is null
   or source_job_key is null
   or source_job_key <> source_name || ':' || source_job_id
