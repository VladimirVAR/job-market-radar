{{ config(
    materialized='view',
    tags=['staging', 'adzuna']
) }}

with source as (

    select *
    from {{ source('raw', 'raw_adzuna_job_postings') }}

),

parsed as (

    select
        batch_id,
        request_id,
        raw_job_posting_id,
        source_name,
        source_job_id,
        source_job_key,
        search_scope_key,

        nullif(trim(raw_payload_json ->> 'title'), '') as job_title,

        nullif(trim(raw_payload_json -> 'company' ->> 'display_name'), '') as company_name,

        nullif(
            trim(raw_payload_json -> 'location' ->> 'display_name'),
            ''
        ) as location_raw,

        -- city: third element of location.area array (index 2), e.g. ["France", "Île-de-France", "Paris"]
        nullif(
            trim(raw_payload_json -> 'location' -> 'area' ->> 2),
            ''
        ) as city,

        -- region: second element of location.area array (index 1)
        nullif(
            trim(raw_payload_json -> 'location' -> 'area' ->> 1),
            ''
        ) as region,

        -- country: first element of location.area array (index 0), fallback to 'France'
        coalesce(
            nullif(trim(raw_payload_json -> 'location' -> 'area' ->> 0), ''),
            'France'
        ) as country,

        -- contract_type: uppercase permanent/contract value from Adzuna
        nullif(
            upper(trim(raw_payload_json ->> 'contract_type')),
            ''
        ) as contract_type,

        -- work_mode: infer from description text (Adzuna doesn't expose a dedicated field)
        case
            when lower(coalesce(raw_payload_json ->> 'description', '')) like '%100% télétravail%'
                or lower(coalesce(raw_payload_json ->> 'description', '')) like '%full remote%'
                or lower(coalesce(raw_payload_json ->> 'description', '')) like '%fully remote%'
                or lower(coalesce(raw_payload_json ->> 'title', '')) like '% remote%'
                then 'remote'
            when lower(coalesce(raw_payload_json ->> 'description', '')) like '%hybride%'
                or lower(coalesce(raw_payload_json ->> 'description', '')) like '%hybrid%'
                or lower(coalesce(raw_payload_json ->> 'description', '')) like '%télétravail partiel%'
                then 'hybrid'
            when lower(coalesce(raw_payload_json ->> 'description', '')) like '%présentiel%'
                or lower(coalesce(raw_payload_json ->> 'description', '')) like '%on-site%'
                or lower(coalesce(raw_payload_json ->> 'description', '')) like '%on site%'
                then 'on_site'
            else 'unknown'
        end as work_mode,

        -- seniority_level: infer from title and description
        case
            when lower(coalesce(raw_payload_json ->> 'title', '')) like '%junior%'
                or lower(coalesce(raw_payload_json ->> 'title', '')) like '%débutant%'
                or lower(coalesce(raw_payload_json ->> 'description', '')) like '%débutant accepté%'
                or lower(coalesce(raw_payload_json ->> 'description', '')) like '%junior%'
                or lower(coalesce(raw_payload_json ->> 'description', '')) like '%0-2 ans%'
                or lower(coalesce(raw_payload_json ->> 'description', '')) like '%0 à 2 ans%'
                then 'junior'
            when lower(coalesce(raw_payload_json ->> 'title', '')) like '%senior%'
                or lower(coalesce(raw_payload_json ->> 'title', '')) like '%lead%'
                or lower(coalesce(raw_payload_json ->> 'title', '')) like '%principal%'
                or lower(coalesce(raw_payload_json ->> 'description', '')) like '%senior%'
                or lower(coalesce(raw_payload_json ->> 'description', '')) like '%5 ans%'
                or lower(coalesce(raw_payload_json ->> 'description', '')) like '%6 ans%'
                or lower(coalesce(raw_payload_json ->> 'description', '')) like '%7 ans%'
                then 'senior'
            else 'unknown'
        end as seniority_level,

        nullif(trim(raw_payload_json ->> 'description'), '') as description_text,

        case
            when nullif(trim(raw_payload_json ->> 'created'), '') ~ '^\d{4}-\d{2}-\d{2}'
                then (raw_payload_json ->> 'created')::timestamptz
            else null::timestamptz
        end as published_at,

        null::timestamptz as updated_at,

        ingested_at::timestamptz as retrieved_at,

        nullif(trim(raw_payload_json ->> 'redirect_url'), '') as source_url,

        payload_hash

    from source

),

final as (

    select
        batch_id,
        request_id,
        raw_job_posting_id,
        source_name,
        source_job_id,
        source_job_key,
        search_scope_key,
        job_title,
        company_name,
        location_raw,
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
        payload_hash
    from parsed

)

select *
from final
