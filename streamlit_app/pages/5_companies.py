from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))
from db import first_existing_column, load_dataframe, show_empty_state  # noqa: E402


st.set_page_config(page_title="Companies | Job Market Radar", page_icon="🏢", layout="wide")
st.title("🏢 Companies")
st.caption("Company activity and relevance signals from marts.")

try:
    df = load_dataframe("select * from marts.mart_company_activity")
except Exception as exc:
    st.error("Could not load company activity from marts.mart_company_activity.")
    st.code(str(exc))
    st.stop()

if df.empty:
    show_empty_state()
    st.stop()

filtered = df.copy()

with st.sidebar:
    st.header("Filters")
    company_search = st.text_input("Company contains")
    if company_search and "company_name" in filtered.columns:
        filtered = filtered[filtered["company_name"].str.contains(company_search, case=False, na=False)]

    if "avg_relevance_score" in filtered.columns:
        min_relevance = st.slider("Minimum average relevance", 0, 100, 0, 5)
        filtered = filtered[filtered["avg_relevance_score"].fillna(0) >= min_relevance]

count_col = first_existing_column(filtered, ["active_job_count", "job_count", "relevant_job_count"])

if filtered.empty:
    show_empty_state("No companies match the selected filters.")
    st.stop()

left, right = st.columns(2)

with left:
    st.subheader("Most active companies")
    if "company_name" in filtered.columns and count_col:
        chart_df = (
            filtered[["company_name", count_col]]
            .dropna(subset=["company_name"])
            .sort_values(count_col, ascending=False)
            .head(20)
            .set_index("company_name")
        )
        st.bar_chart(chart_df)
    else:
        st.warning("Company chart requires company_name and a job count column.")

with right:
    st.subheader("Average relevance by company")
    if "company_name" in filtered.columns and "avg_relevance_score" in filtered.columns:
        relevance_df = (
            filtered[["company_name", "avg_relevance_score"]]
            .dropna(subset=["company_name"])
            .sort_values("avg_relevance_score", ascending=False)
            .head(20)
            .set_index("company_name")
        )
        st.bar_chart(relevance_df)
    else:
        st.info("Average relevance score is not available in this mart yet.")

st.subheader("Company activity table")
sort_col = count_col or "company_name" if "company_name" in filtered.columns else filtered.columns[0]
st.dataframe(filtered.sort_values(sort_col, ascending=False), use_container_width=True, hide_index=True)
