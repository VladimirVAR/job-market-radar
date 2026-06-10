select *
from {{ ref('mart_relevant_jobs') }}
where candidate_fit_score < 0
   or candidate_fit_score > 100
   or role_fit_score < 0
   or role_fit_score > 25
   or skill_fit_score < 0
   or skill_fit_score > 30
   or seniority_fit_score < 0
   or seniority_fit_score > 20
   or contract_fit_score < 0
   or contract_fit_score > 10
   or location_fit_score < 0
   or location_fit_score > 5
   or growth_value_score < 0
   or growth_value_score > 10
   or negative_signal_penalty < 0
   or negative_signal_penalty > 30
   or candidate_fit_band not in ('strong_match', 'good_match', 'possible_match', 'weak_match', 'low_priority')
   or application_priority not in ('apply_now', 'good_candidate', 'stretch_opportunity', 'learning_signal', 'low_priority')
   or candidate_fit_reason is null
   or candidate_fit_reason = ''
