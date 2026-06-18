# ADR-011: Document Template, Version, and Editor Model

**Status:** Accepted  
**Date:** 2026-06-14

## Context

Generated tender documents must support AI generation, inline editing,
approval, revision history, and multiple frontend editors without making HTML
the authoritative format.

## Decision

- Document lifecycle belongs to the standalone `documents` Django app.
- A template version is immutable. Publishing a change creates a new
  `(code, language, version)` row.
- Only one active version exists for each `(code, language)` pair.
- Canonical content is editor-neutral JSON with a strict node and mark
  allowlist.
- Sanitized HTML and plain text are server-derived projections.
- Client-supplied HTML is not accepted as document authority.
- Important saves create `GeneratedDocumentRevision` rows. Optimistic locking
  uses `edit_version`; stale writes return `409`.
- AI output always starts as `draft`. Approval is an explicit user action.
- Editing an approved or exported document returns it to `draft`.
- Generation, edit, approval, export, failure, and archive actions create
  append-only document audit events.
- Company and tender context is snapshotted from an allowlist. Full registry
  payloads and unrelated PII are excluded.

## Consequences

- TipTap, Lexical, or another frontend editor can use an adapter without
  changing stored content.
- XSS payloads are escaped or rejected before projection is persisted.
- Historical exports remain bound to the exact approved revision, template
  version, and context snapshot.
