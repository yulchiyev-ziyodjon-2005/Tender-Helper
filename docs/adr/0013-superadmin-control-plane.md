# ADR-013: Superadmin Capability, Step-up Authentication, and Audit

**Status:** Accepted  
**Date:** 2026-06-14

## Context

Platform operations need privileged access to users, companies, plans,
subscriptions, feature flags, document templates, and support data. Django
`is_superuser` alone is too broad, stolen long-lived sessions are unsafe for
critical changes, and direct model edits would bypass domain invariants and
audit requirements.

Payment, scraper, queue, and complete AI invocation domains are not yet
authoritative. The control plane must not fabricate operational or financial
data while those adapters are absent.

## Decision

- `AdminPrincipal` is a staff-only, explicit capability assignment.
  `admin_root` implies all capabilities but cannot mutate or delete audit
  records.
- Every admin API requires an active principal and fresh MFA verification.
  Critical writes additionally require a recent password + MFA step-up.
- The MFA implementation is an adapter configured by `ADMIN_MFA_PROVIDER`.
  The default provider is disabled, so production access cannot silently run
  without an approved MFA integration.
- Critical writes require a reason, expected resource version, idempotency
  key, and explicit confirmation.
- `AdminActionRequest` stores the actor-scoped idempotency record and request
  hash. Reusing a key with a different payload or reason is rejected.
- `AdminAuditEvent` stores actor, capability, action, target, reason,
  before/after values, outcome, request ID, IP, and metadata. Model,
  QuerySet, API, and Django admin paths prevent update/delete.
- User blocking and session revocation increment `auth_version`; existing JWT
  access tokens are rejected by versioned authentication.
- Subscription changes call the billing service. Downgrades are scheduled for
  period end and applied by an idempotent, row-locked Celery task.
- Plan updates use optimistic locking and a separate non-mutating impact
  preview. Plans targeted by scheduled changes cannot be deactivated.
- Feature kill switches are enforced inside the entitlement service, not only
  in the admin UI.
- PII is masked by default. Reveal, PII export, and audit export require a
  reason, fresh step-up, and an audit event. CSV cells are protected against
  spreadsheet formula injection.
- Payment, scraper, queue, notification template, and unavailable AI metrics
  return an explicit source status instead of placeholder values.
- Control-plane records are read-only in Django admin. Initial root access is
  bootstrapped with `grant_admin_root`; subsequent capability changes use the
  audited API.

## Consequences

- A Django superuser without an assigned principal cannot use the product
  control plane.
- Production must configure a real MFA adapter before privileged access is
  possible.
- Domain services remain the authority for subscription and entitlement
  behavior; the control plane is orchestration, not a parallel billing system.
- Financial and operational controls remain intentionally unavailable until
  their source domains and reconciliation rules exist.
- Frontend `/superadmin/` work can consume a stable backend contract without
  weakening backend authorization or relying on hidden UI controls.
