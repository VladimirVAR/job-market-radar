{{ config(materialized='table') }}

with staging as (

    select * from {{ ref('stg_france_travail_job_postings') }}
    union all
    select * from {{ ref('stg_adzuna_job_postings') }}

),

final as (

    select
        -- Warehouse snapshot identifiers
        raw_job_posting_id as snapshot_id,
        raw_job_posting_id as job_snapshot_id,

        -- Lineage columns preserved from staging/raw
        batch_id,
        request_id,
        raw_job_posting_id,
        source_name,
        source_job_id,
        source_job_key,
        source_job_key as canonical_job_key,
        search_scope_key,

        -- Business attributes parsed by staging
        job_title,
        nullif(regexp_replace(lower(trim(job_title)), '\s+', ' ', 'g'), '') as normalized_job_title,
        company_name,
        nullif(
            regexp_replace(
                lower(trim(coalesce(company_name, 'unknown_company'))),
                '[^a-z0-9]+',
                '_',
                'g'
            ),
            ''
        ) as company_key,
        location_raw,
        nullif(
            regexp_replace(
                lower(trim(coalesce(city, location_raw, 'unknown_location'))),
                '[^a-z0-9]+',
                '_',
                'g'
            ),
            ''
        ) as location_key,
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

        -- Snapshot semantics
        true as is_seen_in_batch,
        retrieved_at as snapshot_loaded_at,
        current_timestamp as created_at

    from staging

)

select *
from final
