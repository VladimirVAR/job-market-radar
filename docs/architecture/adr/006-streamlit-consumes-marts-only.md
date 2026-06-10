# ADR-006: Streamlit Consumes Marts Only

## Status

Accepted

## Context

The project needs a dashboard for exploring relevant jobs, skill demand, market trends, and weekly summaries.

There is a risk that Streamlit becomes a place where business logic is implemented directly.

## Decision

Streamlit should consume only dashboard-ready marts for business pages.

Business pages should read from:

```text
marts.*
```

Streamlit should not calculate relevance scores, skill demand, or weekly summaries.

## Reasoning

This keeps responsibilities clear:

- dbt owns transformations and metrics
- Streamlit owns presentation
- marts expose product-facing data

## Consequences

Positive:

- clean separation of concerns
- easier testing
- reusable marts
- dashboard logic remains simple
- clearer technical story

Negative:

- more work is required in dbt before dashboard development
- some quick UI experiments may require mart changes

## Alternatives Considered

### Streamlit reads raw tables

Rejected because it breaks the layered architecture.

### Streamlit calculates metrics directly

Rejected because business logic would be hidden in UI code.

### Streamlit reads warehouse models

Allowed only for technical/debug pages, not for business pages.

## Engineering Note

A thin dashboard on top of well-modeled marts is more professional than a dashboard that performs hidden transformations.
