# ADR-010: STIR Registry Provider and Confirmed Draft

- Status: Accepted for backend implementation
- Date: 2026-06-14

## Context

TenderHelper must prefill company details from a public registry without
treating third-party data as user-confirmed profile data. The production
registry source and its legal terms have not yet been approved.

## Decision

The company registry integration uses a provider interface loaded from Django
settings. The default provider is disabled and never performs network calls.
A configurable HTTP adapter is included for development and staging contract
testing, but production activation requires a separate legal and provider
review.

Registry behavior:

- STIR format is validated before provider access.
- Provider timeout is 5 seconds with one retry.
- Successful and not-found results are cached by provider and STIR for 24
  hours. Provider failures are not cached.
- Provider payload is normalized into a strict canonical company schema.
- Lookup creates a persistent `CompanyRegistryDraft`.
- Original normalized data, raw provider payload, and user-confirmed edited
  data are stored separately for audit.
- Provider data reaches `CompanyProfile` only after an authenticated confirm
  request.
- Confirm uses a database transaction and row lock and is single-use.
- Provider unavailable, timeout, and not-found results return a failed draft
  with manual onboarding allowed; onboarding is not blocked.
- Logs contain provider, STIR suffix, status, and latency, but never raw
  provider payload.

## HTTP Adapter Contract

The configurable adapter sends:

```text
GET <COMPANY_REGISTRY_API_URL>?stir=<9-digit-STIR>
Authorization: Bearer <COMPANY_REGISTRY_API_TOKEN>
```

It accepts either a canonical JSON object or an object wrapped in `data`.
Canonical keys are:

- `company_name`
- `company_type`
- `director_name`
- `legal_address`
- `registration_date`
- `has_vat`
- `industry`

HTTP `404` means company not found. Other non-success responses are provider
failures.

## Consequences

- Local development is deterministic and does not accidentally call an
  unapproved external service.
- A real Soliq or Statistics adapter can be added without changing views,
  serializers, drafts, or profile confirmation.
- Production must not set the HTTP provider class until endpoint ownership,
  authentication, rate limits, data retention, and legal usage are approved.
