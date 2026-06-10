# Task 013B — Project Plan Reconciliation & Clean Live Baseline

## Role

Documentation / Release Engineer.

## Goal

Synchronize the repository plan with the real implementation history and validate a clean live-data baseline.

## Current Context

The original plan had tasks 001–012. Implementation introduced 011A, 011B, 013, 013B, and 014.

Current status:

```text
Technical MVP foundation: complete
Live data validation: complete
Final public release polish: pending
```

Current sequence:

```text
001 -> 002 -> 003 -> 004 -> 005 -> 006 -> 007 -> 008 -> 009 -> 010 -> 011A -> 011B -> 012 -> 013 -> 013B -> 014
```

## Required Work

1. Commit Task 013 separately.
2. Add missing task files.
3. Update `backlog.md`.
4. Recreate Docker volumes.
5. Restore live runtime configuration.
6. Run clean live ingestion.
7. Run dbt build.
8. Run data quality checks.
9. Validate Streamlit.
10. Validate Airflow live run if available.
11. Create Task 013B report.

Important command boundary:

```bash
git add src/pipeline/run_data_quality_checks.py reports/task_execution/013-activate-live-france-travail-ingestion-report.md
git commit -m "Complete Task 013 live France Travail ingestion"
```

Clean baseline commands:

```bash
git status
docker compose down -v
docker compose up -d --build
docker compose ps -a
```

## Constraints

- Do not mix Task 013 and Task 013B in one commit.
- Do not commit `.env`.
- Do not commit secrets.
- Avoid code changes unless required for reproducibility.
- Do not create fake screenshots.
- Final screenshots belong mainly to Task 014.

## Deliverables

```text
tasks/README.md
tasks/011A-build-analytics-marts.md
tasks/011B-create-streamlit-dashboard.md
tasks/013-activate-live-france-travail-ingestion.md
tasks/013B-project-plan-reconciliation-and-clean-live-baseline.md
tasks/014-final-polish-public-release-readiness.md
backlog.md
reports/task_execution/013B-project-plan-reconciliation-and-clean-live-baseline-report.md
```

## Definition of Done

Task 013B is complete when the plan and backlog match the real roadmap, Docker was reset, clean live ingestion succeeds, dbt build succeeds, data quality passes, Streamlit renders clean live data, Airflow succeeds or failure is documented, and no secrets are committed.
