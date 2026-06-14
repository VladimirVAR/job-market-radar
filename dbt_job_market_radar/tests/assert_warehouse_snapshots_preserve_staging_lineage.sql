/*
Purpose:
    Ensure every warehouse snapshot row maps back to a staging row
    from one of the known sources.

Passing behavior:
    This test returns zero rows.

Failing behavior:
    Returns warehouse snapshot rows that cannot be traced back to any staging source.
*/

with all_staging as (

    select raw_job_posting_id, batch_id, source_job_key
    from {{ ref('stg_france_travail_job_postings') }}

    union all

    select raw_job_posting_id, batch_id, source_job_key
    from {{ ref('stg_adzuna_job_postings') }}

)

select
    w.job_snapshot_id,
    w.raw_job_posting_id,
    w.batch_id,
    w.source_name,
    w.source_job_id,
    w.source_job_key,
    w.canonical_job_key
from {{ ref('wh_job_posting_snapshots') }} as w
left join all_staging as s
    on w.raw_job_posting_id = s.raw_job_posting_id
   and w.batch_id = s.batch_id
   and w.source_job_key = s.source_job_key
where s.raw_job_posting_id is null
