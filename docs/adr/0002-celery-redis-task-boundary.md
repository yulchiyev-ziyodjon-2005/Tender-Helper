# ADR-002: Celery and Redis Task Boundary

**Status:** Accepted  
**Date:** 2026-06-14

## Context

AI document generation and binary export are slow, failure-prone operations.
Running them as permanent request-thread logic would make HTTP timeouts and
duplicate execution difficult to control.

## Decision

- Celery is the backend task boundary.
- Redis is the production broker and result backend.
- Generation and export tasks are idempotent by lifecycle status: a task only
  processes `generating` or `queued` rows respectively.
- Local development and deterministic tests use
  `CELERY_TASK_ALWAYS_EAGER=True`.
- Production must set eager mode to false and run a separate Celery worker.
- Queue dispatch failure is persisted as a real failed lifecycle event; it is
  never represented as successful progress.

## Consequences

- API requests return a persisted resource that can be polled.
- Retried or duplicate task delivery does not generate a second revision or
  file after the resource has left its processable status.
- Redis and worker health become production deployment requirements.
