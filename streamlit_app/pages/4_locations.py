from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))
from db import first_existing_column, load_dataframe, show_empty_state  # noqa: E402


st.set_page_config(page_title="Locations | Job Market Radar", page_icon="🗺️", layout="wide")
st.title("🗺️ Locations")
st.caption("Location activity from dashboard-ready marts.")

try:
    df = load_dataframe("select * from marts.mart_location_activity")
except Exception as exc:
    st.error("Could not load location activity from marts.mart_location_activity.")
    st.code(str(exc))
    st.stop()

if df.empty:
    show_empty_state()
    st.stop()

filtered = df.copy()

with st.sidebar:
    st.header("Filters")
    if "country" in filtered.columns:
        countries = sorted(filtered["country"].dropna().unique().tolist())
        selected_countries = st.multiselect("Country", countries)
        if selected_countries:
            filtered = filtered[filtered["country"].isin(selected_countries)]

    if "region" in filtered.columns:
        regions = sorted(filtered["region"].dropna().unique().tolist())
        selected_regions = st.multiselect("Region", regions)
        if selected_regions:
            filtered = filtered[filtered["region"].isin(selected_regions)]

count_col = first_existing_column(filtered, ["active_job_count", "job_count"])
label_col = first_existing_column(filtered, ["location_name", "city", "region", "country"])

if count_col:
    total_jobs = int(filtered[count_col].fillna(0).sum())
    st.metric("Active jobs in selected locations", total_jobs)

left, right = st.columns(2)

with left:
    st.subheader("Jobs by location")
    if label_col and count_col:
        chart_df = (
            filtered[[label_col, count_col]]
            .dropna(subset=[label_col])
            .sort_values(count_col, ascending=False)
            .head(20)
            .set_index(label_col)
        )
        st.bar_chart(chart_df)
    else:
        st.warning("Location chart requires a location label and job count column.")

with right:
    st.subheader("Average relevance by location")
    if label_col and "avg_relevance_score" in filtered.columns:
        relevance_df = (
            filtered[[label_col, "avg_relevance_score"]]
            .dropna(subset=[label_col])
            .sort_values("avg_relevance_score", ascending=False)
            .head(20)
            .set_index(label_col)
        )
        st.bar_chart(relevance_df)
    else:
        st.info("Average relevance score is not available in this mart yet.")

st.subheader("Location activity table")
sort_col = count_col or filtered.columns[0]
st.dataframe(filtered.sort_values(sort_col, ascending=False), use_container_width=True, hide_index=True)
