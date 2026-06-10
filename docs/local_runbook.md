# Local Runbook

## Purpose

This runbook explains how to run Job Market Radar locally from a clean checkout.

The commands below reflect the MVP repository structure and validated commands from previous tasks. If a command depends on whether a service runs locally or inside Docker, this is noted explicitly.

---

## 1. Prerequisites

Recommended tools:

- Python 3.10+
- Docker
- Docker Compose
- PostgreSQL client tools, optional but useful
- dbt with PostgreSQL adapter
- Airflow, if running the orchestration layer locally
- Streamlit

---

## 2. Clone the Repository

```bash
git clone <repository-url>
cd job-market-radar
```

Replace `<repository-url>` with the real GitHub repository URL.

---

## 3. Create Local Environment File

```bash
cp .env.example .env
```

Edit `.env` and configure local values.

Expected variables include:

```text
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=job_market_radar
POSTGRES_USER=job_market_radar
POSTGRES_PASSWORD=change_me

FRANCE_TRAVAIL_CLIENT_ID=your_client_id_here
FRANCE_TRAVAIL_CLIENT_SECRET=your_client_secret_here

AIRFLOW_UID=50000
```

Do not commit `.env`.

If running in sample mode, live France Travail credentials may not be required depending on the implementation configuration.

---

## 4. Install Python Dependencies

Recommended local setup:

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 5. Start Docker Services

Start local services:

```bash
docker compose up -d
```

At minimum, PostgreSQL should be available. Depending on the current `docker-compose.yml`, Airflow and Streamlit services may also be defined.

Check containers:

```bash
docker compose ps
```

---

## 6. Initialize Raw Database Objects

If the raw schema has not been created yet, run the SQL DDL files according to the repository setup.

Expected DDL files:

```text
sql/ddl/001_create_schemas.sql
sql/ddl/002_create_raw_tables.sql
```

Example command, to be verified against the local PostgreSQL configuration:

```bash
psql "$DATABASE_URL" -f sql/ddl/001_create_schemas.sql
psql "$DATABASE_URL" -f sql/ddl/002_create_raw_tables.sql
```

If the project provides a Makefile target for database setup, prefer the documented project target.

---

## 7. Run Ingestion Manually

Run France Travail / sample ingestion:

```bash
python -m src.pipeline.run_france_travail_ingestion
```

Expected result:

- one new row in `raw.raw_load_batches`
- request metadata in `raw.raw_api_requests`
- raw job payloads in `raw.raw_france_travail_job_postings`

---

## 8. Run dbt Parse / Build

Validate dbt project parsing:

```bash
dbt parse --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar
```

Run the full dbt build:

```bash
dbt build --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar
```

This builds:

- sources
- staging models
- warehouse models
- marts
- dbt tests

The full `dbt build` command above has been validated in previous tasks.

---

## 9. Run Data Quality Checks

Run the Python validation runner:

```bash
python -m src.pipeline.run_data_quality_checks
```

Expected result:

- validation checks pass
- failures are visible and actionable
- marts are confirmed ready enough for dashboard consumption

---

## 10. Run the Streamlit Dashboard

Run:

```bash
streamlit run streamlit_app/app.py
```

Open the local Streamlit URL shown in the terminal.

Expected pages:

- Overview
- Relevant Jobs
- Skill Radar
- Locations
- Companies
- Weekly Report
- Data Freshness

Business pages should read from `marts.*` only.

---

## 11. Run the Airflow DAG

The DAG id is expected to be:

```text
job_market_radar
```

Manual trigger command:

```bash
airflow dags trigger job_market_radar
```

If Airflow runs in Docker, use one of the following approaches depending on the current setup:

- trigger the DAG from the Airflow UI
- execute the command inside the Airflow container

Example, to be verified against service names in `docker-compose.yml`:

```bash
docker compose exec airflow-webserver airflow dags trigger job_market_radar
```

A full manual DAG run has been validated previously, with all tasks reaching success.

---

## 12. Recommended Full Local Validation Flow

Use this sequence for a local demo validation:

```bash
docker compose up -d
```

```bash
python -m src.pipeline.run_france_travail_ingestion
```

```bash
dbt build --project-dir dbt_job_market_radar --profiles-dir dbt_job_market_radar
```

```bash
python -m src.pipeline.run_data_quality_checks
```

```bash
streamlit run streamlit_app/app.py
```

Optional Airflow validation:

```bash
airflow dags trigger job_market_radar
```

---

## 13. Troubleshooting Notes

### PostgreSQL connection fails

Check:

- Docker container is running.
- `.env` values match dbt profile values.
- port `5432` is available.
- database user/password are correct.

### dbt cannot connect

Check:

- `dbt_job_market_radar/profiles.yml` or local profile exists.
- profile target points to the local PostgreSQL service.
- dbt PostgreSQL adapter is installed.

### Ingestion fails

Check:

- sample mode configuration if using local data.
- France Travail credentials if using live API mode.
- network availability.
- error messages in `raw.raw_load_batches` and `raw.raw_api_requests`.

### Dashboard is empty

Check:

- ingestion loaded records.
- `dbt build` succeeded.
- data quality checks passed.
- marts exist and are populated.
- Streamlit connection environment variables match PostgreSQL.

---

## 14. Demo Readiness Checklist

Before showing the project:

- [ ] Docker services are running.
- [ ] Latest ingestion completed.
- [ ] `dbt build` completed successfully.
- [ ] Data quality checks passed.
- [ ] Streamlit starts successfully.
- [ ] Data Freshness page shows the latest successful data.
- [ ] Known limitations are ready to explain honestly.
