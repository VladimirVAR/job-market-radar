# Task 012: Write Demo Docs

## Goal

Write demo-friendly documentation for GitHub, public project review, and technical reviews.

The documentation should explain the project clearly without exaggerating.

---

## Context

Job Market Radar is a local Data Engineering data product for a practical job-search use case.

The documentation should make the architecture, data flow, trade-offs, and demo story easy to understand.

---

## Deliverables

Create or update:

```text
README.md
docs/architecture/architecture_overview.md
docs/architecture/data_flow.md
docs/architecture/data_model.md
docs/architecture/source_to_target_contract.md
docs/architecture/validation_contract.md
docs/demo_script.md
docs/data_catalog.md
docs/naming_conventions.md
docs/limitations_and_future_work.md
```

---

## README Requirements

README should include:

- project overview
- product idea
- architecture diagram in text form
- stack
- how to run locally
- data flow
- key tables/models
- dashboard description
- validation approach
- limitations
- future improvements

---

## Demo Script Requirements

The demo script should explain:

1. What problem the project solves.
2. Why the architecture uses raw/staging/warehouse/marts.
3. How ingestion works.
4. How raw API responses are preserved.
5. How dbt transformations work.
6. How relevance scoring works.
7. How the dashboard consumes marts.
8. What trade-offs were made.
9. What would be improved next.

---

## Data Catalog Requirements

Document:

- table/model name
- schema/layer
- grain
- purpose
- key columns
- downstream consumers

---

## Limitations and Future Work

Document honestly:

- France Travail only in MVP
- no public project channels/Indeed scraping
- rule-based skill extraction
- simple relevance scoring
- no cloud deployment in MVP
- no ML recommendation system in MVP

Future work:

- Adzuna API
- The Muse API
- better skill extraction
- cross-source matching
- CI/CD
- optional cloud deployment

---

## Acceptance Criteria

- README explains the project clearly.
- Architecture docs are consistent with implemented structure.
- Demo script is walkthrough-friendly.
- Data catalog includes grain for important models.
- Limitations are honest.
- Future improvements are realistic.
- Documentation does not exaggerate the project.

---

## Implementation Notes

Keep documentation clear and professional.

The project should sound like a real data product, not a tutorial script.

---

## Dependencies

Task 011.

---

## Final Output

A complete, release-ready MVP repository.
