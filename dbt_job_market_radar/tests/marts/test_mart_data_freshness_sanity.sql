select *
from {{ ref('mart_data_freshness') }}
where coalesce(latest_records_loaded, 0) < 0
   or coalesce(latest_requests_made, 0) < 0
   or coalesce(latest_requests_recorded, 0) < 0
   or coalesce(current_job_count, 0) < 0
   or coalesce(current_row_count, 0) < 0
   or coalesce(snapshot_row_count, 0) < 0
