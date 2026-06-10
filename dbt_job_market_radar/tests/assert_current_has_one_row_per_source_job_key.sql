/*
Purpose:
    Ensure the current-state warehouse model respects its declared grain.

Expected grain:
    one row per source_job_key

Passing behavior:
    This test returns zero rows.
*/

select
    source_job_key,
    count(*) as row_count
from {{ ref('wh_job_posting_current') }}
group by source_job_key
having count(*) > 1
