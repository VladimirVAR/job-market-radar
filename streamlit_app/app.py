from __future__ import annotations

import pandas as pd
import streamlit as st

from db import first_existing_column, load_dataframe, show_empty_state, test_connection


st.set_page_config(
    page_title="Job Market Radar",
    page_icon="📡",
    layout="wide",
)

st.title("📡 Job Market Radar")
st.caption(
    "Local Data Engineering dashboard. Streamlit reads dashboard-ready marts; "
    "dbt owns transformations, relevance scoring, and market metrics."
)

ok, message = test_connection()
if ok:
    st.success(message)
else:
    st.error("Could not connect to PostgreSQL.")
    st.code(message)
    st.stop()

st.divider()

try:
    overview_df = load_dataframe("select * from marts.mart_job_market_overview")
except Exception as exc:
    st.warning("Overview mart is not available yet.")
    st.code(str(exc))
    overview_df = pd.DataFrame()

if overview_df.empty:
    show_empty_state()
else:
    row = overview_df.iloc[0]
    metric_columns = st.columns(4)

    metric_map = [
        ("Active jobs", ["active_job_count", "total_active_jobs", "total_current_job_postings"]),
        ("Relevant jobs", ["relevant_job_count"]),
        ("Junior-friendly", ["junior_friendly_job_count"]),
        ("Avg relevance", ["avg_relevance_score", "average_relevance_score"]),
    ]

    for container, (label, candidates) in zip(metric_columns, metric_map):
        column = first_existing_column(overview_df, candidates)
        value = row[column] if column else "—"
        if isinstance(value, float):
            value = f"{value:.1f}"
        container.metric(label, value)

st.subheader("Dashboard pages")
st.write(
    "Use the sidebar to open the business pages: Relevant Jobs, Skill Radar, Locations, "
    "Companies, Weekly Report, and Data Freshness."
)

st.markdown(
    """
**Architecture boundary**

- Python loads raw API responses into PostgreSQL.
- dbt builds staging, warehouse, and marts.
- Streamlit displays marts only.
- Relevance score, skill extraction, missing skills, and weekly summaries are not calculated in Streamlit.
"""
)
