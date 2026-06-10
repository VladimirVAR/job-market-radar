select *
from {{ ref('mart_job_postings_current') }}
where relevance_score < 0
   or relevance_score > 100
   or skill_match_score < 0
   or title_domain_score < 0
   or seniority_fit_score < 0
   or work_context_score < 0
   or recency_score < 0
   or data_quality_score < 0
   or hard_penalty_score < 0
   or matched_candidate_skill_count < 0
   or missing_growth_skill_count < 0
   or detected_skill_count < 0
