SHELL := /bin/bash

.PHONY: help setup up down db-shell ingest dbt-debug dbt-build test streamlit

help:
	@echo "Available commands:"
	@echo "  make setup       - create local .env from .env.example if missing"
	@echo "  make up          - start local services"
	@echo "  make down        - stop local services"
	@echo "  make db-shell    - open psql shell in postgres container"
	@echo "  make ingest      - run France Travail raw ingestion"
	@echo "  make dbt-debug   - run dbt debug"
	@echo "  make dbt-build   - run dbt build"
	@echo "  make test        - run pytest"
	@echo "  make streamlit   - run Streamlit app"

setup:
	@if [ ! -f .env ]; then cp .env.example .env; echo ".env created from .env.example"; else echo ".env already exists"; fi

up:
	docker-compose up -d postgres

down:
	docker-compose down

db-shell:
	docker-compose exec postgres psql -U $$POSTGRES_USER -d $$POSTGRES_DB

ingest:
	python -m src.pipeline.run_france_travail_ingestion

dbt-debug:
	dbt debug --project-dir dbt_job_market_radar

dbt-build:
	dbt build --project-dir dbt_job_market_radar

test:
	pytest

streamlit:
	streamlit run streamlit_app/app.py
