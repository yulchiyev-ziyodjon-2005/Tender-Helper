# ADR-017: Manual Tender Identity

- Status: Accepted
- Date: 2026-06-14

## Context

Portal lots have an external lot number, while manually entered tenders have no
trusted external identity. Manual creation was also anonymous, so provenance
could not be audited.

## Decision

Manual tender creation requires authentication. Each new manual `TenderLot`
receives:

- an internal UUID primary key;
- a generated `MANUAL-<random>` lot number;
- `platform_source=manual`;
- a nullable `created_by` foreign key for provenance.

The field is nullable so existing rows migrate without inventing an owner.
New manual rows always set `created_by=request.user`.

## Consequences

- Existing portal and seeded rows remain valid with `created_by=NULL`.
- A future duplicate-detection migration must use source-specific external
  identifiers and must not treat generated manual lot numbers as portal IDs.
- Authorization for editing or deleting manual tenders must scope by
  `created_by`; those operations are not part of the current API.
