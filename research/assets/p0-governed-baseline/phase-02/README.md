---
title: "P0 phase 2 bounds and evidence artifacts"
kind: map
created: "2026-09-15"
tags:
  - archive-navigation
  - directory-index
  - governance
  - proof-of-concept
  - resource-bounds
aliases: []
---

# P0 phase 2 bounds and evidence artifacts (`phase-02`)

## Purpose

Freeze the proof's experimental safety envelope, negative scope, resource
bounds, product-budget method, and evidence profiles before runtime results can
influence them.

## What belongs here

P0-A02 contract inputs belong here. Numeric experimental safety ceilings are
allowed; numeric product qualification budgets, fabricated approvers, and
runtime results are not.

## Index

### Subdirectories

- None yet.

### Documents

- [`p0-evidence-profiles.json`](p0-evidence-profiles.json) — native/Wasm build, sanitizer, fuzz, minimization, SBOM, and provenance retention rules.
- [`p0-experiment-bounds.json`](p0-experiment-bounds.json) — finite cycle, settling, noise, safety, and semantic-comparison protocol.
- [`p0-loader-startup-bounds.json`](p0-loader-startup-bounds.json) — pre-ready resource owners, units, ceilings, enforcement points, and breach actions.
- [`p0-phase-02-validation-contract.json`](p0-phase-02-validation-contract.json) — assembled positive case and sixteen anti-gaming/malformed cases.
- [`p0-phase-02-validation-report.json`](p0-phase-02-validation-report.json) — local validation results and explicit not-run authority cases.
- [`p0-phase-02-producer-review-receipt.json`](p0-phase-02-producer-review-receipt.json) — traced producer review, corrections, validation, and limitations before owner disposition.
- [`p0-phase-02-owner-review-packet.json`](p0-phase-02-owner-review-packet.json) — bounded P0-A02 review questions and the exact requested owner disposition.
- [`p0-phase-02-owner-review-result.json`](p0-phase-02-owner-review-result.json) — the project owner's exact acceptance statement, reviewed packet identities, criteria, and accepted limitations.
- [`p0-product-budget-method.json`](p0-product-budget-method.json) — anti-gaming method frozen in P0 with numeric approval and product authority deferred post-P6/pre-C1.
- [`p0-unsupported-operations.json`](p0-unsupported-operations.json) — finite deny-by-default POC operation inventory.

## Maintaining this index

Every bound must have one owner, unit, finite ceiling, enforcement point, and
breach action. Product budgets remain `unassigned` until a named authority
freezes them through the recorded method. Validate with
`python3 research/70-tools/p0_contract_validation.py phase-02`.
