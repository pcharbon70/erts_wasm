---
title: "In-depth ERTS compatibility implementation stream"
kind: map
created: "2026-09-14"
tags:
  - archive-navigation
  - compatibility
  - directory-index
  - implementation-planning
aliases:
  - "02 — In-depth ERTS compatibility"
---

# In-depth ERTS compatibility implementation stream

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.in_depth_compatibility
entities:
  - id: planning.erts_wasm.in_depth_compatibility
    kind: planning_stream
    source_anchor: '#in-depth-erts-compatibility-implementation-stream'
relations: []
```

## Purpose

Expand an accepted proof of concept into a version-locked, security-reviewed,
measured, and maintainable ERTS-Wasm compatibility profile.

## What belongs here

C1–C10 profile expansion, code lifecycle, scheduler/browser-state behavior,
memory, OTP and staged Elixir qualification, optional browser capabilities,
rendering, security, performance, and maintenance planning belong here.
Unbounded compatibility claims and work that bypasses the P6 entry gate do not.

## Program entry and state

Program B starts only after P6 is accepted. Before C1, product owners freeze
qualification budgets or approve a non-gameable derivation method based on
named proof-of-concept and native baselines. P0 experimental ceilings do not
become product budgets.

Every C milestone is `decomposition pending`. No phase file will be created
until predecessor evidence, open decisions, exact artifacts, and acceptance
cases are sufficiently concrete. All work remains unchecked and all gates are
not run.

## Index

### Subdirectories

- [C1 — Compatibility inventory and native oracle](c1-compatibility-inventory-and-native-oracle/README.md) — closes profile dependencies and expands differential evidence.
- [C2 — Hardened code lifecycle](c2-hardened-code-lifecycle/README.md) — selects and verifies the admitted code-lifecycle policy.
- [C3 — Scheduler and browser-state compatibility](c3-scheduler-and-browser-state-compatibility/README.md) — qualifies scheduling across browser states.
- [C4 — Memory and shared-state compatibility](c4-memory-and-shared-state-compatibility/README.md) — proves memory budgets, failure, and reclamation.
- [C5 — Core OTP and pinned Elixir profile](c5-core-otp-and-pinned-elixir-profile/README.md) — qualifies Tier-1 OTP and gated ELX increments.
- [C6 — Hardened broker and optional browser capabilities](c6-hardened-broker-and-optional-browser-capabilities/README.md) — hardens the broker before adding capabilities individually.
- [C7 — Renderer and application lifecycle](c7-renderer-and-application-lifecycle/README.md) — adds bounded declarative rendering and application lifecycle evidence.
- [C8 — Security and supply-chain hardening](c8-security-and-supply-chain-hardening/README.md) — covers build, load, runtime, update, failure, and teardown trust.
- [C9 — Performance and browser qualification](c9-performance-and-browser-qualification/README.md) — evaluates approved budgets across the support matrix.
- [C10 — Maintained ERTS-Wasm release profile](c10-maintained-erts-wasm-release-profile/README.md) — rehearses updates and accepts or rejects sustainable ownership.

### Documents

- None yet.

## Maintaining this index

Keep the P6 entry gate, product-budget rule, milestone order, compatibility
nonclaims, and evidence state synchronized with the [runtime roadmap](../erts-webassembly-runtime-milestones.md).
Add no phase merely to fill an index.
