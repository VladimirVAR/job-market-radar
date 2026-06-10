# Job Market Radar Backlog

## Current Status

```text
Technical MVP foundation: complete
Live data validation: complete
Candidate-specific scoring: complete
Final public release polish: complete
MVP public release: ready
```

## Current Task Sequence

```text
001 -> 002 -> 003 -> 004 -> 005 -> 006 -> 007 -> 008 -> 009 -> 010 -> 011A -> 011B -> 012 -> 013 -> 013B -> 013C -> 014
```

## Phase Overview

| Phase | Task | Status | Summary |
|---|---|---|---|
| Phase 1 — Repository Foundation | 001 | Complete | Create repository structure |
| Phase 2 — Local Infrastructure | 002 | Complete | Create Docker Compose environment |
| Phase 3 — Raw Layer | 003 | Complete | Create raw schema |
| Phase 4 — Source Ingestion | 004 | Complete | Build France Travail API client |
| Phase 4 — Raw Loading | 005 | Complete | Load raw job postings |
| Phase 5 — dbt Foundation | 006 | Complete | Create dbt project |
| Phase 5 — Staging | 007 | Complete | Build staging models |
| Phase 5 — Warehouse | 008 | Complete | Build warehouse snapshots/current models |
| Phase 6 — Data Quality | 009 | Complete | Build validation checks |
| Phase 6 — Orchestration | 010 | Complete | Create Airflow DAG |
| Phase 7 — Analytics Marts | 011A | Complete | Build analytics marts |
| Phase 8 — Streamlit Dashboard | 011B | Complete | Create Streamlit dashboard |
| Phase 9 — Documentation / Demo | 012 | Complete | Write project documentation |
| Phase 10 — Live Data Validation | 013 | Complete | Activate live France Travail API ingestion |
| Phase 11 — Plan Reconciliation & Clean Baseline | 013B | Complete | Reconcile project plan and validate clean live baseline |
| Phase 12 — Candidate Fit Scoring | 013C | Complete | Define and implement Candidate Fit Score v1 in marts, Streamlit, validation, and documentation |
| Phase 13 — Final Polish / Public Release Readiness | 014 | Complete | Clean warnings, polish UI/docs, capture screenshots, and validate release state |

## Current Architecture

```text
France Travail / sample source
  -> raw PostgreSQL tables
  -> dbt staging models
  -> dbt warehouse models
  -> dbt marts
  -> data quality checks
  -> Airflow orchestration
  -> Streamlit dashboard
```

## Important Plan Reconciliation Notes

The original plan had a single Task 011.

During implementation, Task 011 was split into:

```text
011A — Build Analytics Marts
011B — Create Streamlit Dashboard
```

Reason:

```text
Streamlit must consume marts only.
```

Task 013 was added to validate live France Travail API ingestion.

Task 013B was added to reconcile the task plan, update the backlog, reset the local database, and validate a clean live-data baseline.

Task 013C was added to make the product candidate-specific. It introduced Candidate Fit Score v1 in dbt marts and updated Streamlit / documentation to answer:

```text
Which jobs are most relevant for this candidate, and why?
```

Task 014 completed final public release polish.

## Candidate Fit Score v1 Status

```text
Candidate-specific scoring: complete
Candidate Fit Score calculation in dbt marts: complete
Relevant Jobs Streamlit display: complete
Candidate Profile v1 documentation: complete
Scoring contract documentation: complete
Final public release polish: complete
```

Candidate Fit Score v1 is rule-based, explainable, and deterministic. It is not a machine learning recommendation model and should not be presented as one.

## Deferred / Future Improvements

Do not describe the following as fully implemented MVP warehouse deliverables unless they are later added and validated:

```text
warehouse.wh_skills
warehouse.wh_job_posting_skills
candidate profile version models
skill dictionary version models
advanced inactive job logic
```

Current MVP handles skill demand, relevance logic, and Candidate Fit Score v1 in marts using rule-based SQL.

## Future Roadmap

- Add Adzuna API.
- Add The Muse API.
- Improve skill extraction with NLP / semantic matching.
- Add historical trend tracking.
- Add richer relevance scoring.
- Add configurable candidate profiles.
- Add Candidate Fit Score historical tracking.
- Add skill dictionary versioning.
- Add cross-source job matching.
- Add CI checks.
- Add optional cloud deployment.
- Add automated screenshot/demo generation.
- Replace the Airflow weekly report placeholder with a fuller report generator.

## Next Step

```text
External GitHub review / public project walkthrough
```

Recommended non-MVP follow-ups:

- prepare a short project walkthrough;
- prepare a technical architecture walkthrough;
- optionally add CI checks;
- optionally replace the weekly report placeholder with a generated report artifact.
