with scope_latest as (

    select distinct on (b.source_name, r.search_scope_key)
        b.source_name,
        r.search_scope_key,
        b.batch_id as latest_scope_batch_id
    from {{ source('raw', 'raw_load_batches') }} b
    join {{ source('raw', 'raw_api_requests') }} r on r.batch_id = b.batch_id
    where b.status = 'success'
    order by b.source_name, r.search_scope_key, b.started_at desc, b.batch_id desc

)

select j.canonical_job_key
from {{ ref('mart_job_postings_current') }} j
join {{ ref('wh_job_posting_current') }} w on w.canonical_job_key = j.canonical_job_key
left join scope_latest sl
    on sl.source_name = j.source_name
   and sl.search_scope_key = w.latest_search_scope_key
where j.is_active = true
  and sl.latest_scope_batch_id is not null
  and j.latest_batch_id <> sl.latest_scope_batch_id
