from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))
from db import first_existing_column, load_dataframe, show_empty_state  # noqa: E402


st.set_page_config(page_title="Skill Radar | Job Market Radar", page_icon="🧭", layout="wide")
st.title("🧭 Skill Radar")
st.caption("Market skill demand and candidate growth skills prepared by dbt marts.")

try:
    demand_df = load_dataframe("select * from marts.mart_skill_demand")
    missing_df = load_dataframe("select * from marts.mart_missing_skills")
except Exception as exc:
    st.error("Could not load skill marts.")
    st.code(str(exc))
    st.stop()

left, right = st.columns(2)

with left:
    st.subheader("Most demanded skills")
    if demand_df.empty:
        show_empty_state("No skill demand data available yet.")
    else:
        filtered = demand_df.copy()
        if "skill_category" in filtered.columns:
            categories = sorted(filtered["skill_category"].dropna().unique().tolist())
            selected = st.multiselect("Skill category", categories)
            if selected:
                filtered = filtered[filtered["skill_category"].isin(selected)]

        count_col = first_existing_column(filtered, ["matching_job_count", "active_job_count", "job_count"])
        if "skill_name" in filtered.columns and count_col:
            chart_df = (
                filtered[["skill_name", count_col]]
                .dropna(subset=["skill_name"])
                .sort_values(count_col, ascending=False)
                .head(15)
                .set_index("skill_name")
            )
            st.bar_chart(chart_df)
        st.dataframe(filtered.sort_values(count_col, ascending=False) if count_col else filtered, use_container_width=True, hide_index=True)

with right:
    st.subheader("Missing / growth skills")
    if missing_df.empty:
        show_empty_state("No missing skill data available yet.")
    else:
        filtered_missing = missing_df.copy()
        if "priority_level" in filtered_missing.columns:
            priorities = sorted(filtered_missing["priority_level"].dropna().unique().tolist())
            selected_priorities = st.multiselect("Priority level", priorities)
            if selected_priorities:
                filtered_missing = filtered_missing[filtered_missing["priority_level"].isin(selected_priorities)]

        count_col = first_existing_column(filtered_missing, ["job_count", "relevant_job_count"])
        if "skill_name" in filtered_missing.columns and count_col:
            chart_df = (
                filtered_missing[["skill_name", count_col]]
                .dropna(subset=["skill_name"])
                .sort_values(count_col, ascending=False)
                .head(15)
                .set_index("skill_name")
            )
            st.bar_chart(chart_df)
        st.dataframe(filtered_missing.sort_values(count_col, ascending=False) if count_col else filtered_missing, use_container_width=True, hide_index=True)

st.info(
    "MVP note: skill extraction is rule-based and intentionally simple. "
    "This makes the results easy to explain during a project walkthrough."
)
