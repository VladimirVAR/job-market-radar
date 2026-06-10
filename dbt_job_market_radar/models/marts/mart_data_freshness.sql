{{ config(materialized='view') }}

-- Grain: one row per source_name.
-- Purpose: expose data and pipeline freshness for the Streamlit Data Freshness page.
-- This mart is allowed to use raw batch/request metadata because it is operational freshness data.

with successful_batches as (

    select
        batch_id,
        source_name,
        pipeline_name,
        started_at,
        finished_at,
        records_loaded,
        requests_made,
        row_number() over (
            partition by source_name
            order by finished_at desc nulls last, started_at desc
        ) as rn
    from {{ source('raw', 'raw_load_batches') }}
    where status = 'success'

),

latest_successful_batches as (

    select *
    from successful_batches
    where rn = 1

),

request_counts as (

    select
        batch_id,
        source_name,
        count(*) as latest_requests_recorded,
        max(finished_at) as latest_request_finished_at
    from {{ source('raw', 'raw_api_requests') }}
    group by batch_id, source_name

),

current_job_counts as (

    select
        source_name,
        count(*) filter (where coalesce(is_current_version, true) = true) as current_job_count,
        count(*) as current_row_count,
        max(last_seen_at) as latest_current_last_seen_at
    from {{ ref('wh_job_posting_current') }}
    group by source_name

),

snapshot_counts as (

    select
        source_name,
        count(*) as snapshot_row_count,
        max(retrieved_at) as latest_snapshot_retrieved_at
    from {{ ref('wh_job_posting_snapshots') }}
    group by source_name

)

select
    coalesce(b.source_name, c.source_name, s.source_name) as source_name,
    b.batch_id as latest_successful_batch_id,
    b.started_at as latest_successful_batch_started_at,
    b.finished_at as latest_successful_batch_finished_at,
    b.records_loaded as latest_records_loaded,
    coalesce(b.requests_made, r.latest_requests_recorded) as latest_requests_made,
    r.latest_requests_recorded,
    c.current_job_count,
    c.current_row_count,
    s.snapshot_row_count,
    nullif(
        greatest(
            coalesce(b.finished_at, timestamp '1900-01-01'),
            coalesce(r.latest_request_finished_at, timestamp '1900-01-01'),
            coalesce(c.latest_current_last_seen_at, timestamp '1900-01-01'),
            coalesce(s.latest_snapshot_retrieved_at, timestamp '1900-01-01')
        ),
        timestamp '1900-01-01'
    ) as freshest_data_timestamp,
    current_timestamp as generated_at
from latest_successful_batches b
left join request_counts r
    on b.batch_id = r.batch_id
   and b.source_name = r.source_name
full outer join current_job_counts c
    on b.source_name = c.source_name
full outer join snapshot_counts s
    on coalesce(b.source_name, c.source_name) = s.source_name
