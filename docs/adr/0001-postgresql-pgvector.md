# ADR-001: PostgreSQL Foundation and Search Extensions

**Status:** Accepted  
**Date:** 2026-06-14

## Context

SQLite is useful for local development and fast unit tests, but it cannot
represent the production concurrency, indexing, and extension requirements.
Tender substring search must remain ordinary relational search and meet the
100,000-row latency target without introducing a separate search engine.

## Decision

- Staging and production use PostgreSQL 16 through `DATABASE_URL`.
- SQLite remains an explicit local/test fallback only. `APP_ENV=staging` or
  `production` refuses to start without a PostgreSQL URL.
- Persistent connections and health checks are configured through
  `DATABASE_CONN_MAX_AGE`.
- `pg_trgm` is installed by a non-atomic Django migration.
- Trigram GIN indexes are created concurrently for title, buyer, lot number,
  and category.
- Indexes target `UPPER(column)` because Django's PostgreSQL `icontains`
  lookup emits `UPPER(column) LIKE UPPER(%s)`. Raw-column indexes would exist
  but would not reliably support the actual ORM expression.
- Search input is always passed through Django ORM parameters. User input is
  never interpolated into SQL.
- Search benchmark data, `EXPLAIN ANALYZE`, and the 300 ms p95 assertion run
  against PostgreSQL 16 in CI.
- pgvector remains the accepted future vector store, but vector columns and
  RAG retrieval are outside WP6 and are not enabled by this migration.

## Consequences

- The deployment database role must be allowed to create `pg_trgm`.
- Migration rollback removes the four application indexes concurrently but
  preserves the shared extension.
- Category receives a trigram index because it participates in the same OR
  search predicate; its storage/write cost must be revisited using production
  benchmark data.
- Local SQLite smoke timings are contract checks only and cannot be presented
  as production performance evidence.
