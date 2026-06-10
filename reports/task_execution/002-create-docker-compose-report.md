# Task 002 Report — Create Docker Compose / Local MVP Environment

## 1. Task Summary

**Task:** Phase 2 — Repo skeleton / Local environment
**Task number:** 002
**Responsible role:** DevOps / Orchestration Engineer
**Goal:** Create a reproducible local environment using Docker and Docker Compose.

The task required creating a local MVP environment that can support:

```text
PostgreSQL
Airflow
dbt
Streamlit
.env-based configuration
local reproducibility
```

Required deliverables:

```text
docker-compose.yml
.env.example
```

Minimum required service:

```text
postgres
```

Recommended MVP services:

```text
postgres
airflow-webserver
airflow-scheduler
streamlit
```

The task also required PostgreSQL to use a named volume, expose port `5432`, use `.env` variables, and remain compatible with Python and dbt connections.

---

## 2. Final Status

**Status:** Completed for MVP local environment.

The environment was successfully started with:

```bash
docker compose up
```

The following services are running:

```text
job_market_radar_postgres
job_market_radar_airflow_postgres
job_market_radar_airflow_webserver
job_market_radar_airflow_scheduler
```

`docker compose ps` confirmed:

```text
job_market_radar_airflow_postgres   Up / healthy
job_market_radar_airflow_scheduler  Up
job_market_radar_airflow_webserver  Up
job_market_radar_postgres           Up / healthy
```

The Airflow UI is reachable at:

```text
http://localhost:8080
```

The project PostgreSQL database is exposed on:

```text
localhost:5432
```

Airflow command execution inside the container works:

```bash
docker compose exec airflow-webserver airflow dags list
```

Current output:

```text
No data found
```

This is expected because the Airflow DAG itself belongs to **Task 010 — Create Airflow DAG**, not Task 002.

---

## 3. Implemented Services

### 3.1 Project PostgreSQL

Service:

```text
postgres
```

Container:

```text
job_market_radar_postgres
```

Purpose:

```text
Main analytical PostgreSQL database for Job Market Radar.
```

Responsibilities:

```text
raw schema
staging schema
warehouse schema
marts schema
dbt target database
Streamlit data source
Python ingestion target
```

Port mapping:

```text
localhost:5432 -> container:5432
```

Named volume:

```text
postgres_data
```

This aligns with the accepted architecture decision to use PostgreSQL as the local analytical store because PostgreSQL runs easily in Docker, supports relational modeling, JSONB, Python, and dbt.

---

### 3.2 Airflow Metadata PostgreSQL

Service:

```text
airflow-postgres
```

Container:

```text
job_market_radar_airflow_postgres
```

Purpose:

```text
Internal Airflow metadata database.
```

Responsibilities:

```text
Airflow users
DAG runs
task instances
scheduler metadata
webserver metadata
Airflow internal tables
```

Named volume:

```text
airflow_postgres_data
```

Architectural note:

```text
Project data and Airflow metadata are intentionally separated.
```

This keeps the analytical database clean and avoids mixing orchestration metadata with product data.

---

### 3.3 Airflow Init

Service:

```text
airflow-init
```

Container:

```text
job_market_radar_airflow_init
```

Purpose:

```text
Initialize Airflow metadata database and create admin user.
```

Actions performed:

```text
airflow db migrate
airflow users create --username admin ...
```

Final result:

```text
airflow-init exited with code 0
```

This means the Airflow metadata database was migrated successfully and the admin user was created.

---

### 3.4 Airflow Webserver

Service:

```text
airflow-webserver
```

Container:

```text
job_market_radar_airflow_webserver
```

Purpose:

```text
Airflow UI.
```

Port mapping:

```text
localhost:8080 -> container:8080
```

Status:

```text
Running
```

Verified through browser:

```text
http://localhost:8080
```

Admin login works:

```text
username: admin
password: admin
```

---

### 3.5 Airflow Scheduler

Service:

```text
airflow-scheduler
```

Container:

```text
job_market_radar_airflow_scheduler
```

Purpose:

```text
Airflow scheduler for future DAG execution.
```

Status:

```text
Running
```

Current DAG list:

```text
No data found
```

This is expected until Task 010 creates the actual DAG.

---

### 3.6 Streamlit

Service:

```text
streamlit
```

Status:

```text
Configured but optional.
```

The service is placed behind a Docker Compose profile:

```text
dashboard
```

Expected future command:

```bash
docker compose --profile dashboard up streamlit
```

This is correct for Task 002 because Streamlit implementation belongs to a later task. The dashboard should eventually consume marts only, while Task 002 only prepares local infrastructure.

---

## 4. Environment Configuration

The environment uses:

```text
.env
.env.example
```

`.env.example` contains placeholder values for:

```text
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD

FRANCE_TRAVAIL_CLIENT_ID
FRANCE_TRAVAIL_CLIENT_SECRET

AIRFLOW_UID
AIRFLOW_IMAGE_NAME
AIRFLOW_WEBSERVER_PORT

AIRFLOW_POSTGRES_DB
AIRFLOW_POSTGRES_USER
AIRFLOW_POSTGRES_PASSWORD

AIRFLOW_ADMIN_USER
AIRFLOW_ADMIN_PASSWORD
AIRFLOW_ADMIN_FIRSTNAME
AIRFLOW_ADMIN_LASTNAME
AIRFLOW_ADMIN_EMAIL

AIRFLOW_PIP_REQUIREMENTS

STREAMLIT_PORT
```

Important note:

```text
.env.example should be committed.
.env should not be committed.
```

`.gitignore` includes:

```text
.env
```

So local credentials are excluded from Git.

Final Git commit status should still be checked with:

```bash
git status
```

---

## 5. Commands Verified

### 5.1 Clean shutdown and volume reset

After debugging, the environment was reset with:

```bash
docker compose down -v
```

The command removed containers, volumes, and the project network successfully after the YAML syntax issue was fixed.

---

### 5.2 Compose validation

The Docker Compose configuration was validated with:

```bash
docker compose config
```

The final config successfully rendered services including:

```text
airflow-init
airflow-postgres
airflow-scheduler
airflow-webserver
postgres
```

The rendered config also confirmed volume bindings for:

```text
./dags -> /opt/airflow/dags
. -> /opt/airflow/project
airflow_logs -> /opt/airflow/logs
```

Named volumes:

```text
airflow_logs
airflow_postgres_data
postgres_data
```

---

### 5.3 Environment startup

The environment was started with:

```bash
docker compose up
```

Docker created:

```text
job-market-radar_default network
job-market-radar_airflow_logs volume
job-market-radar_postgres_data volume
job-market-radar_airflow_postgres_data volume
job_market_radar_postgres container
job_market_radar_airflow_postgres container
job_market_radar_airflow_init container
job_market_radar_airflow_scheduler container
job_market_radar_airflow_webserver container
```

---

### 5.4 Airflow DAG list command

Command:

```bash
docker compose exec airflow-webserver airflow dags list
```

Result:

```text
No data found
```

Interpretation:

```text
Airflow is reachable and command execution works.
There are currently no DAGs because DAG creation is a later task.
```

---

## 6. Issues Encountered and Resolved

### 6.1 Initial Airflow init failure

Initial problem:

```text
airflow-init exited with code 2
```

Root cause:

```text
Invalid bash command formatting around `|| true`.
```

The first version of the `airflow-init` command used multiline Bash syntax that was not interpreted correctly inside Docker Compose.

Resolution:

```text
Simplified the `airflow-init` command into a valid bash -c command.
```

Result:

```text
airflow-init completed successfully with exit code 0.
```

---

### 6.2 YAML indentation error

Problem:

```text
failed to parse docker-compose.yml:
mapping key "container_name" already defined
```

Root cause:

```text
airflow-init was accidentally nested under airflow-postgres due to incorrect YAML indentation.
```

The broken structure made Docker Compose interpret `container_name` for `airflow-init` as a duplicate key inside the `airflow-postgres` service.

Resolution:

```text
Moved airflow-init back to the correct service indentation level.
```

After correction:

```bash
docker compose config
```

rendered successfully.

---

### 6.3 Port conflict investigation

A local diagnostic check was performed because the machine already had older Docker containers and WSL-based tooling.

Findings:

```text
Port 5432 is currently held by Docker backend for job_market_radar_postgres.
Port 8080 was free before Airflow webserver startup.
Old de_postgres container exists but is stopped.
Old de_postgres restart policy is `no`.
mini-de-pipeline postgres uses localhost:5433, so it does not conflict.
```

Conclusion:

```text
The actual failure was not caused by port conflict.
The failure was caused by Airflow init command syntax and later YAML indentation.
```

---

## 7. Current Known Warnings / Technical Debt

### 7.1 Airflow installs Python packages at container startup

Current configuration uses:

```text
_PIP_ADDITIONAL_REQUIREMENTS
```

with:

```text
dbt-postgres psycopg2-binary pandas requests python-dotenv
```

This works for MVP but is not ideal because dependencies are installed every time the container starts.

Observed warning:

```text
Adding requirements at container startup is fragile and is done every time the container starts.
```

Recommendation for later:

```text
Build a custom Airflow image with pinned dependencies.
```

Do not block Task 002 on this.

---

### 7.2 dbt version is not pinned

Current dependency:

```text
dbt-postgres
```

Because the version is not pinned, pip pulled a very recent dbt version:

```text
dbt-postgres 1.10.0
dbt-core 1.12.0b1
protobuf 6.33.6
```

This produced dependency warnings related to Google packages.

Recommendation:

```text
Pin dbt-postgres to a stable version before Task 006 or before the Airflow DAG starts running dbt commands.
```

Suggested future change:

```text
AIRFLOW_PIP_REQUIREMENTS=dbt-postgres==1.9.0 psycopg2-binary pandas requests python-dotenv
```

Current impact:

```text
Not blocking Task 002.
Airflow webserver and scheduler are running.
```

---

### 7.3 No DAGs visible yet

Current result:

```text
airflow dags list
No data found
```

This is expected.

Reason:

```text
Task 010 has not been implemented yet.
```

Task 010 is responsible for creating:

```text
dags/job_market_radar_dag.py
```

with the required orchestration flow:

```text
start
  -> create_load_batch_and_ingest_france_travail
  -> dbt_build
  -> run_data_quality_checks
  -> generate_weekly_report
  -> end
```

---

## 8. Acceptance Criteria Review

| Acceptance Criterion | Status | Notes |
|---|---:|---|
| `docker compose up` starts the environment | Passed | Environment starts successfully |
| PostgreSQL is reachable on `localhost:5432` | Passed | `job_market_radar_postgres` maps `5432:5432` |
| Airflow UI is reachable on `localhost:8080` | Passed | UI opened successfully |
| `airflow dags list` works inside Airflow container | Passed | Command works and returns `No data found` |
| `.env.example` exists with placeholders | Passed | File exists and contains required variables |
| `.env` is ignored by Git | Passed by file content | `.gitignore` contains `.env`; final `git status` still recommended |
| No cloud/Kubernetes complexity | Passed | Local Docker Compose only |
| PostgreSQL uses named volume | Passed | `postgres_data` volume |
| Airflow metadata DB uses named volume | Passed | `airflow_postgres_data` volume |
| Streamlit service prepared if useful | Passed / optional | Configured under dashboard profile |

---

## 9. Architecture Notes for Data Architect

### 9.1 Environment boundary

The local environment now separates:

```text
Project database
Airflow metadata database
Airflow orchestration runtime
Optional dashboard runtime
```

This supports clean separation of concerns.

---

### 9.2 Airflow responsibility

Airflow is prepared as an orchestration layer only.

It should later trigger:

```text
Python ingestion
dbt build
data quality checks
weekly report generation
```

Airflow should not contain transformation logic, business SQL, relevance scoring, or dashboard logic.

---

### 9.3 dbt responsibility

dbt is not yet implemented in this task, but the environment is prepared to support it.

The data flow expects dbt to own:

```text
staging
warehouse
marts
tests
documentation
lineage
```

---

### 9.4 PostgreSQL responsibility

The project PostgreSQL database is now available and ready for Task 003.

Task 003 should create:

```text
raw
staging
warehouse
marts
```

and raw tables:

```text
raw.raw_load_batches
raw.raw_api_requests
raw.raw_france_travail_job_postings
```

---

## 10. Final Decision

**Task 002 is accepted as complete for MVP.**

The local Docker Compose environment is running and ready for the next implementation task.

The remaining concerns are classified as non-blocking technical debt:

```text
Pin dbt dependency versions.
Consider custom Airflow image later.
Add README setup instructions.
Create actual Airflow DAG in Task 010.
```

---

## 11. Recommended Next Task

Proceed to:

```text
Task 003 — Create Raw Schema
```

Expected deliverables:

```text
sql/ddl/001_create_schemas.sql
sql/ddl/002_create_raw_tables.sql
```

Expected schemas:

```text
raw
staging
warehouse
marts
```

Expected raw tables:

```text
raw.raw_load_batches
raw.raw_api_requests
raw.raw_france_travail_job_postings
```

This is the correct next step because Task 002 prepared the local database, and now the project needs the raw database structure before ingestion can be implemented.
