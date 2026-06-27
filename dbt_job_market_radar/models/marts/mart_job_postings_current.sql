{{ config(materialized='view') }}

-- Grain: one row per source_job_key / canonical_job_key in the current warehouse state.
-- Purpose: dashboard-ready job posting list with simple MVP relevance and junior-friendly signals.
-- MVP simplification: skills are detected with transparent rule-based matching from title + description.

with current_jobs as (

    select
        canonical_job_key,
        source_job_key,
        source_name,
        latest_batch_id,
        first_seen_at,
        last_seen_at,
        coalesce(is_current_version, true) as is_active,
        missing_since_batch_id,
        job_title,
        normalized_job_title,
        company_name,
        company_key,
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
        source_url,
        payload_hash,
        lower(
            coalesce(job_title, '') || ' ' ||
            coalesce(normalized_job_title, '') || ' ' ||
            coalesce(description_text, '')
        ) as searchable_text
    from {{ ref('wh_job_posting_current') }}

),

skill_flags as (

    select
        *,
        (searchable_text ~* '(^|[^a-z0-9])python([^a-z0-9]|$)') as has_python,
        (searchable_text ~* '(^|[^a-z0-9])sql([^a-z0-9]|$)') as has_sql,
        (searchable_text ~* 'postgres|postgresql') as has_postgresql,
        (searchable_text ~* '(^|[^a-z0-9])dbt([^a-z0-9]|$)') as has_dbt,
        (searchable_text ~* 'airflow') as has_airflow,
        (searchable_text ~* 'docker') as has_docker,
        (searchable_text ~* '(^|[^a-z0-9])(aws|amazon web services)([^a-z0-9]|$)') as has_aws,
        (searchable_text ~* 'spark|pyspark') as has_spark,
        (searchable_text ~* 'snowflake') as has_snowflake,
        (searchable_text ~* 'bigquery|big query') as has_bigquery,
        (searchable_text ~* 'data[ -]?warehouse|data warehousing|(^|[^a-z0-9])dwh([^a-z0-9]|$)') as has_data_warehouse,
        (searchable_text ~* '(^|[^a-z0-9])etl([^a-z0-9]|$)') as has_etl,
        (searchable_text ~* '(^|[^a-z0-9])elt([^a-z0-9]|$)') as has_elt,
        (searchable_text ~* '(^|[^a-z0-9])(power\s*bi|powerbi)([^a-z0-9]|$)') as has_power_bi,
        (searchable_text ~* '(^|[^a-z0-9])azure([^a-z0-9]|$)') as has_azure,
        (searchable_text ~* '(^|[^a-z0-9])gcp([^a-z0-9]|$)|google cloud') as has_gcp
    from current_jobs

),

skill_arrays as (

    select
        *,
        array_remove(array[
            case when has_python then 'python' end,
            case when has_sql then 'sql' end,
            case when has_postgresql then 'postgresql' end,
            case when has_dbt then 'dbt' end,
            case when has_airflow then 'airflow' end,
            case when has_docker then 'docker' end,
            case when has_aws then 'aws' end,
            case when has_data_warehouse then 'data warehouse' end,
            case when has_etl then 'etl' end,
            case when has_elt then 'elt' end,
            case when has_power_bi then 'power_bi' end
        ], null) as matched_candidate_skills,
        array_remove(array[
            case when has_spark then 'spark' end,
            case when has_snowflake then 'snowflake' end,
            case when has_bigquery then 'bigquery' end,
            case when has_azure then 'azure' end,
            case when has_gcp then 'gcp' end
        ], null) as missing_growth_skills,
        array_remove(array[
            case when has_python then 'python' end,
            case when has_sql then 'sql' end,
            case when has_postgresql then 'postgresql' end,
            case when has_dbt then 'dbt' end,
            case when has_airflow then 'airflow' end,
            case when has_docker then 'docker' end,
            case when has_aws then 'aws' end,
            case when has_spark then 'spark' end,
            case when has_snowflake then 'snowflake' end,
            case when has_bigquery then 'bigquery' end,
            case when has_data_warehouse then 'data warehouse' end,
            case when has_etl then 'etl' end,
            case when has_elt then 'elt' end,
            case when has_power_bi then 'power_bi' end,
            case when has_azure then 'azure' end,
            case when has_gcp then 'gcp' end
        ], null) as detected_skills
    from skill_flags

),

scored as (

    select
        *,
        coalesce(array_length(matched_candidate_skills, 1), 0) as matched_candidate_skill_count,
        coalesce(array_length(missing_growth_skills, 1), 0) as missing_growth_skill_count,
        coalesce(array_length(detected_skills, 1), 0) as detected_skill_count,

        least(45, coalesce(array_length(matched_candidate_skills, 1), 0) * 8) as skill_match_score,

        case
            when searchable_text ~* 'data engineer|data engineering|ing[ée]nieur data|etl developer|développeur etl|analytics engineer|bi engineer' then 25
            when searchable_text ~* 'data analyst|analyste data|business intelligence|bi analyst' then 15
            when searchable_text ~* 'software engineer|developer|développeur' and searchable_text ~* 'data|sql|etl|warehouse' then 8
            else 0
        end as title_domain_score,

        case
            when coalesce(seniority_level, 'unknown') = 'junior' then 15
            when coalesce(seniority_level, 'unknown') = 'unknown' then 8
            when coalesce(seniority_level, 'unknown') = 'mid' then 5
            when coalesce(seniority_level, 'unknown') = 'senior' then 0
            else 5
        end as seniority_fit_score,

        case
            when coalesce(work_mode, 'unknown') in ('remote', 'hybrid') then 5
            when coalesce(work_mode, 'unknown') in ('onsite', 'unknown') then 3
            else 0
        end as work_context_score,

        case
            when coalesce(published_at::date, last_seen_at::date, first_seen_at::date) >= current_date - 7 then 10
            when coalesce(published_at::date, last_seen_at::date, first_seen_at::date) >= current_date - 14 then 7
            when coalesce(published_at::date, last_seen_at::date, first_seen_at::date) >= current_date - 30 then 4
            else 0
        end as recency_score,

        case
            when job_title is not null
             and company_name is not null
             and coalesce(city, region, country) is not null
             and source_url is not null then 10
            when job_title is not null
             and company_name is not null then 7
            when job_title is not null then 4
            else 0
        end as data_quality_score,

        case
            when searchable_text ~* 'senior|lead|principal|staff|architect|manager|expert|5\+ years|7\+ years|5 ans|7 ans' then 20
            when searchable_text ~* 'commercial|sales manager|waiter|serveur|technicien' and searchable_text !~* 'data|sql|etl|warehouse' then 30
            else 0
        end as hard_penalty_score,

        least(
            100,
            greatest(
                0,
                least(45, coalesce(array_length(matched_candidate_skills, 1), 0) * 8)
                + case
                    when searchable_text ~* 'data engineer|data engineering|ing[ée]nieur data|etl developer|développeur etl|analytics engineer|bi engineer' then 25
                    when searchable_text ~* 'data analyst|analyste data|business intelligence|bi analyst' then 15
                    when searchable_text ~* 'software engineer|developer|développeur' and searchable_text ~* 'data|sql|etl|warehouse' then 8
                    else 0
                  end
                + case
                    when coalesce(seniority_level, 'unknown') = 'junior' then 15
                    when coalesce(seniority_level, 'unknown') = 'unknown' then 8
                    when coalesce(seniority_level, 'unknown') = 'mid' then 5
                    when coalesce(seniority_level, 'unknown') = 'senior' then 0
                    else 5
                  end
                + case
                    when coalesce(work_mode, 'unknown') in ('remote', 'hybrid') then 5
                    when coalesce(work_mode, 'unknown') in ('onsite', 'unknown') then 3
                    else 0
                  end
                + case
                    when coalesce(published_at::date, last_seen_at::date, first_seen_at::date) >= current_date - 7 then 10
                    when coalesce(published_at::date, last_seen_at::date, first_seen_at::date) >= current_date - 14 then 7
                    when coalesce(published_at::date, last_seen_at::date, first_seen_at::date) >= current_date - 30 then 4
                    else 0
                  end
                + case
                    when job_title is not null
                     and company_name is not null
                     and coalesce(city, region, country) is not null
                     and source_url is not null then 10
                    when job_title is not null
                     and company_name is not null then 7
                    when job_title is not null then 4
                    else 0
                  end
                - case
                    when searchable_text ~* 'senior|lead|principal|staff|architect|manager|expert|5\+ years|7\+ years|5 ans|7 ans' then 20
                    when searchable_text ~* 'commercial|sales manager|waiter|serveur|technicien' and searchable_text !~* 'data|sql|etl|warehouse' then 30
                    else 0
                  end
            )
        ) as relevance_score,

        case
            when searchable_text ~* 'junior|entry[ -]?level|débutant|debutant|graduate|alternance|stage|trainee'
             and searchable_text !~* 'senior|lead|principal|staff|architect|expert|5\+ years|7\+ years|5 ans|7 ans'
                then true
            when coalesce(seniority_level, 'unknown') = 'junior'
             and searchable_text !~* 'senior|lead|principal|staff|architect|expert|5\+ years|7\+ years|5 ans|7 ans'
                then true
            else false
        end as is_junior_friendly
    from skill_arrays

)

select
    canonical_job_key,
    source_job_key,
    source_name,
    latest_batch_id,
    first_seen_at,
    last_seen_at,
    is_active,
    missing_since_batch_id,
    job_title,
    normalized_job_title,
    coalesce(nullif(company_name, ''), 'unknown') as company_name,
    company_key,
    location_key,
    coalesce(nullif(city, ''), 'unknown') as city,
    region,
    country,
    contract_type,
    work_mode,
    seniority_level,
    published_at,
    updated_at,
    source_url,
    source_url as job_url,
    payload_hash,
    detected_skills,
    matched_candidate_skills,
    missing_growth_skills,
    detected_skill_count,
    matched_candidate_skill_count,
    missing_growth_skill_count,
    skill_match_score,
    title_domain_score,
    seniority_fit_score,
    work_context_score,
    recency_score,
    data_quality_score,
    hard_penalty_score,
    relevance_score,
    case
        when relevance_score >= 80 then 'high_match'
        when relevance_score >= 60 then 'good_match'
        when relevance_score >= 40 then 'weak_match'
        else 'low_match'
    end as relevance_bucket,
    is_junior_friendly,
    concat_ws(
        '; ',
        case
            when matched_candidate_skill_count > 0
                then 'Matches candidate skills: ' || array_to_string(matched_candidate_skills, ', ')
            else 'No candidate skills detected'
        end,
        case
            when missing_growth_skill_count > 0
                then 'Growth skills mentioned: ' || array_to_string(missing_growth_skills, ', ')
        end,
        case
            when is_junior_friendly then 'Junior-friendly signal found'
        end,
        case
            when hard_penalty_score > 0 then 'Seniority or domain penalty applied'
        end
    ) as relevance_reason
from scored
