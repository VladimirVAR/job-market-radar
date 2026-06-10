-- ============================================================
-- Job Market Radar
-- Task 003: Create Raw Schema
-- File: sql/ddl/002_create_raw_tables.sql
--
-- Purpose:
--   Create raw-layer tables for:
--   - load batch tracking
--   - API request metadata tracking
--   - raw France Travail job posting payload preservation
--
-- Important:
--   Raw tables must not parse business fields such as job title,
--   company, contract type, or description. Business parsing belongs
--   to staging/dbt models.
-- ============================================================


-- ============================================================
-- Table: raw.raw_load_batches
-- Grain:
--   One row per pipeline execution.
-- ============================================================

create table if not exists raw.raw_load_batches (
    batch_id uuid primary key default gen_random_uuid(),

    source_name text not null,
    pipeline_name text not null,

    started_at timestamp with time zone not null,
    finished_at timestamp with time zone,

    status text not null default 'running',
    triggered_by text not null default 'manual',

    records_loaded integer not null default 0,
    requests_made integer not null default 0,

    error_message text,

    created_at timestamp with time zone not null default current_timestamp,

    constraint chk_raw_load_batches_status
        check (status in ('running', 'success', 'failed', 'partial_success')),

    constraint chk_raw_load_batches_records_loaded_non_negative
        check (records_loaded >= 0),

    constraint chk_raw_load_batches_requests_made_non_negative
        check (requests_made >= 0),

    constraint chk_raw_load_batches_finished_after_started
        check (finished_at is null or finished_at >= started_at)
);


-- ============================================================
-- Table: raw.raw_api_requests
-- Grain:
--   One row per API request, API page, or search parameter set.
-- ============================================================

create table if not exists raw.raw_api_requests (
    request_id uuid primary key default gen_random_uuid(),

    batch_id uuid not null,

    source_name text not null,
    endpoint text not null,
    http_method text not null default 'GET',
    request_url text,

    request_params_json jsonb not null default '{}'::jsonb,
    search_scope_key text not null,

    page_number integer,
    page_size integer,

    response_status_code integer,
    response_time_ms integer,
    response_headers_json jsonb not null default '{}'::jsonb,

    started_at timestamp with time zone not null,
    finished_at timestamp with time zone,

    error_message text,

    created_at timestamp with time zone not null default current_timestamp,

    constraint fk_raw_api_requests_batch
        foreign key (batch_id)
        references raw.raw_load_batches (batch_id),

    constraint chk_raw_api_requests_http_method
        check (http_method in ('GET', 'POST', 'PUT', 'PATCH', 'DELETE')),

    constraint chk_raw_api_requests_page_number_non_negative
        check (page_number is null or page_number >= 0),

    constraint chk_raw_api_requests_page_size_positive
        check (page_size is null or page_size > 0),

    constraint chk_raw_api_requests_response_status_code
        check (
            response_status_code is null
            or response_status_code between 100 and 599
        ),

    constraint chk_raw_api_requests_response_time_non_negative
        check (response_time_ms is null or response_time_ms >= 0),

    constraint chk_raw_api_requests_finished_after_started
        check (finished_at is null or finished_at >= started_at)
);


-- ============================================================
-- Table: raw.raw_france_travail_job_postings
-- Grain:
--   One raw job posting payload per source job per request per batch.
-- ============================================================

create table if not exists raw.raw_france_travail_job_postings (
    raw_job_posting_id uuid primary key default gen_random_uuid(),

    batch_id uuid not null,
    request_id uuid not null,

    source_name text not null default 'france_travail',
    source_job_id text not null,
    source_job_key text not null,
    search_scope_key text not null,

    raw_payload_json jsonb not null,
    payload_hash text not null,

    ingested_at timestamp with time zone not null default current_timestamp,
    created_at timestamp with time zone not null default current_timestamp,

    constraint fk_raw_france_travail_job_postings_batch
        foreign key (batch_id)
        references raw.raw_load_batches (batch_id),

    constraint fk_raw_france_travail_job_postings_request
        foreign key (request_id)
        references raw.raw_api_requests (request_id),

    constraint chk_raw_france_travail_job_postings_payload_is_object
        check (jsonb_typeof(raw_payload_json) = 'object')
);


-- ============================================================
-- Indexes: raw.raw_api_requests
-- ============================================================

create index if not exists idx_raw_api_requests_batch_id
    on raw.raw_api_requests (batch_id);

create index if not exists idx_raw_api_requests_search_scope_key
    on raw.raw_api_requests (search_scope_key);

create index if not exists idx_raw_api_requests_source_name
    on raw.raw_api_requests (source_name);

create index if not exists idx_raw_api_requests_response_status_code
    on raw.raw_api_requests (response_status_code);


-- ============================================================
-- Indexes: raw.raw_france_travail_job_postings
-- ============================================================

create index if not exists idx_raw_france_travail_job_postings_batch_id
    on raw.raw_france_travail_job_postings (batch_id);

create index if not exists idx_raw_france_travail_job_postings_request_id
    on raw.raw_france_travail_job_postings (request_id);

create index if not exists idx_raw_france_travail_job_postings_source_job_key
    on raw.raw_france_travail_job_postings (source_job_key);

create index if not exists idx_raw_france_travail_job_postings_search_scope_key
    on raw.raw_france_travail_job_postings (search_scope_key);

create index if not exists idx_raw_france_travail_job_postings_payload_hash
    on raw.raw_france_travail_job_postings (payload_hash);