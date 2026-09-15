---
title: "C5 — Core OTP and pinned Elixir profile"
kind: map
created: "2026-09-14"
tags:
  - compatibility
  - directory-index
  - elixir
  - implementation-planning
  - otp
  - runtime-loading
aliases: []
---

# C5 — Core OTP and pinned Elixir profile

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.in_depth_compatibility.c5
entities:
  - id: planning.erts_wasm.in_depth_compatibility.c5
    kind: milestone
    source_anchor: '#c5-core-otp-and-pinned-elixir-profile'
  - id: planning.erts_wasm.in_depth_compatibility.c5.plan
    kind: plan
    source_anchor: '#ordered-phases'
relations:
  - subject: planning.erts_wasm.in_depth_compatibility.c5
    predicate: belongs_to
    object: planning.erts_wasm.in_depth_compatibility
  - subject: planning.erts_wasm.in_depth_compatibility.c5
    predicate: contains
    object: planning.erts_wasm.in_depth_compatibility.c5.plan
  - subject: planning.erts_wasm.in_depth_compatibility.c5
    predicate: precedes
    object: planning.erts_wasm.in_depth_compatibility.c6
```

## Purpose

Qualify Tier-1 OTP and then incrementally admit one exact, closed Elixir
profile without inferring broad compatibility from a lower increment.

## What belongs here

Tier-1 OTP applications and behaviours, ELX-0 discovery closure, ELX-1 smoke
admission, ELX-2 core semantics, ELX-3 OTP behaviour integration, ELX-4
representative application closures, and per-increment manifests, support
matrices, negative tests, lifecycle, fault, and resource evidence belong here.
Runtime Mix, IEx, compiler applications, eval, arbitrary loading, and broad
configuration providers remain excluded unless separately admitted.

## Planning and delivery state

Milestone definition: retained and reviewable. Phase plan: `decomposition
pending` accepted C4 evidence and exact Tier-1/Elixir candidates. Execution and
tests: not started. Six source work items remain unchecked; the source gate is
not run.

## Authoritative inputs

- [C4 plan](../c4-memory-and-shared-state-compatibility/README.md) must supply accepted memory and quota behavior.
- [OTP and Elixir compatibility profile](../../../20-notes/components/otp-and-elixir-compatibility-profile.md) defines the Erlang-first and ELX-0–ELX-4 sequence.
- [ADR-0001](../../../20-notes/architecture-decisions/adr-0001-implementation-languages-and-beam-qualification-sequence.md) makes the POC Erlang-first and later Elixir exact and incremental.
- [C1 plan](../c1-compatibility-inventory-and-native-oracle/README.md) supplies discovery-only candidate closure.

## Entry decisions and dependencies

C5 cannot be decomposed or executed until C4 passes. ELX-1 cannot begin until
the accepted P6 Erlang baseline, Tier-1 OTP baseline, and ELX-0 closure all
pass. Exact Elixir patches, compiler/dependency generations, Tier-1 surface,
representative ELX-4 applications, implementation location, and reviewers
remain unresolved.

## Gate-to-phase and artifact mapping

| Gate / acceptance ID | Required combined result | Artifact IDs | Owning phase and task IDs | Entry dependencies | Evidence and gate state |
| --- | --- | --- | --- | --- | --- |
| C5-A01 | Qualify the selected Tier-1 OTP surface and close one exact ELX-0 compiler/runtime/dependency/capability graph without admitting Elixir. | `c5-tier1-matrix`, `c5-elx0-closure` | Decomposition pending | Accepted C4-GATE and C1 discovery | Not run / blocked. |
| C5-ELX1 | Admit one precompiled manifest-listed smoke module only after P6, Tier-1, and ELX-0 pass. | `c5-elx1-manifest`, `c5-elx1-evidence` | Decomposition pending | C5-A01 | Not run / blocked. |
| C5-ELX2 | Qualify core Elixir language/runtime semantics for the exact profile. | `c5-elx2-manifest`, `c5-elx2-evidence` | Decomposition pending | Accepted C5-ELX1 | Not run / blocked. |
| C5-ELX3 | Qualify Elixir OTP behaviour integration for the exact profile. | `c5-elx3-manifest`, `c5-elx3-evidence` | Decomposition pending | Accepted C5-ELX2 | Not run / blocked. |
| C5-ELX4 | Qualify each selected representative application as a separate closed increment. | Per-application manifest, matrix, and evidence | Decomposition pending | Accepted C5-ELX3 | Not run / blocked. |
| C5-GATE | Every accepted increment has a closed graph and versioned semantic, lifecycle, fault, negative, resource, manifest, and support-matrix evidence package. | Complete C5 profile evidence | Decomposition pending | Accepted preceding increments | Not run / blocked. |

## Retained work and evidence obligations

- [ ] Qualify Tier-1 applications, supervisors, `gen_server`, `gen_statem`,
  selected logging, and standard-library paths.
- [ ] Complete ELX-0 by selecting one exact Elixir source/compiler/dependency
  generation and closing its reachable loading, native, `on_load`,
  configuration, and capability graph without granting runtime support.
- [ ] Complete ELX-1 by admitting one precompiled, manifest-listed Elixir smoke
  module only after the Erlang and Tier-1 OTP baselines pass. Record the exact
  narrow result and reject any general Elixir inference.
- [ ] Complete ELX-2 and ELX-3 separately for core language/runtime semantics
  and OTP behaviour integration, including native/Wasm failures, lifecycle,
  cancellation, and resource settlement.
- [ ] Complete ELX-4 one representative application closure at a time while
  keeping Mix, IEx, compiler applications, eval, arbitrary loading, and runtime
  configuration providers excluded unless a later profile separately admits
  them.
- [ ] Regenerate, sign, and review the release manifest and machine-readable
  support matrix for every Elixir increment.

## Ordered phases

Decomposition pending accepted C4 evidence and exact selected candidates.
Expected ordering is Tier-1 plus ELX-0, ELX-1, ELX-2, ELX-3, then one phase per
ELX-4 application closure. No phase is created until its predecessor evidence
passes and its exact artifact graph and acceptance cases are known.

## Milestone exit

**Gate:** each ELX increment has its own closed artifact/capability graph,
versioned support matrix, manifest, and representative native/Wasm semantic,
lifecycle, fault, negative, and resource evidence. Failure stops later
increments; no broad compatibility is inferred from a lower increment.

Closure requires a separately reviewed evidence package for Tier-1 and each
accepted ELX increment, with exact compiler/source/dependency/BEAM identities,
manifest, exclusions, and no unresolved reachable edge.

## Index

### Subdirectories

- None yet.

### Documents

- None yet; decomposition pending accepted C4 evidence and exact candidates.

## Maintaining this index

Retain every work item unchecked and the gate not run until decomposition and
evidence exist. Admission begins only inside C5 after accepted P6, Tier-1, and
ELX-0 evidence; discovery or a smoke module never implies broad Elixir support.
