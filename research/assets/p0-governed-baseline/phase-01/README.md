---
title: "P0 phase 1 baseline artifacts"
kind: map
created: "2026-09-15"
tags:
  - archive-navigation
  - directory-index
  - governance
  - proof-of-concept
  - runtime-loading
aliases: []
---

# P0 phase 1 baseline artifacts (`phase-01`)

## Purpose

Make the P0-A01 source, authority, runtime-dependency, and thread-census
baseline reviewable and reproducible without claiming an ERTS/Wasm build.

## What belongs here

Contract inputs, materialization receipts, local source-inspection results, and
owner-review packets for `p0-p01-pins` through `p0-p01-thread-census` belong
here. Independent acceptance, ERTS/Wasm compilation, browser runtime,
lifecycle, and compatibility evidence is not present.

## Index

### Subdirectories

- None yet.

### Documents

- [`p0-baseline-lock.json`](p0-baseline-lock.json) — exact qualification pins, acquisition origins, digests, and explicitly unresolved materialization checks.
- [`p0-language-ownership.json`](p0-language-ownership.json) — source-language, generated-artifact, ABI, toolchain, and review-trigger ownership.
- [`p0-phase-01-validation-contract.json`](p0-phase-01-validation-contract.json) — positive and contradiction cases for the assembled Phase 1 contract.
- [`p0-phase-01-validation-report.json`](p0-phase-01-validation-report.json) — local results and explicit not-run acceptance cases.
- [`p0-phase-01-materialization-receipt.json`](p0-phase-01-materialization-receipt.json) — exact native-bootstrap, build-image, browser, TypeScript, and pinned-source reproduction results and limitations.
- [`p0-phase-01-owner-review-packet.json`](p0-phase-01-owner-review-packet.json) — explicit review items and the attestation required from the assigned independent owner.
- [`p0-phase-01-owner-review-result.json`](p0-phase-01-owner-review-result.json) — the owner's dated acceptance of the packet and its recorded limitations.
- [`p0-runtime-inventory.json`](p0-runtime-inventory.json) — categorized observations and commands against the pinned OTP tree.
- [`p0-thread-census-contract.json`](p0-thread-census-contract.json) — independent logical-role, pthread-host, pool-capacity, and browser-supervisor measurements.
- [`p0-trust-scope-matrix.json`](p0-trust-scope-matrix.json) — assets, trust zones, authorities, quotas, topology candidates, and stop conditions.

## Maintaining this index

Change a pin only through an explicit baseline revision, retain source-fact,
local-observation, inference, and unresolved classifications, and keep the
independent-review state honest. Validate changes with
`python3 research/70-tools/p0_contract_validation.py phase-01`.
