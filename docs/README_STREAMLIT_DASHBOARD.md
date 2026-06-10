# Streamlit Dashboard Deliverable

Copy the `streamlit_app/` folder and `reports/task_execution/011B-create-streamlit-dashboard-report.md` into the Job Market Radar repository.

Run from repository root:

```bash
streamlit run streamlit_app/app.py
```

Expected environment variables:

```text
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=job_market_radar
POSTGRES_USER=job_market_radar
POSTGRES_PASSWORD=change_me
```

Inside Docker, `POSTGRES_HOST` may be `postgres`.
