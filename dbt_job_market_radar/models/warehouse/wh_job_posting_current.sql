{{ config(materialized='view') }}

with snapshots as (

    select *
    from {{ ref('wh_job_posting_snapshots') }}

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
        source_job_key,
        canonical_job_key,
        source_name,
        source_job_id,
        raw_job_posting_id as latest_raw_job_posting_id,
        batch_id as latest_batch_id,
        request_id as latest_request_id,
        search_scope_key as latest_search_scope_key,

        -- Latest known business attributes
        job_title,
        normalized_job_title,
        company_name,
        company_key,
        location_raw,
        location_key,
        city,
        region,
        country,
        contract_type,
        work_mode,
        seniority_level,
        description_text,
        published_at,
        updated_at,
        retrieved_at,
        source_url,
        payload_hash,

        -- Observation metadata
        first_seen_at,
        last_seen_at,
        observation_count,
        true as is_current_version

    from ranked
    where current_rank = 1

)

select *
from final
