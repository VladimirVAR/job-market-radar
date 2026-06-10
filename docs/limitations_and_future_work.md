# Limitations and Future Work

## Purpose

This document records known MVP limitations and realistic future improvements.

The project should be presented honestly as a local job-search data product MVP, not as a production hiring platform.

---

## Current MVP Limitations

### 1. Single primary source

The MVP uses France Travail / sample data.

This is enough to demonstrate the end-to-end architecture, but it does not represent the full European Data Engineering job market.

### 2. Live API credentials may be required

Live France Travail API mode may require valid credentials.

Sample mode exists to make local validation and demos more reliable.

### 3. Small local demo dataset

The local dataset may be intentionally small.

This keeps demos fast and reproducible, but limits the depth of trend analysis.

### 4. Rule-based skill extraction

Skill extraction is based on dictionary/rule matching.

This is transparent and easy to validate, but may:

- miss synonyms
- miss implicit skills
- produce false positives
- require manual dictionary maintenance

### 5. Simple relevance scoring

The MVP relevance score is explainable and rule-based.

It is not a machine learning recommendation model.

This is intentional for the MVP because explainability matters more than sophistication.

### 6. Limited weekly history

Weekly trends become meaningful only after multiple scheduled runs accumulate.

Early demos may show limited historical change.

### 7. Simple Streamlit UI

The dashboard is intentionally simple.

The goal is to demonstrate data product structure and analytical outputs, not advanced UI design.

### 8. Weekly report placeholder

The Airflow step `generate_weekly_report` is currently a placeholder or minimal reporting step depending on the implementation state.

This should be improved in a future version.

### 9. No production deployment

The MVP is designed for local execution.

It does not include production infrastructure, monitoring, cloud warehouse deployment, or managed scheduling.

### 10. No LinkedIn / Indeed scraping

The MVP does not scrape public project channels or Indeed.

This is intentional to avoid violating Terms of Service and to keep the data source strategy clean.

---

## Future Improvements

### 1. Add more job sources

Potential sources:

- Adzuna API
- The Muse API

This would improve market coverage and make cross-source comparison possible.

### 2. Improve skill extraction

Possible improvements:

- richer skill taxonomy
- synonym handling
- phrase matching
- NLP-based extraction
- embeddings for semantic matching

Any improved method should still be validated and explainable enough for technical review.

### 3. Improve relevance scoring

Possible improvements:

- weighted skill categories
- seniority-aware scoring
- location preferences
- contract preferences
- remote/hybrid preferences
- negative signals for overly senior roles
- multiple candidate profiles

### 4. Add historical trend tracking

Once more scheduled runs exist, the project can show:

- weekly market movement
- skill demand trends
- company activity changes
- location trends
- recurring postings

### 5. Add salary normalization

If reliable salary data becomes available, future models could normalize salary fields and compare roles by compensation range.

This should only be added when the source data is consistent enough.

### 6. Add CI checks

Useful CI checks:

- Python linting
- unit tests
- dbt parse
- dbt compile
- SQL style checks
- documentation link checks

### 7. Add optional hosted deployment

Possible deployment path:

- hosted Streamlit app
- managed PostgreSQL or cloud warehouse
- scheduled pipeline runner
- environment variable management

This is intentionally out of MVP scope.

### 8. Generate weekly Markdown reports

The current report step can be expanded into a real generated report with:

- latest market overview
- new relevant jobs
- top skills
- top missing skills
- active cities
- active companies
- data freshness summary

### 9. Add screenshots to documentation

Recommended screenshots:

- Airflow DAG success
- Streamlit Overview
- Streamlit Relevant Jobs
- Streamlit Skill Radar
- Streamlit Data Freshness

Screenshots should be real, not mocked.

---

## Project Framing

Recommended honest wording:

> This is a local MVP public release that demonstrates a complete Data Engineering flow: ingestion, raw preservation, dbt transformations, warehouse modeling, marts, validation, orchestration, and dashboard presentation.

Avoid:

> This is a production-ready hiring intelligence platform.

The honest version is stronger because it shows engineering judgment and realistic scope control.
