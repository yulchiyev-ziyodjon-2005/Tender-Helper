# ADR-014: Subscription Entitlement and Usage Authority

**Status:** Accepted  
**Date:** 2026-06-14

## Context

Legacy subscription behavior read `CompanyProfile.current_tariff`, exposed a
public hardcoded plan list, and had no lifecycle or atomic usage accounting.
That design could not enforce paid features when an endpoint was called
directly.

## Decision

- `SubscriptionPlan` is the authoritative plan and limit configuration.
- `CompanySubscription` is the lifecycle record. Only `active` and valid
  `trialing` records grant plan entitlements.
- Expired paid subscriptions fall back to an active Free period.
- `CompanyProfile.current_tariff` remains a read-compatible projection and is
  never the feature-gate authority.
- Company access is resolved through a dedicated membership boundary. WP2 maps
  `CompanyProfile.user` to `owner`; a future `CompanyMember` model can replace
  the resolver without changing gate callers.
- Feature checks are centralized in the subscription entitlement service and
  enforce membership, role, active plan, feature availability, and STIR.
- `UsageRecord` stores one aggregate per company, metric, and billing period.
  Consumption uses a conditional database update inside a transaction.
- The period's limit is snapshotted on first use so later plan configuration
  edits do not retroactively change an in-progress period.
- Plan prices remain nullable until commercial values are approved.
- Checkout returns `501 payment_not_configured` and cannot activate a plan
  until a verified payment integration exists.

## Consequences

- Direct endpoint access cannot bypass paid feature checks.
- Enterprise inherits Business capabilities through explicit seeded features.
- Free/Pro/Business/Enterprise analysis limits are 4/100/250/500 per period.
- Payment callbacks and admin overrides must call the subscription activation
  service instead of updating legacy tariff fields.
- PostgreSQL remains the production target for row-lock semantics; SQLite is
  retained for local development and deterministic service tests.
