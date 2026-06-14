-- Job Market Radar — Analytical Queries
-- Purpose: technical review SQL examples based only on marts.
-- Business pages must not query raw, staging, or warehouse models directly.

-- 1. Overview KPIs
select
    total_current_job_postings,
    active_job_count,
    relevant_job_count,
    high_match_job_count,
    junior_friendly_job_count,
    distinct_companies,
    distinct_locations,
    avg_relevance_score,
    latest_last_seen_at
from marts.mart_job_market_overview;

-- 2. Best matching active jobs for the candidate profile
select
    job_title,
    company_name,
    city,
    region,
    country,
    contract_type,
    work_mode,
    seniority_level,
    relevance_score,
    relevance_bucket,
    matched_candidate_skills,
    missing_growth_skills,
    relevance_reason,
    job_url
from marts.mart_relevant_jobs
where is_active = true
order by relevance_score desc, last_seen_at desc
limit 20;

-- 3. Junior-friendly opportunities
select
    job_title,
    company_name,
    city,
    contract_type,
    work_mode,
    relevance_score,
    matched_candidate_skills,
    missing_growth_skills,
    relevance_reason,
    job_url
from marts.mart_relevant_jobs
where is_active = true
  and is_junior_friendly = true
order by relevance_score desc, last_seen_at desc
limit 20;

-- 4. Top demanded skills in current active postings
select
    skill_name,
    skill_category,
    matching_job_count,
    total_job_count,
    share_of_jobs,
    last_seen_at
from marts.mart_skill_demand
where matching_job_count > 0
order by matching_job_count desc, skill_name
limit 15;

-- 5. Candidate growth / missing skills in relevant jobs
select
    skill_name,
    skill_category,
    job_count,
    share_of_relevant_jobs,
    avg_relevance_score,
    priority_level
from marts.mart_missing_skills
order by job_count desc, share_of_relevant_jobs desc, skill_name;

-- 6. Best locations by active job count and relevance
select
    location_name,
    job_count,
    share_of_jobs,
    distinct_companies,
    avg_relevance_score,
    junior_friendly_job_count,
    last_seen_at
from marts.mart_location_demand
order by job_count desc, avg_relevance_score desc;

-- 7. Most active companies
select
    company_name,
    job_count,
    relevant_job_count,
    junior_friendly_job_count,
    distinct_locations,
    avg_relevance_score,
    last_seen_at
from marts.mart_company_demand
order by job_count desc, relevant_job_count desc, company_name;

-- 8. Weekly market summary for dashboard/reporting
select
    week_start_date,
    week_end_date,
    total_active_jobs,
    new_jobs,
    relevant_job_count,
    high_match_job_count,
    junior_friendly_jobs,
    top_skills,
    top_missing_skills,
    top_locations,
    top_companies,
    has_enough_history,
    summary_text
from marts.mart_weekly_market_summary
order by week_start_date desc;

-- 9. Data freshness / latest successful load
select
    source_name,
    latest_successful_batch_id,
    latest_successful_batch_started_at,
    latest_successful_batch_finished_at,
    latest_records_loaded,
    latest_requests_made,
    current_job_count,
    snapshot_row_count,
    freshest_data_timestamp
from marts.mart_data_freshness
order by source_name;
