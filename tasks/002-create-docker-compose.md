# Task 002: Create Docker Compose

## Goal

Create a reproducible local environment using Docker and docker-compose.

The MVP must run locally with PostgreSQL and should be ready to support Airflow, dbt, and Streamlit.

---

## Context

The project uses PostgreSQL as the local analytical store.

Airflow, dbt, and Streamlit may run either in containers or locally depending on the final MVP implementation. The docker-compose setup should remain simple.

---

## Deliverables

Create:

```text
docker-compose.yml
.env.example
```

Minimum services:

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

If Airflow container setup becomes too heavy, document a local Airflow alternative and keep PostgreSQL in Docker.

---

## Required Environment Variables

Add to `.env.example`:

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

Do not commit a real `.env` file.

---

## PostgreSQL Requirements

The PostgreSQL service should:

- use a named volume
- expose port `5432`
- use variables from `.env`
- be compatible with Python and dbt connections

---

## Acceptance Criteria

- `docker-compose up` starts PostgreSQL successfully.
- PostgreSQL data persists across container restarts.
- `.env.example` contains all required variables with placeholder values.
- `.env` is included in `.gitignore`.
- No real credentials are committed.
- README or docs mention how to start the local environment.

---

## Implementation Notes

Keep the compose file simple.

Avoid Kubernetes, cloud services, or production-style deployment complexity.

---

## Dependencies

Task 001.

---

## Next Task

Task 003: Create Raw Schema.
