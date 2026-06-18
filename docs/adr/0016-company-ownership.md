# ADR-016: Company Ownership Enforcement

- Status: Accepted
- Date: 2026-06-14

## Context

Analysis requests may include a `company_id`. Resolving that identifier without
scoping it to the authenticated user would allow cross-account data access.

## Decision

Every company lookup used by user-facing APIs must begin from
`CompanyProfile.objects.filter(user=request.user)`. A supplied identifier that
is outside that queryset returns `404`, preventing both access and object
enumeration. The backend is the final ownership authority.

## Consequences

- Analysis history, status, result, and calculator queries remain scoped through
  `company__user=request.user`.
- Future team access must introduce an explicit membership permission instead
  of weakening this owner scope.
- Ownership behavior requires API tests for unauthenticated and cross-user
  requests.
