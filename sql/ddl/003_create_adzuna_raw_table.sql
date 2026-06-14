-- ============================================================
-- Job Market Radar
-- File: sql/ddl/003_create_adzuna_raw_table.sql
--
-- Purpose:
--   Create raw-layer table for Adzuna job posting payloads.
--   Structure mirrors raw_france_travail_job_postings.
--   Business parsing belongs to staging/dbt models.
-- ============================================================


-- ============================================================
-- Table: raw.raw_adzuna_job_postings
-- Grain:
--   One raw job posting payload per source job per request per batch.
-- ============================================================

create table if not exists raw.raw_adzuna_job_postings (
    raw_job_posting_id uuid primary key default gen_random_uuid(),

    batch_id uuid not null,
    request_id uuid not null,

    source_name text not null default 'adzuna',
    source_job_id text not null,
    source_job_key text not null,
    search_scope_key text not null,

    raw_payload_json jsonb not null,
    payload_hash text not null,

    ingested_at timestamp with time zone not null default current_timestamp,
    created_at timestamp with time zone not null default current_timestamp,

    constraint fk_raw_adzuna_job_postings_batch
        foreign key (batch_id)
        references raw.raw_load_batches (batch_id),

    constraint fk_raw_adzuna_job_postings_request
        foreign key (request_id)
        references raw.raw_api_requests (request_id),

    constraint chk_raw_adzuna_job_postings_payload_is_object
        check (jsonb_typeof(raw_payload_json) = 'object')
);


-- ============================================================
-- Indexes: raw.raw_adzuna_job_postings
-- ============================================================

create index if not exists idx_raw_adzuna_job_postings_batch_id
    on raw.raw_adzuna_job_postings (batch_id);

create index if not exists idx_raw_adzuna_job_postings_request_id
    on raw.raw_adzuna_job_postings (request_id);

create index if not exists idx_raw_adzuna_job_postings_source_job_key
    on raw.raw_adzuna_job_postings (source_job_key);

create index if not exists idx_raw_adzuna_job_postings_search_scope_key
    on raw.raw_adzuna_job_postings (search_scope_key);

create index if not exists idx_raw_adzuna_job_postings_payload_hash
    on raw.raw_adzuna_job_postings (payload_hash);
