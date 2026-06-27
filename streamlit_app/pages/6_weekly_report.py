from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))
from db import format_list_like, load_dataframe, show_empty_state  # noqa: E402


st.set_page_config(page_title="Weekly Report | Job Market Radar", page_icon="🗓️", layout="wide")
st.title("🗓️ Weekly Report")
st.caption("Current weekly market summary from marts.mart_weekly_market_summary.")

try:
    df = load_dataframe("select * from marts.mart_weekly_market_summary")
except Exception as exc:
    st.error("Could not load weekly market summary from marts.mart_weekly_market_summary.")
    st.code(str(exc))
    st.stop()

if df.empty:
    show_empty_state()
    st.stop()

if "week_start_date" in df.columns:
    df = df.sort_values("week_start_date", ascending=False)

latest = df.iloc[0]

if "has_enough_history" in df.columns and not bool(latest.get("has_enough_history")):
    st.warning(
        "Historical week-over-week comparison is limited for now. "
        "This page shows the current-week MVP summary."
    )

metric_cols = st.columns(5)
metric_fields = [
    ("Active jobs", "total_active_jobs"),
    ("New jobs", "new_jobs"),
    ("Closed / missing", "closed_or_missing_jobs"),
    ("Junior-friendly", "junior_friendly_jobs"),
    ("Avg relevance", "avg_relevance_score"),
]
for container, (label, field) in zip(metric_cols, metric_fields):
    raw = latest[field] if field in df.columns else None
    if raw is None or (hasattr(raw, "__class__") and raw.__class__.__name__ == "NAType") or str(raw) in ("nan", "None", "<NA>"):
        value = "N/A"
    elif isinstance(raw, float):
        value = f"{raw:.1f}"
    else:
        value = raw
    container.metric(label, value)

st.divider()

left, middle, right = st.columns(3)
summary_fields = [
    (left, "Top skills", "top_skills"),
    (middle, "Top missing skills", "top_missing_skills"),
    (right, "Top companies", "top_companies"),
]
for container, title, field in summary_fields:
    with container:
        st.subheader(title)
        if field in df.columns:
            st.write(format_list_like(latest[field]))
        else:
            st.info("Not available yet.")

st.subheader("Weekly summary table")
st.dataframe(df, use_container_width=True, hide_index=True)
