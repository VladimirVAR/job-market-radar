from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))
from db import (  # noqa: E402
    format_list_like,
    load_dataframe,
    prepare_display_dataframe,
    show_empty_state,
)


st.set_page_config(page_title="Relevant Jobs | Job Market Radar", page_icon="🎯", layout="wide")
st.title("🎯 Relevant Jobs")
st.caption(
    "Filter and explore current jobs ranked by Candidate Fit Score. "
    "Candidate fit is calculated upstream in dbt marts; Streamlit only displays it."
)

APPLICATION_PRIORITY_ORDER = [
    "apply_now",
    "good_candidate",
    "stretch_opportunity",
    "learning_signal",
    "low_priority",
]

CANDIDATE_FIT_BAND_ORDER = [
    "strong_match",
    "good_match",
    "possible_match",
    "weak_match",
    "low_priority",
]

APPLICATION_PRIORITY_LABELS = {
    "apply_now": "Apply now",
    "good_candidate": "Good candidate",
    "stretch_opportunity": "Stretch opportunity",
    "learning_signal": "Learning signal",
    "low_priority": "Low priority",
}

CANDIDATE_FIT_BAND_LABELS = {
    "strong_match": "Strong match",
    "good_match": "Good match",
    "possible_match": "Possible match",
    "weak_match": "Weak match",
    "low_priority": "Low priority",
}

CORE_CANDIDATE_FIT_COLUMNS = [
    "candidate_fit_score",
    "candidate_fit_band",
    "application_priority",
    "candidate_fit_reason",
]

MAIN_CANDIDATE_FIT_COLUMNS = [
    "application_priority",
    "candidate_fit_score",
    "candidate_fit_band",
    "job_title",
    "company_name",
    "city",
    "contract_type",
    "work_mode",
    "seniority_level",
    "source_url",
]

LEGACY_MAIN_COLUMNS = [
    "job_title",
    "company_name",
    "city",
    "contract_type",
    "work_mode",
    "seniority_level",
    "relevance_score",
    "relevance_bucket",
    "is_junior_friendly",
    "source_url",
]

DETAIL_COLUMNS = [
    "candidate_fit_reason",
    "matched_candidate_skills",
    "missing_growth_skills",
    "positive_reason_codes",
    "negative_reason_codes",
    "is_strong_target_role",
    "is_acceptable_adjacent_role",
    "is_seniority_risk",
    "is_stretch_opportunity",
    "is_learning_signal",
]

COMPONENT_SCORE_COLUMNS = [
    "role_fit_score",
    "skill_fit_score",
    "seniority_fit_score",
    "contract_fit_score",
    "location_fit_score",
    "growth_value_score",
    "negative_signal_penalty",
    "relevance_score",
]

LIST_LIKE_COLUMNS = [
    "matched_candidate_skills",
    "missing_growth_skills",
    "positive_reason_codes",
    "negative_reason_codes",
]

FRIENDLY_COLUMN_LABELS = {
    "application_priority": "Priority",
    "candidate_fit_score": "Candidate fit",
    "candidate_fit_band": "Fit band",
    "job_title": "Job title",
    "company_name": "Company",
    "city": "City",
    "contract_type": "Contract",
    "work_mode": "Work mode",
    "seniority_level": "Seniority",
    "source_url": "Job URL",
    "relevance_score": "Legacy relevance",
    "relevance_bucket": "Relevance bucket",
    "is_junior_friendly": "Junior-friendly",
}


@st.cache_data(show_spinner=False)
def load_relevant_jobs() -> pd.DataFrame:
    """Load dashboard-ready relevant jobs from the marts layer only."""
    return load_dataframe("select * from marts.mart_relevant_jobs")


def contains_text(value: Any, needle: str) -> bool:
    if not needle:
        return True
    if value is None:
        return False
    if isinstance(value, (list, tuple, set)):
        haystack = " ".join(str(item) for item in value)
    else:
        haystack = str(value)
    return needle.lower() in haystack.lower()


def ordered_values(values: list[Any], preferred_order: list[str]) -> list[str]:
    """Return known values in product order, then any extra values alphabetically."""
    cleaned = [str(value) for value in values if str(value).strip()]
    known = [value for value in preferred_order if value in cleaned]
    extras = sorted(value for value in set(cleaned) if value not in preferred_order)
    return known + extras


def build_text_search_mask(df: pd.DataFrame, columns: list[str], needle: str) -> pd.Series:
    mask = pd.Series(False, index=df.index)
    for column in columns:
        mask = mask | df[column].apply(lambda value: contains_text(value, needle))
    return mask


def format_label(value: Any, labels: dict[str, str]) -> str:
    if value is None or pd.isna(value):
        return ""
    return labels.get(str(value), str(value).replace("_", " ").title())


def add_readable_labels(display_df: pd.DataFrame) -> pd.DataFrame:
    """Return a display-only copy with user-friendly enum labels.

    The underlying mart values are left unchanged for filters, sorting, tests, and
    traceability. Only the Streamlit table labels are made friendlier.
    """
    readable_df = display_df.copy()
    if "application_priority" in readable_df.columns:
        readable_df["application_priority"] = readable_df["application_priority"].apply(
            lambda value: format_label(value, APPLICATION_PRIORITY_LABELS)
        )
    if "candidate_fit_band" in readable_df.columns:
        readable_df["candidate_fit_band"] = readable_df["candidate_fit_band"].apply(
            lambda value: format_label(value, CANDIDATE_FIT_BAND_LABELS)
        )
    return readable_df


def sort_jobs(df: pd.DataFrame, sort_by: str) -> pd.DataFrame:
    if sort_by == "Candidate fit score desc" and "candidate_fit_score" in df.columns:
        return df.sort_values(
            "candidate_fit_score",
            ascending=False,
            key=lambda series: pd.to_numeric(series, errors="coerce").fillna(-1),
        )
    if sort_by == "Relevance score desc" and "relevance_score" in df.columns:
        return df.sort_values(
            "relevance_score",
            ascending=False,
            key=lambda series: pd.to_numeric(series, errors="coerce").fillna(-1),
        )
    if sort_by == "Publication date desc" and "published_at" in df.columns:
        return df.sort_values(
            "published_at",
            ascending=False,
            key=lambda series: pd.to_datetime(series, errors="coerce"),
        )
    if sort_by == "Last seen desc" and "last_seen_at" in df.columns:
        return df.sort_values(
            "last_seen_at",
            ascending=False,
            key=lambda series: pd.to_datetime(series, errors="coerce"),
        )
    if sort_by == "Company A-Z" and "company_name" in df.columns:
        return df.sort_values("company_name", ascending=True)
    return df


def existing_columns(df: pd.DataFrame, columns: list[str]) -> list[str]:
    return [column for column in columns if column in df.columns]


def build_column_config(display_df: pd.DataFrame) -> dict[str, Any]:
    column_config: dict[str, Any] = {}

    for column, label in FRIENDLY_COLUMN_LABELS.items():
        if column in display_df.columns and column not in {"source_url", "candidate_fit_score", "relevance_score"}:
            column_config[column] = st.column_config.TextColumn(label)

    if "source_url" in display_df.columns:
        column_config["source_url"] = st.column_config.LinkColumn("Job URL", display_text="Open")
    if "candidate_fit_score" in display_df.columns:
        column_config["candidate_fit_score"] = st.column_config.ProgressColumn(
            "Candidate fit",
            min_value=0,
            max_value=100,
            format="%d",
            help="Calculated upstream in marts.mart_relevant_jobs.",
        )
    if "relevance_score" in display_df.columns:
        column_config["relevance_score"] = st.column_config.ProgressColumn(
            "Legacy relevance",
            min_value=0,
            max_value=100,
            format="%d",
            help="Existing relevance score kept for backwards compatibility.",
        )
    return column_config


def job_option_label(row: pd.Series) -> str:
    title = str(row.get("job_title", "Untitled job") or "Untitled job")
    company = str(row.get("company_name", "unknown company") or "unknown company")
    city = str(row.get("city", "unknown location") or "unknown location")
    score = row.get("candidate_fit_score", None)

    if pd.notna(score):
        try:
            score_text = f"{float(score):.0f}"
        except (TypeError, ValueError):
            score_text = str(score)
        return f"{score_text} · {title} · {company} · {city}"

    return f"{title} · {company} · {city}"


def show_candidate_fit_details(df: pd.DataFrame, candidate_fit_available: bool) -> None:
    """Show row-level Candidate Fit details without making the main table too wide."""
    if not candidate_fit_available:
        return

    with st.expander("Candidate Fit details", expanded=False):
        st.caption(
            "Select one job to inspect the explanation, matched skills, growth-skill gaps, "
            "reason codes, flags, and component scores prepared by the dbt mart."
        )

        detail_df = df.reset_index(drop=True)
        if detail_df.empty:
            st.info("No job details available for the current filters.")
            return

        option_map = {job_option_label(row): idx for idx, row in detail_df.iterrows()}
        selected_label = st.selectbox("Job to inspect", list(option_map.keys()))
        selected = detail_df.loc[option_map[selected_label]]

        if "candidate_fit_reason" in selected.index:
            st.markdown("**Why this job has this fit score**")
            st.write(str(selected["candidate_fit_reason"] or "No explanation available."))

        skill_cols = existing_columns(detail_df, ["matched_candidate_skills", "missing_growth_skills"])
        if skill_cols:
            left, right = st.columns(2)
            if "matched_candidate_skills" in skill_cols:
                left.markdown("**Matched candidate skills**")
                left.write(format_list_like(selected.get("matched_candidate_skills", "")) or "—")
            if "missing_growth_skills" in skill_cols:
                right.markdown("**Growth skills / gaps**")
                right.write(format_list_like(selected.get("missing_growth_skills", "")) or "—")

        reason_cols = existing_columns(detail_df, ["positive_reason_codes", "negative_reason_codes"])
        if reason_cols:
            left, right = st.columns(2)
            if "positive_reason_codes" in reason_cols:
                left.markdown("**Positive reason codes**")
                left.write(format_list_like(selected.get("positive_reason_codes", "")) or "—")
            if "negative_reason_codes" in reason_cols:
                right.markdown("**Risk / negative reason codes**")
                right.write(format_list_like(selected.get("negative_reason_codes", "")) or "—")

        flag_cols = existing_columns(
            detail_df,
            [
                "is_strong_target_role",
                "is_acceptable_adjacent_role",
                "is_seniority_risk",
                "is_stretch_opportunity",
                "is_learning_signal",
                "is_junior_friendly",
            ],
        )
        if flag_cols:
            flags = pd.DataFrame(
                {
                    "Signal": [column.replace("is_", "").replace("_", " ").title() for column in flag_cols],
                    "Value": [bool(selected.get(column, False)) for column in flag_cols],
                }
            )
            st.markdown("**Candidate fit flags**")
            st.dataframe(flags, hide_index=True, width="stretch")

        score_cols = existing_columns(detail_df, COMPONENT_SCORE_COLUMNS)
        if score_cols:
            scores = pd.DataFrame(
                {
                    "Component": [column.replace("_", " ").title() for column in score_cols],
                    "Score": [selected.get(column) for column in score_cols],
                }
            )
            st.markdown("**Component scores**")
            st.dataframe(scores, hide_index=True, width="stretch")


try:
    df = load_relevant_jobs()
except Exception as exc:
    st.error("Could not load relevant jobs from marts.mart_relevant_jobs.")
    st.code(str(exc))
    st.stop()

if df.empty:
    show_empty_state()
    st.stop()

candidate_fit_available = all(column in df.columns for column in CORE_CANDIDATE_FIT_COLUMNS)

if not candidate_fit_available:
    st.warning(
        "Candidate Fit fields are not available yet. Showing legacy relevance fields. "
        "Run the latest dbt mart build for Task 013C to enable Candidate Fit display."
    )

filtered = df.copy()

with st.sidebar:
    st.header("Filters")

    if "application_priority" in filtered.columns:
        priorities = ordered_values(
            filtered["application_priority"].dropna().unique().tolist(),
            APPLICATION_PRIORITY_ORDER,
        )
        selected_priorities = st.multiselect("Application priority", priorities)
        if selected_priorities:
            filtered = filtered[filtered["application_priority"].isin(selected_priorities)]

    if "candidate_fit_band" in filtered.columns:
        fit_bands = ordered_values(
            filtered["candidate_fit_band"].dropna().unique().tolist(),
            CANDIDATE_FIT_BAND_ORDER,
        )
        selected_fit_bands = st.multiselect("Candidate fit band", fit_bands)
        if selected_fit_bands:
            filtered = filtered[filtered["candidate_fit_band"].isin(selected_fit_bands)]

    if "candidate_fit_score" in filtered.columns:
        min_candidate_fit = st.slider("Minimum candidate fit score", 0, 100, 0, 5)
        filtered = filtered[
            pd.to_numeric(filtered["candidate_fit_score"], errors="coerce").fillna(0)
            >= min_candidate_fit
        ]
    elif "relevance_score" in filtered.columns:
        min_score = st.slider("Minimum relevance score", 0, 100, 0, 5)
        filtered = filtered[
            pd.to_numeric(filtered["relevance_score"], errors="coerce").fillna(0) >= min_score
        ]

    if "city" in filtered.columns:
        cities = sorted([x for x in filtered["city"].dropna().unique().tolist() if str(x).strip()])
        selected_cities = st.multiselect("City", cities)
        if selected_cities:
            filtered = filtered[filtered["city"].isin(selected_cities)]

    if "work_mode" in filtered.columns:
        work_modes = sorted([x for x in filtered["work_mode"].dropna().unique().tolist() if str(x).strip()])
        selected_work_modes = st.multiselect("Work mode", work_modes)
        if selected_work_modes:
            filtered = filtered[filtered["work_mode"].isin(selected_work_modes)]

    if "seniority_level" in filtered.columns:
        seniorities = sorted([x for x in filtered["seniority_level"].dropna().unique().tolist() if str(x).strip()])
        selected_seniorities = st.multiselect("Seniority", seniorities)
        if selected_seniorities:
            filtered = filtered[filtered["seniority_level"].isin(selected_seniorities)]

    if "contract_type" in filtered.columns:
        contracts = sorted([x for x in filtered["contract_type"].dropna().unique().tolist() if str(x).strip()])
        selected_contracts = st.multiselect("Contract type", contracts)
        if selected_contracts:
            filtered = filtered[filtered["contract_type"].isin(selected_contracts)]

    if "is_junior_friendly" in filtered.columns:
        junior_only = st.checkbox("Junior-friendly only", value=False)
        if junior_only:
            filtered = filtered[filtered["is_junior_friendly"].fillna(False).astype(bool)]

    skill_search = st.text_input("Skill contains", placeholder="Example: Python, dbt, Spark")
    if skill_search:
        skill_columns = [col for col in ["matched_candidate_skills", "missing_growth_skills"] if col in filtered.columns]
        if skill_columns:
            filtered = filtered[build_text_search_mask(filtered, skill_columns, skill_search)]

    sort_options = []
    if "candidate_fit_score" in filtered.columns:
        sort_options.append("Candidate fit score desc")
    if "relevance_score" in filtered.columns:
        sort_options.append("Relevance score desc")
    sort_options.extend(["Publication date desc", "Last seen desc", "Company A-Z"])
    sort_by = st.selectbox("Sort by", sort_options)

filtered = sort_jobs(filtered, sort_by)

metric_columns = st.columns(4)
metric_columns[0].metric("Jobs shown", len(filtered))

if "candidate_fit_score" in filtered.columns and not filtered.empty:
    avg_fit = pd.to_numeric(filtered["candidate_fit_score"], errors="coerce").mean()
    metric_columns[1].metric("Avg candidate fit", f"{avg_fit:.1f}" if pd.notna(avg_fit) else "—")
else:
    metric_columns[1].metric("Avg candidate fit", "—")

if "application_priority" in filtered.columns:
    apply_now_count = int((filtered["application_priority"] == "apply_now").sum())
    metric_columns[2].metric("Apply now", apply_now_count)
else:
    metric_columns[2].metric("Apply now", "—")

if "is_stretch_opportunity" in filtered.columns or "is_learning_signal" in filtered.columns:
    stretch_count = int(
        filtered.get("is_stretch_opportunity", pd.Series(False, index=filtered.index))
        .fillna(False)
        .astype(bool)
        .sum()
    )
    learning_count = int(
        filtered.get("is_learning_signal", pd.Series(False, index=filtered.index))
        .fillna(False)
        .astype(bool)
        .sum()
    )
    metric_columns[3].metric("Stretch / learning", f"{stretch_count} / {learning_count}")
else:
    metric_columns[3].metric("Stretch / learning", "—")

if filtered.empty:
    show_empty_state("No jobs match the selected filters.")
    st.stop()

preferred_columns = MAIN_CANDIDATE_FIT_COLUMNS if candidate_fit_available else LEGACY_MAIN_COLUMNS
visible_columns = existing_columns(filtered, preferred_columns)

display_df = add_readable_labels(
    prepare_display_dataframe(
        filtered[visible_columns],
        list_like_columns=LIST_LIKE_COLUMNS,
    )
)

st.subheader("Prioritized jobs")
st.caption(
    "The table keeps only high-signal fields for quick review. "
    "Use the details section below to inspect explanations, reason codes, flags, and component scores."
)

st.dataframe(
    display_df,
    width="stretch",
    hide_index=True,
    column_config=build_column_config(display_df),
)

show_candidate_fit_details(filtered, candidate_fit_available)

with st.expander("How to read Candidate Fit"):
    st.markdown(
        """
**Candidate Fit Score** is an explainable, rule-based prioritization signal prepared in the dbt mart layer.

- `apply_now`: strong target role with high candidate fit and no obvious seniority risk.
- `good_candidate`: useful candidate match, but not as strong as apply-now.
- `stretch_opportunity`: worth manual review, usually because it has risk or growth-skill gaps.
- `learning_signal`: useful mainly for understanding market demand and future learning.
- `low_priority`: weak fit for the current Candidate Profile v1.

Streamlit does not calculate the score, priority, bands, or reasons. It only reads and displays fields from `marts.mart_relevant_jobs`.
"""
    )
