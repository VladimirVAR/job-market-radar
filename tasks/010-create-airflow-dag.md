# Task 010: Create Airflow DAG

## Goal

Create an Airflow DAG that orchestrates the end-to-end MVP pipeline.

Airflow should coordinate tasks, not perform business transformations.

---

## Context

The required pipeline flow is:

```text
start
  -> create_load_batch_and_ingest_france_travail
  -> dbt_build
  -> run_data_quality_checks
  -> generate_weekly_report
  -> end
```

---

## Deliverables

Create:

```text
dags/job_market_radar_dag.py
```

---

## Required Tasks

The DAG should include:

```text
start
create_load_batch_and_ingest_france_travail
dbt_build
run_data_quality_checks
generate_weekly_report
end
```

---

## Commands

Expected commands:

```bash
python -m src.pipeline.run_france_travail_ingestion
dbt build --project-dir dbt_job_market_radar
python -m src.pipeline.run_data_quality_checks
python -m src.reporting.generate_weekly_markdown_report
```

---

## Acceptance Criteria

- DAG is visible in Airflow.
- Task dependencies are correct.
- Ingestion task runs before dbt.
- dbt task runs before validation.
- Validation runs before report generation.
- DAG does not contain transformation SQL.
- DAG does not contain dashboard logic.
- DAG can be triggered manually.

---

## Implementation Notes

Keep the DAG simple.

Do not add complex dynamic task generation in MVP unless needed.

Use environment variables for paths and configuration where useful.

---

## Dependencies

Task 009.

---

## Next Task

Task 011: Create Streamlit Dashboard.
