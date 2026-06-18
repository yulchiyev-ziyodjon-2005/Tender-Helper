# ADR-015: Document Export Engine and Signed Downloads

**Status:** Accepted  
**Date:** 2026-06-14

## Context

Approved documents require backend-generated PDF and DOCX files, durable
storage metadata, and short-lived downloads.

## Decision

- DOCX is generated with `python-docx`.
- PDF is generated with ReportLab and a configurable Unicode TrueType font.
- Export input is an immutable `GeneratedDocumentRevision`, not mutable live
  editor state.
- Files are written through Django's storage API. Local storage is used in
  development; an S3-compatible Django storage backend can replace it without
  changing the domain service.
- Every export stores format, checksum, byte size, template version, revision,
  context snapshot, and lifecycle status.
- Download URLs use a timestamped application signature and require ownership
  authentication. Default validity is five minutes.
- Export failure marks the export row `failed`; the approved document remains
  approved and can be retried.

## Consequences

- Exported files are reproducible and traceable to the approved content.
- Storage migration does not require changing API or lifecycle models.
- Production deployment must configure a Unicode font and object storage.
