/*
Purpose:
    Validate current-state temporal consistency.

Expected rule:
    first_seen_at <= last_seen_at

Passing behavior:
    This test returns zero rows.
*/

select
    canonical_job_key,
    source_job_key,
    first_seen_at,
    last_seen_at
from {{ ref('wh_job_posting_current') }}
where first_seen_at is null
   or last_seen_at is null
   or first_seen_at > last_seen_at
