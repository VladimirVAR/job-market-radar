# Task 008: Build Warehouse Snapshots

## Goal

Build warehouse models for job posting snapshots and current-state views.

The warehouse layer should support historical observations and latest job status.

---

## Context

Job postings can appear, change, disappear, and reappear.

The system needs both historical snapshots and current-state models.

---

## Deliverables

Create:

```text
dbt_job_market_radar/models/warehouse/wh_job_posting_snapshots.sql
dbt_job_market_radar/models/warehouse/wh_job_posting_current.sql
dbt_job_market_radar/models/warehouse/wh_job_posting_skills.sql
dbt_job_market_radar/models/warehouse/wh_skills.sql
dbt_job_market_radar/models/warehouse/wh_candidate_profile_versions.sql
dbt_job_market_radar/models/warehouse/wh_skill_dictionary_versions.sql
```

---

## Model: `wh_job_posting_snapshots`

**Grain:** one canonical job posting observation per source job per batch.

Required fields:

```text
job_snapshot_id
batch_id
source_name
source_job_id
source_job_key
canonical_job_key
search_scope_key
job_title
normalized_job_title
company_name
company_key
location_key
city
region
country
contract_type
work_mode
seniority_level
description_text
published_at
updated_at
retrieved_at
source_url
payload_hash
raw_job_posting_id
is_seen_in_batch
created_at
```

---

## Model: `wh_job_posting_current`

**Grain:** one row per latest known canonical job posting.

Required fields:

```text
canonical_job_key
source_name
source_job_key
latest_batch_id
first_seen_at
last_seen_at
is_active
missing_since_batch_id
job_title
normalized_job_title
company_name
company_key
location_key
city
region
country
contract_type
work_mode
seniority_level
description_text
published_at
updated_at
source_url
payload_hash
```

---

## MVP Key Strategy

For MVP:

```text
canonical_job_key = source_job_key
```

Future multi-source deduplication can improve this.

---

## Inactive Job Logic

A job should only be marked inactive if it is missing from a later batch with the same `search_scope_key`.

Do not mark a job inactive based on a different search scope.

---

## Acceptance Criteria

- `dbt build --select warehouse` succeeds.
- Snapshot model preserves `batch_id`, `raw_job_posting_id`, and `source_job_key`.
- Current model has one row per `canonical_job_key`.
- Current model uses the latest known snapshot.
- `first_seen_at <= last_seen_at`.
- Inactive logic is documented.
- Warehouse model grain is documented.

---

## Implementation Notes

Start simple.

Do not implement advanced cross-source matching in MVP.

---

## Dependencies

Task 007.

---

## Next Task

Task 009: Build Validation Checks.
