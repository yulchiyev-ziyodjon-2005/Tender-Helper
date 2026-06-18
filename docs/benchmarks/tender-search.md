# Tender Search Benchmark

**Contract date:** 2026-06-14  
**Target:** PostgreSQL 16, 100,000 active lots, p95 <= 300 ms

## Automated Gate

The `backend-postgresql` CI job:

1. starts PostgreSQL 16;
2. applies migrations and verifies `pg_trgm` functional GIN indexes;
3. creates 100,000 deterministic active benchmark lots;
4. runs `EXPLAIN ANALYZE` with buffers;
5. executes 20 measured searches after three warmups;
6. fails when p95 exceeds 300 ms.

Equivalent command:

```powershell
python manage.py seed_tender_search_benchmark --count 100000 --reset
python manage.py benchmark_tender_search `
  --query "specialized server" `
  --iterations 20 `
  --warmup 3 `
  --minimum-dataset-size 100000 `
  --assert-p95-ms 300 `
  --explain
```

Synthetic seed data is restricted to `APP_ENV=test` unless
`--allow-non-test` is explicitly supplied. Rows use the
`BENCH-SEARCH-` prefix so reset does not delete unrelated tenders.

## Local Fallback

SQLite can verify the query contract, but not the PostgreSQL latency target:

```powershell
python manage.py benchmark_tender_search `
  --query server `
  --iterations 5 `
  --allow-sqlite
```

The first PostgreSQL CI execution result should be retained with the build
artifact or observability system. SQLite timings must not be used as the
production acceptance result.
