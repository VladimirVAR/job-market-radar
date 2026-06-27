from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))
from db import first_existing_column, load_dataframe, show_empty_state  # noqa: E402


st.set_page_config(page_title="Overview | Job Market Radar", page_icon="📊", layout="wide")
st.title("📊 Overview")
st.caption("High-level market KPIs prepared by the marts layer.")

try:
    overview_df = load_dataframe("select * from marts.mart_job_market_overview")
    skill_df = load_dataframe("select * from marts.mart_skill_demand")
    location_df = load_dataframe("select * from marts.mart_location_activity")
except Exception as exc:
    st.error("Could not load Overview data from marts.")
    st.code(str(exc))
    st.stop()

if overview_df.empty:
    show_empty_state()
    st.stop()

row = overview_df.iloc[0]

metric_specs = [
    ("Tracked jobs", ["total_current_job_postings", "active_job_count", "total_active_jobs"]),
    ("Active jobs", ["active_job_count", "total_active_jobs"]),
    ("Relevant jobs", ["relevant_job_count"]),
    ("High-match jobs", ["high_match_job_count"]),
    ("Junior-friendly jobs", ["junior_friendly_job_count"]),
    ("Companies", ["distinct_companies"]),
    ("Locations", ["distinct_locations"]),
    ("Avg relevance", ["avg_relevance_score", "average_relevance_score"]),
]

cols = st.columns(4)
for index, (label, candidates) in enumerate(metric_specs):
    column = first_existing_column(overview_df, candidates)
    value = row[column] if column else "—"
    if isinstance(value, float):
        value = f"{value:.1f}"
    cols[index % 4].metric(label, value)

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Top demanded skills")
    if skill_df.empty:
        show_empty_state("No skill demand data available yet.")
    else:
        count_col = first_existing_column(skill_df, ["matching_job_count", "active_job_count", "job_count"])
        if "skill_name" in skill_df.columns and count_col:
            chart_df = (
                skill_df[["skill_name", count_col]]
                .dropna(subset=["skill_name"])
                .sort_values(count_col, ascending=False)
                .head(10)
                .set_index("skill_name")
            )
            st.bar_chart(chart_df)
        st.dataframe(skill_df.head(20), use_container_width=True, hide_index=True)

with right:
    st.subheader("Top locations")
    if location_df.empty:
        show_empty_state("No location activity data available yet.")
    else:
        count_col = first_existing_column(location_df, ["active_job_count", "job_count"])
        label_col = first_existing_column(location_df, ["location_name", "city", "region", "country"])
        if label_col and count_col:
            chart_df = (
                location_df[[label_col, count_col]]
                .dropna(subset=[label_col])
                .sort_values(count_col, ascending=False)
                .head(10)
                .set_index(label_col)
            )
            st.bar_chart(chart_df)
        st.dataframe(location_df.head(20), use_container_width=True, hide_index=True)
