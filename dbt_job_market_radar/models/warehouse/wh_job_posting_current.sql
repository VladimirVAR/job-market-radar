{{ config(materialized='view') }}

with snapshots as (

    select *
    from {{ ref('wh_job_posting_snapshots') }}

),

scope_batches as (

    select distinct
        b.source_name,
        r.search_scope_key,
        b.batch_id,
        b.started_at
    from {{ source('raw', 'raw_load_batches') }} b
    join {{ source('raw', 'raw_api_requests') }} r on r.batch_id = b.batch_id
    where b.status = 'success'

),

scope_latest as (

    select distinct on (source_name, search_scope_key)
        source_name,
        search_scope_key,
        batch_id as latest_scope_batch_id
    from scope_batches
    order by source_name, search_scope_key, started_at desc, batch_id desc

),

missing_since as (

    select
        r.source_job_key,
        (array_agg(sb.batch_id order by sb.started_at asc, sb.batch_id asc))[1] as missing_since_batch_id
    from (
        select distinct on (source_job_key)
            source_job_key,
            source_name,
            search_scope_key,
            retrieved_at as last_seen_retrieved_at
        from snapshots
        order by source_job_key, retrieved_at desc, raw_job_posting_id desc
    ) r
    join scope_batches sb
        on sb.source_name = r.source_name
       and sb.search_scope_key = r.search_scope_key
       and sb.started_at > r.last_seen_retrieved_at
    where not exists (
        select 1 from snapshots sn
        where sn.source_job_key = r.source_job_key
          and sn.batch_id = sb.batch_id
          and sn.search_scope_key = sb.search_scope_key
    )
    group by r.source_job_key

),

ranked as (

    select
        *,
        row_number() over (
            partition by source_job_key
            order by
                coalesce(updated_at, published_at, retrieved_at) desc nulls last,
                retrieved_at desc nulls last,
                raw_job_posting_id desc
        ) as current_rank,
        min(retrieved_at) over (
            partition by source_job_key
        ) as first_seen_at,
        max(retrieved_at) over (
            partition by source_job_key
        ) as last_seen_at,
        count(*) over (
            partition by source_job_key
        ) as observation_count
    from snapshots

),

final as (

    select
        -- Current-state identifiers
        ranked.source_job_key,
        ranked.canonical_job_key,
        ranked.source_name,
        ranked.source_job_id,
        ranked.raw_job_posting_id as latest_raw_job_posting_id,
        ranked.batch_id as latest_batch_id,
        ranked.request_id as latest_request_id,
        ranked.search_scope_key as latest_search_scope_key,

        -- Latest known business attributes
        ranked.job_title,
        ranked.normalized_job_title,
        ranked.company_name,
        ranked.company_key,
        ranked.location_raw,
        ranked.location_key,
        ranked.city,
        ranked.region,
        ranked.country,
        ranked.contract_type,
        ranked.work_mode,
        ranked.seniority_level,
        ranked.description_text,
        ranked.published_at,
        ranked.updated_at,
        ranked.retrieved_at,
        ranked.source_url,
        ranked.payload_hash,

        -- Observation metadata
        ranked.first_seen_at,
        ranked.last_seen_at,
        ranked.observation_count,

        -- Active/inactive: true only when job appears in the latest comparable scope batch.
        -- Defaults to true when no comparable batch is found to avoid false inactivation.
        case
            when sl.latest_scope_batch_id is null then true
            else (ranked.batch_id = sl.latest_scope_batch_id)
        end as is_current_version,

        -- First later comparable batch where this job was absent; null when still active.
        ms.missing_since_batch_id

    from ranked
    left join scope_latest sl
        on sl.source_name = ranked.source_name
       and sl.search_scope_key = ranked.search_scope_key
    left join missing_since ms
        on ms.source_job_key = ranked.source_job_key
    where ranked.current_rank = 1

)

select *
from final
