---
title: "P0 governed baseline artifacts"
kind: map
created: "2026-09-15"
tags:
  - archive-navigation
  - directory-index
  - governance
  - proof-of-concept
aliases: []
---

# P0 governed baseline artifacts (`p0-governed-baseline`)

## Purpose

Retain the machine-readable contracts and validation results produced while
implementing the P0 governed-baseline plan.

## What belongs here

Version locks, trust and ownership matrices, source inventories, experiment
bounds, loader contracts, negative fixtures, and validation reports tied to
P0 task and acceptance IDs belong here. Passing planning-evidence records do
not belong here until an independent reviewer accepts the corresponding work.

## Index

### Subdirectories

- [Phase 1 baseline authority and runtime inventory](phase-01/README.md) — exact input identities, trust and language ownership, pinned-source runtime inventory, and thread-census contract.

### Documents

- None yet.

## Maintaining this index

Inventory every direct child, keep contract IDs stable, and preserve explicit
unknown, unavailable, review-pending, and not-run states. Never reinterpret a
locally valid contract as accepted gate evidence.
