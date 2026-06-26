{{ config(materialized='view') }}

-- Grain: one row per source_name.
-- Purpose: pipeline monitoring mart for Power BI and other BI tools.
--          Adds health classification and batch history on top of mart_data_freshness.

with freshness as (

    select
        source_name,
        latest_successful_batch_id,
        latest_successful_batch_started_at,
        latest_successful_batch_finished_at,
        latest_records_loaded   as records_loaded_last_batch,
        latest_requests_made    as requests_made_last_batch,
        current_job_count,
        freshest_data_timestamp,
        generated_at
    from {{ ref('mart_data_freshness') }}

),

batch_history as (

    select
        source_name,
        count(*)                                             as total_batches_all_time,
        count(*) filter (where status = 'success')          as successful_batches_all_time,
        count(*) filter (where status = 'failed')           as failed_batches_all_time,
        count(*) filter (where status = 'running')          as running_batches_all_time,
        max(finished_at) filter (where status = 'failed')   as last_failed_at
    from {{ source('raw', 'raw_load_batches') }}
    group by source_name

),

last_failure as (

    select distinct on (source_name)
        source_name,
        left(error_message, 500) as last_error_message
    from {{ source('raw', 'raw_load_batches') }}
    where status = 'failed'
    order by source_name, finished_at desc nulls last

),

combined as (

    select
        coalesce(f.source_name, h.source_name)                      as source_name,
        f.latest_successful_batch_id,
        f.latest_successful_batch_started_at,
        f.latest_successful_batch_finished_at,
        extract(epoch from (
            current_timestamp - f.latest_successful_batch_finished_at
        )) / 60.0                                                    as minutes_since_last_success,
        f.records_loaded_last_batch,
        f.requests_made_last_batch,
        f.current_job_count,
        coalesce(h.total_batches_all_time, 0)                       as total_batches_all_time,
        coalesce(h.successful_batches_all_time, 0)                  as successful_batches_all_time,
        coalesce(h.failed_batches_all_time, 0)                      as failed_batches_all_time,
        coalesce(h.running_batches_all_time, 0)                     as running_batches_all_time,
        h.last_failed_at,
        lf.last_error_message,
        f.freshest_data_timestamp,
        f.generated_at
    from freshness f
    full outer join batch_history h
        on f.source_name = h.source_name
    left join last_failure lf
        on coalesce(f.source_name, h.source_name) = lf.source_name

),

classified as (

    select
        *,

        case
            when freshest_data_timestamp is null
                then 'no_data'
            when freshest_data_timestamp < current_timestamp - interval '7 days'
                then 'stale'
            when freshest_data_timestamp < current_timestamp - interval '48 hours'
                then 'warning'
            else 'healthy'
        end as freshness_status,

        case
            when latest_successful_batch_finished_at is null
                then 'no_data'
            when latest_successful_batch_finished_at < current_timestamp - interval '7 days'
                then 'stale'
            when latest_successful_batch_finished_at < current_timestamp - interval '48 hours'
                then 'warning'
            when last_failed_at > coalesce(
                    latest_successful_batch_finished_at,
                    timestamp '1900-01-01'
                )
                then 'warning'
            else 'healthy'
        end as source_health_status

    from combined

)

select
    source_name,
    latest_successful_batch_id,
    latest_successful_batch_started_at,
    latest_successful_batch_finished_at,
    round(minutes_since_last_success::numeric, 1)           as minutes_since_last_success,
    records_loaded_last_batch,
    requests_made_last_batch,
    current_job_count,
    total_batches_all_time,
    successful_batches_all_time,
    failed_batches_all_time,
    running_batches_all_time,
    last_failed_at,
    last_error_message,
    freshest_data_timestamp,
    freshness_status,
    source_health_status,
    case source_health_status
        when 'no_data'
            then source_name || ': no successful load recorded'
        when 'stale'
            then source_name || ': stale data, last success '
                || round((minutes_since_last_success / 1440)::numeric)::text || ' days ago'
        when 'warning'
            then case
                when last_failed_at > coalesce(latest_successful_batch_finished_at, timestamp '1900-01-01')
                    then source_name || ': latest pipeline attempt failed after last successful load'
                else
                    source_name || ': data is aging, last success '
                        || round((minutes_since_last_success / 60)::numeric)::text || ' hours ago'
            end
        else
            source_name || ': OK, last loaded '
                || round(minutes_since_last_success::numeric)::text || ' min ago'
    end                                                     as monitoring_message,
    generated_at
from classified
