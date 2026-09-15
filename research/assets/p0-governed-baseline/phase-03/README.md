---
title: "P0 phase 3 loader and trust artifacts"
kind: map
created: "2026-09-15"
tags:
  - archive-navigation
  - directory-index
  - proof-of-concept
  - runtime-loading
  - security
aliases: []
---

# P0 phase 3 loader and trust artifacts (`phase-03`)

## Purpose

Specify the generation-scoped loader, manifest, root executable trust, and P0
acceptance contracts before a browser runtime implementation begins.

## What belongs here

Versioned schemas, state/ownership/failure rules, delivery policy, and local
contract-validation results belong here. Executable loader code and runtime
evidence do not.

## Index

### Subdirectories

- None yet.

### Documents

- [`p0-bootstrap-trust.json`](p0-bootstrap-trust.json) — selected first-proof trust root, delivery/header policy, trusted base, and rejection cases.
- [`p0-loader-contract.json`](p0-loader-contract.json) — loader states, topology partial orders, fixed boot inputs, identity, admission, ownership, and failure rules.
- [`p0-runtime-manifest.schema.json`](p0-runtime-manifest.schema.json) — versioned minimum schema for one coherent runtime generation.

## Maintaining this index

Treat any source, toolchain, asset, trust-root, manifest, topology, boot-input,
or bound change as a new generation contract. Never mark the P0 gate from
schema validation alone. Validate with
`python3 research/70-tools/p0_contract_validation.py phase-03`.
