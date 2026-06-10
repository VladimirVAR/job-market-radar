{{ config(materialized='view') }}

-- Task 013C Part A
-- Grain: one current active job posting enriched with candidate-specific fit scoring.
-- Purpose: expose a transparent Candidate Fit Score v1 for Streamlit and downstream reports.
-- Important: Streamlit must display these fields only; it must not calculate candidate fit logic.

with base as (

    select
        canonical_job_key,
        source_job_key,
        source_name,
        job_title,
        normalized_job_title,
        company_name,
        city,
        region,
        country,
        contract_type,
        work_mode,
        seniority_level,
        source_url,
        job_url,
        published_at,
        first_seen_at,
        last_seen_at,
        detected_skills,
        matched_candidate_skills,
        missing_growth_skills,
        detected_skill_count as required_skills_count,
        matched_candidate_skill_count as matched_skills_count,
        missing_growth_skill_count,
        relevance_score,
        relevance_bucket,
        relevance_reason,
        is_junior_friendly,
        is_active,
        latest_batch_id,
        payload_hash
    from {{ ref('mart_job_postings_current') }}
    where coalesce(is_active, true) = true

),

normalized as (

    select
        *,
        lower(
            coalesce(job_title, '') || ' ' ||
            coalesce(normalized_job_title, '') || ' ' ||
            coalesce(contract_type, '') || ' ' ||
            coalesce(work_mode, '') || ' ' ||
            coalesce(city, '') || ' ' ||
            coalesce(region, '') || ' ' ||
            coalesce(country, '') || ' ' ||
            coalesce(seniority_level, '') || ' ' ||
            coalesce(relevance_reason, '') || ' ' ||
            coalesce(array_to_string(detected_skills, ' '), '') || ' ' ||
            coalesce(array_to_string(matched_candidate_skills, ' '), '') || ' ' ||
            coalesce(array_to_string(missing_growth_skills, ' '), '')
        ) as candidate_fit_text,
        coalesce(array_length(matched_candidate_skills, 1), 0) as matched_candidate_skills_count,
        coalesce(array_length(missing_growth_skills, 1), 0) as missing_growth_skills_count,
        coalesce(array_length(detected_skills, 1), 0) as detected_skills_count
    from base

),

signals as (

    select
        *,

        (
            candidate_fit_text ~* 'data[ -]?engineer|data engineering|ing[ée]nieur data|ingénieur data|etl developer|développeur etl|developpeur etl|data integration|analytics engineer|data pipeline|pipeline developer|data warehouse developer|warehouse developer|elt|etl|data warehouse|data warehousing'
            and candidate_fit_text !~* 'frontend|front-end|front end|react|angular|vue|mobile developer|ios developer|android developer|commercial|sales|business developer|account manager'
        ) as is_strong_target_role,

        (
            candidate_fit_text ~* 'bi developer|bi engineer|business intelligence|data analyst|analyste data|data analyst bi|sql developer|reporting engineer|analytics reporting|reporting analyst'
            and candidate_fit_text !~* 'frontend|front-end|front end|commercial|sales|account manager'
        ) as is_acceptable_adjacent_role,

        (
            candidate_fit_text ~* 'backend developer|back-end developer|front[- ]?end|frontend|full[- ]?stack|software engineer|développeur web|developpeur web|java developer|c# developer|\.net developer|mobile developer'
            and candidate_fit_text !~* 'data|sql|etl|elt|warehouse|analytics|bi'
        ) as has_low_priority_role_signal,

        (
            candidate_fit_text ~* 'junior|débutant|debutant|entry[ -]?level|0[ -]?[àa-][ -]?2 ans|0[ -]?2 years|première expérience|premiere experience|first experience|formation possible|reconversion|graduate|alternance|stage|trainee'
        ) as has_positive_junior_signal,

        (
            coalesce(seniority_level, 'unknown') = 'senior'
            or candidate_fit_text ~* 'senior|lead|principal|staff|architect|architecte|manager|expert|5\+ years|5 ans|7\+ years|7 ans|10\+ years|10 ans|minimum 5|minimum cinq'
        ) as is_seniority_risk,

        (
            coalesce(contract_type, '') ~* 'cdi|cdd|alternance|stage|internship|apprenticeship|graduate'
        ) as has_candidate_friendly_contract,

        (
            coalesce(contract_type, '') ~* 'freelance|ind[ée]pendant|independant|contractor|mission'
        ) as has_freelance_or_expert_contract,

        (
            coalesce(work_mode, '') ~* 'remote|hybrid|t[ée]l[ée]travail|teletravail'
            or coalesce(country, '') ~* 'france|french'
            or coalesce(region, '') is not null
            or coalesce(city, '') is not null
        ) as has_practical_location_fit,

        (coalesce(array_length(missing_growth_skills, 1), 0) > 0) as has_growth_skill_signal
    from normalized

),

components as (

    select
        *,

        case
            when is_strong_target_role then 25
            when is_acceptable_adjacent_role then 16
            when matched_candidate_skills_count >= 3 and candidate_fit_text ~* 'data|sql|etl|elt|warehouse|analytics|bi' then 10
            when candidate_fit_text ~* 'data|sql|etl|elt|warehouse|analytics|bi' then 6
            else 0
        end as role_fit_score,

        least(30, matched_candidate_skills_count * 5) as skill_fit_score,

        case
            when is_seniority_risk then 0
            when has_positive_junior_signal or coalesce(is_junior_friendly, false) then 20
            when coalesce(seniority_level, 'unknown') = 'junior' then 18
            when coalesce(seniority_level, 'unknown') = 'unknown' then 14
            when coalesce(seniority_level, 'unknown') = 'mid' then 8
            else 10
        end as seniority_fit_score,

        case
            when has_freelance_or_expert_contract then 0
            when has_candidate_friendly_contract then 10
            when coalesce(contract_type, '') = '' or coalesce(contract_type, 'unknown') = 'unknown' then 6
            else 5
        end as contract_fit_score,

        case
            when has_practical_location_fit then 5
            else 2
        end as location_fit_score,

        least(10, missing_growth_skills_count * 3) as growth_value_score,

        least(
            30,
            case when is_seniority_risk then 15 else 0 end
            + case when has_low_priority_role_signal then 12 else 0 end
            + case when has_freelance_or_expert_contract then 6 else 0 end
            + case when not is_strong_target_role and not is_acceptable_adjacent_role and matched_candidate_skills_count < 2 then 8 else 0 end
        ) as negative_signal_penalty
    from signals

),

scored as (

    select
        *,
        greatest(
            0,
            least(
                100,
                role_fit_score
                + skill_fit_score
                + seniority_fit_score
                + contract_fit_score
                + location_fit_score
                + growth_value_score
                - negative_signal_penalty
            )
        )::integer as candidate_fit_score
    from components

),

classified as (

    select
        *,

        case
            when candidate_fit_score >= 80 then 'strong_match'
            when candidate_fit_score >= 65 then 'good_match'
            when candidate_fit_score >= 50 then 'possible_match'
            when candidate_fit_score >= 35 then 'weak_match'
            else 'low_priority'
        end as candidate_fit_band,

        (
            candidate_fit_score >= 50
            and (is_seniority_risk or missing_growth_skills_count >= 2)
            and (is_strong_target_role or is_acceptable_adjacent_role or matched_candidate_skills_count >= 2)
        ) as is_stretch_opportunity,

        (
            has_growth_skill_signal
            and (
                candidate_fit_score < 65
                or is_seniority_risk
                or (not is_strong_target_role and not is_acceptable_adjacent_role)
            )
        ) as is_learning_signal
    from scored

),

prioritized as (

    select
        *,
        case
            when candidate_fit_score >= 80
             and is_seniority_risk = false
             and is_strong_target_role = true
                then 'apply_now'
            when candidate_fit_score >= 65
                then 'good_candidate'
            when is_stretch_opportunity
                then 'stretch_opportunity'
            when is_learning_signal
                then 'learning_signal'
            else 'low_priority'
        end as application_priority
    from classified

),

reasoned as (

    select
        *,
        array_remove(array[
            case when is_strong_target_role then 'target_role' end,
            case when is_acceptable_adjacent_role then 'acceptable_adjacent_role' end,
            case when matched_candidate_skills_count > 0 then 'candidate_skill_match' end,
            case when has_positive_junior_signal or coalesce(is_junior_friendly, false) then 'junior_friendly' end,
            case when has_practical_location_fit then 'remote_or_france_location' end,
            case when has_growth_skill_signal then 'growth_skill_signal' end,
            case when has_candidate_friendly_contract then 'candidate_friendly_contract' end
        ]::text[], null) as positive_reason_codes,

        array_remove(array[
            case when is_seniority_risk then 'seniority_risk' end,
            case when has_low_priority_role_signal then 'low_role_fit' end,
            case when matched_candidate_skills_count = 0 then 'missing_core_skills' end,
            case when has_freelance_or_expert_contract then 'freelance_or_expert_contract' end,
            case when not is_strong_target_role and not is_acceptable_adjacent_role then 'not_target_role' end
        ]::text[], null) as negative_reason_codes,

        coalesce(
            nullif(
                concat_ws(
                    '; ',
                    case
                        when application_priority = 'apply_now'
                            then 'Strong candidate fit: target Data Engineering role with good skill, seniority and practical-context alignment'
                        when application_priority = 'good_candidate'
                            then 'Good candidate fit: useful role and skill alignment, but manual review is recommended'
                        when application_priority = 'stretch_opportunity'
                            then 'Stretch opportunity: relevant signal exists, but seniority or growth-skill gaps require caution'
                        when application_priority = 'learning_signal'
                            then 'Learning signal: not the best application target now, but useful for tracking demanded growth skills'
                        else 'Low priority for the current candidate profile'
                    end,
                    case
                        when matched_candidate_skills_count > 0
                            then 'Matched candidate skills: ' || array_to_string(matched_candidate_skills, ', ')
                    end,
                    case
                        when missing_growth_skills_count > 0
                            then 'Growth skills mentioned: ' || array_to_string(missing_growth_skills, ', ')
                    end,
                    case
                        when is_seniority_risk
                            then 'Seniority risk detected'
                    end
                ),
                ''
            ),
            'Candidate fit could not be explained from available fields'
        ) as candidate_fit_reason
    from prioritized

)

select
    canonical_job_key,
    source_job_key,
    source_name,
    job_title,
    company_name,
    city,
    region,
    country,
    contract_type,
    work_mode,
    seniority_level,
    source_url,
    job_url,
    published_at,
    first_seen_at,
    last_seen_at,
    detected_skills,
    matched_candidate_skills,
    missing_growth_skills,
    required_skills_count,
    matched_skills_count,
    missing_growth_skill_count,

    relevance_score,
    relevance_bucket,
    relevance_reason,
    is_junior_friendly,

    role_fit_score,
    skill_fit_score,
    seniority_fit_score,
    contract_fit_score,
    location_fit_score,
    growth_value_score,
    negative_signal_penalty,
    candidate_fit_score,
    candidate_fit_band,
    application_priority,
    positive_reason_codes,
    negative_reason_codes,
    candidate_fit_reason,
    is_strong_target_role,
    is_acceptable_adjacent_role,
    is_seniority_risk,
    is_stretch_opportunity,
    is_learning_signal,

    is_active,
    latest_batch_id,
    payload_hash
from reasoned
