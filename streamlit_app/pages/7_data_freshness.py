from __future__ import annotations

import sys
from pathlib import Path
from uuid import UUID

import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))
from db import first_existing_column, load_dataframe, show_empty_state  # noqa: E402


st.set_page_config(page_title="Data Freshness | Job Market Radar", page_icon="✅", layout="wide")
st.title("✅ Data Freshness / Pipeline Status")
st.caption("Technical status exposed through marts.mart_data_freshness.")

try:
    df = load_dataframe("select * from marts.mart_data_freshness")
except Exception as exc:
    st.error("Could not load data freshness from marts.mart_data_freshness.")
    st.code(str(exc))
    st.stop()

if df.empty:
    show_empty_state("No freshness data available yet. Run the pipeline first.")
    st.stop()

row = df.iloc[0]

metric_specs = [
    ("Source", ["source_name"]),
    ("Latest batch", ["latest_successful_batch_id", "latest_batch_id", "batch_id"]),
    ("Records loaded", ["latest_records_loaded", "records_loaded"]),
    ("Requests made", ["latest_requests_made", "requests_made", "latest_requests_recorded"]),
    ("Current jobs", ["current_job_count"]),
    ("Snapshot rows", ["snapshot_row_count"]),
]

cols = st.columns(3)
for index, (label, candidates) in enumerate(metric_specs):
    column = first_existing_column(df, candidates)
    value = row[column] if column else "—"

    if value is None:
        display_value = "—"
    else:
        display_value = str(value)

    cols[index % 3].metric(label, display_value)

st.subheader("Latest timestamps")
timestamp_fields = [
    "latest_successful_batch_started_at",
    "latest_successful_batch_finished_at",
    "freshest_data_timestamp",
]
for field in timestamp_fields:
    if field in df.columns:
        st.write(f"**{field}:** {row[field]}")

status_col = first_existing_column(df, ["status", "latest_batch_status", "freshness_status"])
if status_col:
    status = str(row[status_col]).lower()
    if status in {"success", "fresh", "ok"}:
        st.success(f"Status: {row[status_col]}")
    elif status in {"warning", "stale", "partial_success"}:
        st.warning(f"Status: {row[status_col]}")
    else:
        st.error(f"Status: {row[status_col]}")

st.subheader("Freshness details")

display_df = df.copy()
for column in display_df.columns:
    display_df[column] = display_df[column].map(
        lambda value: str(value) if isinstance(value, UUID) else value
    )

st.dataframe(display_df, use_container_width=True, hide_index=True)