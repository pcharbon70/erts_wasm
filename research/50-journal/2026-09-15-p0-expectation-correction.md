---
title: "2026-09-15 — P0 expectation and evidence-order correction"
kind: journal
created: "2026-09-15"
tags:
  - governance
  - implementation-planning
  - proof-of-concept
  - runtime-loading
aliases: []
---

# 2026-09-15 — P0 expectation and evidence-order correction

This correction updates the [P0 governed-baseline plan](../60-planning/01-proof-of-concept/p0-governed-baseline-and-proof-contract/README.md)
to remove a circular dependency. P0 prepares and independently accepts the
governance contracts and experiment environment that authorize P1; it cannot
require the implementation artifacts and results that P1–P6 are designed to
produce.

## Problem found

The Phase 3 acceptance report mixed valid P0 readiness blockers with downstream
outcomes. In particular, it treated absent C/Emscripten, runtime, browser,
sanitizer, fuzz, compatibility, implementation-patch, and numeric
product-budget evidence as reasons to deny P0. That interpretation made later
work necessary to obtain its own entry authority.

## Corrected boundary

P0 now requires:

- independently accepted P0 contracts and phase handoffs;
- assigned immediate reviewers and P1 experiment owners;
- materialized, independently resolved OTP source/bootstrap, Emscripten build
  image/toolchain, and Chrome and Firefox fixtures;
- a reproduced clean experiment-readiness environment, including the static
  header/security preflight but excluding a P1 target compile; and
- no active P0 stop condition.

P0 explicitly defers built runtime assets, nonempty implementation patches,
compile/link/instantiate evidence, ERTS/OTP boot, browser semantics and
lifecycle, sanitizer/fuzz/compatibility results, and numeric product budgets.
The final product authority and values remain required after P6 and before C1.

## Role assignment update

Pascal Charbonneau (`pcharbon70`) subsequently self-assigned as the accountable
owner for the P0 review roles and the planned implementation experiments. The
machine-readable [role assignment](../assets/p0-governed-baseline/phase-03/p0-role-assignments.json)
binds the exact review and experiment scopes. Assignment satisfies the P0
ownership prerequisite but does not mark a review, experiment, task, phase, or
gate complete. If Pascal produces later execution evidence personally, a
different independent reviewer must accept that evidence before it can close a
task or gate. Numeric product-budget authority remains deferred after P6 and
before C1.

## Artifact corrections

- `p0-acceptance-contract` now enumerates downstream outcomes that cannot block
  P0 and narrows its pass conditions to contract/review/readiness evidence.
- `p0-acceptance-report` preserves the actual unresolved P0 blockers and moves
  downstream work into `deferred_outcomes_not_blocking_p0`.
- `p0-empty-target-environment` verifies tool, browser, mount, and delivery
  readiness without compiling a target probe.
- `p0-asset-dependency-patch-ledger` records downstream artifact milestones and
  the canonical SHA-256 of the empty patch stream instead of requiring
  artifacts or patches that do not yet exist.
- `p0-product-budget-method` freezes the method while deferring authority and
  numeric approval to the post-P6/pre-C1 gate.

## Validation and disposition

The P0 validator now rejects attempts to restore downstream runtime/product
outcomes as P0 blockers, validates the empty patch digest, and enforces the
deferred product-approval state. The complete archive and unit suite were run
after the correction; no runtime implementation command was run and no runtime
claim was added.

P0 remains **blocked**, but only for its legitimate unresolved work:
independent reviews, pinned-input materialization, the Chrome archive digest,
and clean experiment-readiness reproduction. Formal
P1 entry remains locked until those items are resolved.

Later the same day, P0.1 materialized the native bootstrap, build image,
qualification-browser archives, and browser-host compiler inputs and recorded
the Chrome digest. The remaining P0.1 blocker is the assigned owner's explicit
review disposition; the clean-environment replay remains a later P0 gate item.

## Provenance

The corrected baseline is merge revision
`1a049f45580af13ea42c31afa40d95320acfe11d`. The earlier Phase 2 and Phase 3
journals remain historical records of the original disposition and link to
this correction. The containing revision of this journal is the correction
revision.
