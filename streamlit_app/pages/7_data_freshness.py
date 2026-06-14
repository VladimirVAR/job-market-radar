from __future__ import annotations

import sys
from pathlib import Path
from uuid import UUID

import pandas as pd
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

display_df = df.copy()
for column in display_df.columns:
    display_df[column] = display_df[column].map(
        lambda value: str(value) if isinstance(value, UUID) else value
    )

source_col = first_existing_column(df, ["source_name"])
latest_records_col = first_existing_column(df, ["latest_records_loaded", "records_loaded"])
current_jobs_col = first_existing_column(df, ["current_job_count", "current_row_count"])
snapshot_rows_col = first_existing_column(df, ["snapshot_row_count"])
freshest_ts_col = first_existing_column(df, ["freshest_data_timestamp", "generated_at"])

st.subheader("Overall freshness")

metric_columns = st.columns(4)

source_count = df[source_col].nunique() if source_col else len(df)
metric_columns[0].metric("Sources", int(source_count))

if latest_records_col:
    latest_records_total = pd.to_numeric(df[latest_records_col], errors="coerce").fillna(0).sum()
    metric_columns[1].metric("Latest records loaded", int(latest_records_total))
else:
    metric_columns[1].metric("Latest records loaded", "—")

if current_jobs_col:
    current_jobs_total = pd.to_numeric(df[current_jobs_col], errors="coerce").fillna(0).sum()
    metric_columns[2].metric("Current jobs", int(current_jobs_total))
else:
    metric_columns[2].metric("Current jobs", "—")

if freshest_ts_col:
    freshest_timestamp = pd.to_datetime(df[freshest_ts_col], errors="coerce").max()
    metric_columns[3].metric(
        "Freshest data",
        "—" if pd.isna(freshest_timestamp) else str(freshest_timestamp),
    )
else:
    metric_columns[3].metric("Freshest data", "—")

st.divider()

st.subheader("Latest successful batch by source")

summary_columns = [
    "source_name",
    "latest_successful_batch_id",
    "latest_records_loaded",
    "latest_requests_made",
    "latest_requests_recorded",
    "current_job_count",
    "current_row_count",
    "snapshot_row_count",
    "latest_successful_batch_started_at",
    "latest_successful_batch_finished_at",
    "freshest_data_timestamp",
]

visible_columns = [column for column in summary_columns if column in display_df.columns]
st.dataframe(display_df[visible_columns], use_container_width=True, hide_index=True)

st.subheader("Per-source checks")

for _, row in display_df.sort_values(source_col if source_col else display_df.columns[0]).iterrows():
    source_name = row.get("source_name", "unknown_source")
    with st.expander(str(source_name), expanded=False):
        cols = st.columns(4)
        cols[0].metric("Latest records", row.get("latest_records_loaded", "—"))
        cols[1].metric("Requests made", row.get("latest_requests_made", "—"))
        cols[2].metric("Current jobs", row.get("current_job_count", row.get("current_row_count", "—")))
        cols[3].metric("Snapshot rows", row.get("snapshot_row_count", "—"))

        st.write("**Latest successful batch:**", row.get("latest_successful_batch_id", "—"))
        st.write("**Started at:**", row.get("latest_successful_batch_started_at", "—"))
        st.write("**Finished at:**", row.get("latest_successful_batch_finished_at", "—"))
        st.write("**Freshest data timestamp:**", row.get("freshest_data_timestamp", "—"))

st.subheader("Raw freshness mart output")
st.dataframe(display_df, use_container_width=True, hide_index=True)
