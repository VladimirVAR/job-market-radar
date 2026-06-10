# ADR-007: Use Rule-Based Skill Extraction in MVP

## Status

Accepted

## Context

The product needs to extract skills from job postings to support relevance scoring, skill demand analysis, and missing skill recommendations.

Possible approaches include rule-based matching, NLP libraries, embeddings, or machine learning.

## Decision

Use rule-based dictionary matching for the MVP.

## Reasoning

Rule-based extraction is:

- simple to implement
- transparent
- explainable
- easy to validate
- sufficient for MVP
- appropriate for a one-person local MVP

The skill dictionary should be versioned to keep relevance scoring reproducible.

## Consequences

Positive:

- fast implementation
- explainable results
- easy debugging
- clear limitations
- good fit for SQL/dbt modeling

Negative:

- may miss synonyms
- may produce false positives
- less powerful than NLP-based methods
- requires manual dictionary maintenance

## Alternatives Considered

### Machine learning model

Rejected for MVP because it adds complexity and reduces explainability.

### Embedding-based matching

Rejected for MVP because it requires extra infrastructure and validation.

### Manual tagging only

Rejected because it does not scale and does not demonstrate automated data processing.

## MVP Note

The MVP prioritizes explainability over sophistication. Future versions can improve extraction quality.
