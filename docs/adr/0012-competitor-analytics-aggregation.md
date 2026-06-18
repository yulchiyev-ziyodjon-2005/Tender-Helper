# ADR-012: Competitor Analytics Aggregation and Data Quality

**Status:** Accepted  
**Date:** 2026-06-14

## Context

Competitor statistics must be reproducible from completed tender results.
Keeping only aggregate rows would make ranking, discounts, and corrections
impossible to audit. Public result feeds can also contain missing bids,
invalid prices, inconsistent company names, and incomplete STIR values.

## Decision

- `TenderParticipant`, `TenderBid`, and `TenderAward` are the normalized source
  records owned by the `competitors` backend app.
- Only verified awards for completed tenders enter aggregation.
- STIR is the preferred identity key. When STIR is absent, a Unicode-normalized
  and case-folded company name is used as a deterministic fallback.
- Categories are Unicode-normalized, whitespace-collapsed, and case-folded.
- Invalid start prices, missing winning bids, unsupported currencies, and
  discounts outside `0..100` are excluded and recorded as fingerprinted
  `CompetitorDataQualityIssue` rows.
- A corrected source resolves the previous open issue during recalculation.
- `CompetitorAnalytics` is a recalculable lot/category/period snapshot.
  `update_or_create` and source replacement make repeated runs idempotent.
- Every snapshot is linked to exact participant, bid, and award rows through
  `CompetitorAnalyticsSource`.
- Ranking is deterministic: wins, win rate, participations, average winning
  discount, then identity key.
- Lot scope uses the selected lot's category but excludes the selected lot
  itself to avoid leaking its own result into the comparison set.
- The public API is read-only and Business/Enterprise gated. No manual
  competitor creation endpoint is exposed.
- Celery refreshes configured `30/90/365` day snapshots daily. Category
  snapshots use completed results; lot snapshots are prepared for active lots.
- Minimum sample size `3` and freshness SLO `86400` seconds are configurable
  operational defaults pending production dataset and business validation.

## Consequences

- Metrics are explainable and can be recomputed after source corrections.
- Name-only identities can still collide; source adapters should provide STIR
  whenever legally and technically available.
- Portal ingestion remains a separate source-adapter concern and must pass the
  same normalized model and data-quality boundary.
- SQLite supports deterministic local tests; PostgreSQL remains the production
  target for scale, scheduling, and concurrent aggregation.
