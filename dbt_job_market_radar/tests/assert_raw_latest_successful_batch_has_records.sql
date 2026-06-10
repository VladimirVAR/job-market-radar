/*
Purpose:
    Ensure the latest successful ingestion batch exists and loaded at least one raw job posting.

Passing behavior:
    This test returns zero rows.

Failing behavior:
    Returns one row if:
    - no successful batch exists
    - latest successful batch has records_loaded <= 0
    - latest successful batch has records_loaded is null
*/

with latest_successful_batch as (

    select
        batch_id,
        status,
        records_loaded,
        started_at,
        finished_at
    from {{ source('raw', 'raw_load_batches') }}
    where status = 'success'
    order by
        started_at desc nulls last,
        batch_id desc
    limit 1

),

validation_errors as (

    select
        'no_successful_batch_exists' as failure_reason,
        cast(null as uuid) as batch_id,
        cast(null as text) as status,
        cast(null as integer) as records_loaded

    where not exists (
        select 1
        from latest_successful_batch
    )

    union all

    select
        'latest_successful_batch_has_no_records' as failure_reason,
        batch_id,
        status,
        records_loaded
    from latest_successful_batch
    where coalesce(records_loaded, 0) <= 0

)

select *
from validation_errors
