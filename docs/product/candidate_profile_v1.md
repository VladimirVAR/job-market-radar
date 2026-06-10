# Candidate Profile v1

## Purpose

Candidate Profile v1 defines the demo/product profile used by Job Market Radar to rank job postings for a specific early-career Data Engineering path.

This is not a private user profile system. It is a transparent MVP configuration used to make the product useful and explainable in a project demo.

## Target persona

Career-switching junior Data Engineer candidate in France / Europe.

The profile is designed for a candidate who already has a practical foundation in data engineering tools and wants to identify realistic first roles, adjacent opportunities, and useful growth signals.

## Current / target skills

Candidate Profile v1 treats the following as current or target skills:

```text
Python
SQL
PostgreSQL
Docker
dbt
Airflow
AWS basics
Data Engineering fundamentals
Data warehouse / ELT concepts
Data quality
```

These skills represent the profile that the MVP is trying to match against job descriptions.

## Growth skills

The following skills are tracked as growth skills:

```text
Spark
Kafka
Snowflake
BigQuery
Azure
GCP
Terraform
Kubernetes
CI/CD
```

A job mentioning growth skills can still be useful even if it is not an immediate application target. In the dashboard, this can appear as a stretch opportunity or learning signal.

## How this profile is used

The dbt mart layer uses Candidate Profile v1 to expose fields such as:

```text
candidate_fit_score
candidate_fit_band
application_priority
matched_candidate_skills
missing_growth_skills
candidate_fit_reason
```

Streamlit displays these fields but does not calculate them.

## Product boundaries

Candidate Profile v1 is:

- a fixed MVP profile;
- explainable;
- deterministic;
- suitable for a project demo;
- useful for first-pass job prioritization.

Candidate Profile v1 is not:

- a private user profile database;
- a multi-user personalization system;
- a machine learning profile embedding;
- a final decision engine for whether to apply.

## Future improvements

Possible next versions:

- configurable candidate profile file;
- UI profile editor;
- multiple candidate profiles;
- skill weights by priority;
- location and contract preferences;
- historical profile versioning;
- better skill taxonomy.
