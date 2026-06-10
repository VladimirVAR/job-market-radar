# Tasks

## Purpose

The `tasks/` folder contains implementation assignment documents for Job Market Radar.

Task files describe intended implementation work. They are not execution reports.

## Task files vs execution reports

Task assignment files live in:

```text
tasks/
```

Execution reports live in:

```text
reports/task_execution/
```

Use task files to understand planned scope. Use reports to understand what was actually done.

## Original plan

The original MVP plan contained tasks `001` through `012`.

## Implementation changes

During implementation, the project evolved:

```text
011 was split into:
  011A — Build Analytics Marts
  011B — Create Streamlit Dashboard

013 was added:
  013 — Activate Live France Travail API Ingestion

013B was added:
  013B — Project Plan Reconciliation & Clean Live Baseline

013C was added:
  013C — Define and Implement Candidate Fit Scoring v1

014 was completed:
  014 — Final Polish / Public Release Readiness
```

The 011 split was introduced because Streamlit should consume dashboard-ready marts only. Business logic belongs in dbt, not in the UI layer.

## Current task sequence

```text
001 -> 002 -> 003 -> 004 -> 005 -> 006 -> 007 -> 008 -> 009 -> 010 -> 011A -> 011B -> 012 -> 013 -> 013B -> 013C -> 014
```

## How to read older task files

Older task files should be interpreted as initial implementation assignments. If they conflict with newer task files, execution reports, ADRs, or `backlog.md`, prefer the newer project state.

## Where to find execution reports

```text
reports/task_execution/
```

## Current status

```text
Technical MVP foundation: complete
Live data validation: complete
Candidate-specific scoring: complete
Final public release polish: complete
MVP public release: ready
```
