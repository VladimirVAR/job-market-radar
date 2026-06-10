{{ config(
    materialized='view',
    tags=['staging', 'france_travail']
) }}

with source as (

    select *
    from {{ source('raw', 'raw_france_travail_job_postings') }}

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

        nullif(trim(raw_payload_json ->> 'intitule'), '') as job_title,

        nullif(trim(raw_payload_json -> 'entreprise' ->> 'nom'), '') as company_name,

        nullif(
            trim(
                coalesce(
                    raw_payload_json -> 'lieuTravail' ->> 'libelle',
                    raw_payload_json -> 'lieuTravail' ->> 'commune',
                    raw_payload_json -> 'lieuTravail' ->> 'nomCommune'
                )
            ),
            ''
        ) as location_raw,

        nullif(
            trim(
                coalesce(
                    raw_payload_json -> 'lieuTravail' ->> 'commune',
                    raw_payload_json -> 'lieuTravail' ->> 'nomCommune',
                    case
                        when nullif(trim(raw_payload_json -> 'lieuTravail' ->> 'libelle'), '') ~ '^[0-9]{2,3}\s*-\s*'
                            then regexp_replace(
                                nullif(trim(raw_payload_json -> 'lieuTravail' ->> 'libelle'), ''),
                                '^[0-9]{2,3}\s*-\s*',
                                ''
                            )
                        else null
                    end
                )
            ),
            ''
        ) as city,

        null::text as region,

        coalesce(
            nullif(trim(raw_payload_json -> 'lieuTravail' ->> 'pays'), ''),
            'France'
        ) as country,

        nullif(
            upper(
                trim(
                    coalesce(
                        raw_payload_json ->> 'typeContrat',
                        raw_payload_json ->> 'typeContratLibelle'
                    )
                )
            ),
            ''
        ) as contract_type,

        case
            when lower(coalesce(raw_payload_json ->> 'teletravail', '')) like '%non%'
                or lower(coalesce(raw_payload_json ->> 'teletravail', '')) like '%pas de télétravail%'
                then 'on_site'
            when lower(coalesce(raw_payload_json ->> 'teletravail', '')) like '%total%'
                or lower(coalesce(raw_payload_json ->> 'teletravail', '')) like '%100%'
                or lower(coalesce(raw_payload_json ->> 'teletravail', '')) like '%full remote%'
                then 'remote'
            when lower(coalesce(raw_payload_json ->> 'teletravail', '')) like '%possible%'
                or lower(coalesce(raw_payload_json ->> 'teletravail', '')) like '%partiel%'
                or lower(coalesce(raw_payload_json ->> 'teletravail', '')) like '%hybride%'
                or lower(coalesce(raw_payload_json ->> 'teletravail', '')) like '%ponctuel%'
                then 'hybrid'
            else 'unknown'
        end as work_mode,

        case
            when lower(
                coalesce(
                    raw_payload_json ->> 'experienceLibelle',
                    raw_payload_json ->> 'experienceExige',
                    ''
                )
            ) like '%débutant%'
                or lower(
                    coalesce(
                        raw_payload_json ->> 'experienceLibelle',
                        raw_payload_json ->> 'experienceExige',
                        ''
                    )
                ) like '%junior%'
                or lower(
                    coalesce(
                        raw_payload_json ->> 'experienceLibelle',
                        raw_payload_json ->> 'experienceExige',
                        ''
                    )
                ) like '%0 an%'
                or lower(
                    coalesce(
                        raw_payload_json ->> 'experienceLibelle',
                        raw_payload_json ->> 'experienceExige',
                        ''
                    )
                ) like '%1 an%'
                then 'junior'
            when lower(
                coalesce(
                    raw_payload_json ->> 'experienceLibelle',
                    raw_payload_json ->> 'experienceExige',
                    ''
                )
            ) like '%senior%'
                or lower(
                    coalesce(
                        raw_payload_json ->> 'experienceLibelle',
                        raw_payload_json ->> 'experienceExige',
                        ''
                    )
                ) like '%5 an%'
                or lower(
                    coalesce(
                        raw_payload_json ->> 'experienceLibelle',
                        raw_payload_json ->> 'experienceExige',
                        ''
                    )
                ) like '%6 an%'
                or lower(
                    coalesce(
                        raw_payload_json ->> 'experienceLibelle',
                        raw_payload_json ->> 'experienceExige',
                        ''
                    )
                ) like '%7 an%'
                then 'senior'
            else 'unknown'
        end as seniority_level,

        nullif(trim(raw_payload_json ->> 'description'), '') as description_text,

        case
            when nullif(trim(raw_payload_json ->> 'dateCreation'), '') ~ '^\d{4}-\d{2}-\d{2}'
                then (raw_payload_json ->> 'dateCreation')::timestamptz
            else null::timestamptz
        end as published_at,

        case
            when nullif(trim(raw_payload_json ->> 'dateActualisation'), '') ~ '^\d{4}-\d{2}-\d{2}'
                then (raw_payload_json ->> 'dateActualisation')::timestamptz
            else null::timestamptz
        end as updated_at,

        ingested_at::timestamptz as retrieved_at,

        nullif(
            trim(
                coalesce(
                    raw_payload_json -> 'origineOffre' ->> 'urlOrigine',
                    raw_payload_json ->> 'urlOrigine',
                    raw_payload_json ->> 'url'
                )
            ),
            ''
        ) as source_url,

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
