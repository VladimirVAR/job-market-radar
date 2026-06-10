# Task 001: Create Repository Structure

## Goal

Create the initial repository structure for the Job Market Radar project.

The structure should support a clean batch-oriented Data Engineering product with Python ingestion, PostgreSQL raw storage, dbt transformations, Airflow orchestration, Streamlit dashboard, and Markdown documentation.

---

## Context

The project architecture is:

```text
sources -> raw -> staging -> warehouse -> marts -> dashboard / reports
```

The repository should make component boundaries visible from the beginning.

---

## Deliverables

Create the following structure:

```text
job-market-radar/
  README.md
  docker-compose.yml
  .env.example
  .gitignore
  requirements.txt
  Makefile

  src/
    common/
      __init__.py
      config.py
      database.py
      logging.py
      hashing.py
      dates.py
      exceptions.py

    ingestion/
      __init__.py
      france_travail/
        __init__.py
        client.py
        auth.py
        request_builder.py
        parser.py

    loaders/
      __init__.py
      batch_loader.py
      request_loader.py
      raw_job_loader.py

    pipeline/
      __init__.py
      run_france_travail_ingestion.py

    reporting/
      __init__.py
      generate_weekly_markdown_report.py

  dags/
    job_market_radar_dag.py

  dbt_job_market_radar/
    README.md

  sql/
    ddl/
    analytics/

  streamlit_app/
    app.py
    db.py
    pages/

  docs/
    architecture/
      adr/

  data/
    sample/

  tasks/

  tests/
    unit/
    integration/
```

---

## Acceptance Criteria

- Repository has clear top-level folders.
- Python source code lives under `src/`.
- Airflow DAGs live under `dags/`.
- dbt project has its own folder.
- SQL DDL and showcase queries have separate folders.
- Streamlit app has its own folder.
- Documentation lives under `docs/`.
- Task specifications live under `tasks/`.
- Empty folders include `.gitkeep` if needed.
- No secrets are committed.

---

## Implementation Notes

Use English names and `snake_case`.

Do not create implementation-heavy files in this task. The goal is structure, not full logic.

---

## Dependencies

None.

---

## Next Task

Task 002: Create Docker Compose.
