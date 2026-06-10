# Candidate Fit Score v1

## Purpose

Candidate Fit Score v1 helps Job Market Radar answer:

```text
Which jobs are most relevant for this candidate, and why?
```

The score ranks current job postings against Candidate Profile v1 and exposes a short explanation that can be shown in Streamlit.

## What the score means

Candidate Fit Score is an explainable first-pass prioritization signal.

It helps separate jobs into practical categories:

- strong roles to review first;
- good candidate matches;
- stretch opportunities;
- learning signals;
- low-priority jobs.

## What the score does not mean

Candidate Fit Score is not:

- a machine learning recommendation model;
- a guarantee that the candidate should apply;
- a guarantee that the candidate will be selected;
- a complete judgment of job quality;
- a replacement for manual review.

It is a deterministic MVP scoring layer built to make the dashboard more useful and explainable.

## Why the score is rule-based

The MVP uses rule-based scoring because it is:

- transparent;
- easy to validate;
- easy to explain during technical review;
- deterministic across runs;
- realistic for a one-person local MVP.

This is consistent with the broader MVP design: prefer simple, explicit, maintainable logic before adding advanced NLP or ML.

## Scoring dimensions

Candidate Fit Score v1 is calculated in the dbt mart layer using component scores:

```text
role_fit_score
skill_fit_score
seniority_fit_score
contract_fit_score
location_fit_score
growth_value_score
negative_signal_penalty
```

The final score is bounded between 0 and 100.

Conceptually:

```text
candidate_fit_score =
  role fit
  + skill fit
  + seniority fit
  + contract fit
  + location fit
  + growth value
  - negative signals
```

Streamlit does not calculate this formula. It only reads the resulting fields from `marts.mart_relevant_jobs`.

## Score bands

Accepted `candidate_fit_band` values:

| Band | Meaning |
|---|---|
| `strong_match` | Strong match for the current candidate profile |
| `good_match` | Good match worth reviewing |
| `possible_match` | Possible fit with some uncertainty |
| `weak_match` | Weak fit, usually lower priority |
| `low_priority` | Poor fit for current candidate goals |

## Application priority labels

Accepted `application_priority` values:

| Priority | Interpretation |
|---|---|
| `apply_now` | Strong target role, high fit, no obvious seniority risk |
| `good_candidate` | Good opportunity worth reviewing |
| `stretch_opportunity` | Potentially useful but includes risk or gaps |
| `learning_signal` | Useful mostly for learning-market insight |
| `low_priority` | Not a good target for the current profile |

## Example interpretations

### `apply_now`

The job is probably a strong target for the current profile. It likely contains relevant Data Engineering / ETL / Analytics Engineering signals, candidate skill matches, and no strong seniority risk.

### `good_candidate`

The job is useful and should be reviewed, but may have weaker role fit, fewer matched skills, or some uncertainty.

### `stretch_opportunity`

The job may be worth manual review even if it has seniority risk, missing growth skills, or a slightly broader role definition.

### `learning_signal`

The job is not necessarily a good application target, but it contains useful market signals such as Spark, Kafka, Snowflake, BigQuery, cloud, Terraform, Kubernetes, or CI/CD.

### `low_priority`

The job does not currently look useful enough for the candidate's immediate job-search priorities.

## Known limitations

- The score is rule-based, not ML-based.
- It depends on job title and description quality.
- French and English keyword coverage is useful but incomplete.
- Skill extraction may miss synonyms or implicit requirements.
- Growth skill extraction is incomplete in the MVP.
- Candidate Profile v1 is hardcoded for the MVP.
- There is no UI profile editor yet.
- There is no multi-user support.

## Future improvements

- Configurable candidate profile.
- Better skill taxonomy.
- Better NLP or semantic matching.
- Candidate-specific weights.
- Historical score tracking.
- Multi-source comparison.
- Score tuning after reviewing real application outcomes.
