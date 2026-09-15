---
title: "C1 — Compatibility inventory and native oracle"
kind: map
created: "2026-09-14"
tags:
  - compatibility
  - directory-index
  - implementation-planning
  - native-oracle
  - runtime-loading
aliases: []
---

# C1 — Compatibility inventory and native oracle

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.in_depth_compatibility.c1
entities:
  - id: planning.erts_wasm.in_depth_compatibility.c1
    kind: milestone
    source_anchor: '#c1-compatibility-inventory-and-native-oracle'
  - id: planning.erts_wasm.in_depth_compatibility.c1.plan
    kind: plan
    source_anchor: '#ordered-phases'
relations:
  - subject: planning.erts_wasm.in_depth_compatibility.c1
    predicate: belongs_to
    object: planning.erts_wasm.in_depth_compatibility
  - subject: planning.erts_wasm.in_depth_compatibility.c1
    predicate: contains
    object: planning.erts_wasm.in_depth_compatibility.c1.plan
  - subject: planning.erts_wasm.in_depth_compatibility.c1
    predicate: precedes
    object: planning.erts_wasm.in_depth_compatibility.c2
```

## Purpose

Expand the accepted POC closure and native/Wasm oracle into a complete,
machine-readable inventory for each candidate compatibility profile before any
new module becomes eligible for admission.

## What belongs here

Module, instruction, native, `on_load`, import, dependency, configuration,
capability, and loader closure; exact Elixir discovery inventories; normalized
differential harness expansion; support matrices; and direct bypass negatives
belong here. Elixir admission and unresolved profile edges do not.

## Planning and delivery state

Milestone definition: retained and reviewable. Phase plan: `decomposition
pending` accepted P6 evidence and approved product budgets. Execution and tests:
not started. Four source work items remain unchecked; the source gate is not
run.

## Authoritative inputs

- [Compatibility stream](../README.md) defines the accepted-P6 and product-budget entry rules.
- [P6 plan](../../01-proof-of-concept/p6-proof-of-concept-qualification-package/README.md) supplies the bounded proof and exact support surface.
- [OTP and Elixir compatibility profile](../../../20-notes/components/otp-and-elixir-compatibility-profile.md) defines discovery versus admission.
- [OTP boot and BEAM code loading](../../../20-notes/components/otp-boot-and-beam-code-loading.md) defines the lowest practical enforcement boundary.

## Entry decisions and dependencies

C1 cannot be decomposed or executed until P6 is accepted and qualification
budgets or their non-gameable derivation method are frozen. Candidate profile
contents, exact Elixir discovery patches, implementation location, and review
authority remain unresolved.

## Gate-to-phase and artifact mapping

| Gate / acceptance ID | Required combined result | Artifact IDs | Owning phase and task IDs | Entry dependencies | Evidence and gate state |
| --- | --- | --- | --- | --- | --- |
| C1-A01 | Close every candidate profile across modules, instructions, native edges, imports, capabilities, configuration, and loader enforcement. | `c1-profile-closure`, `c1-loader-negative-matrix` | Decomposition pending | Accepted P6-GATE and frozen budgets | Not run / blocked. |
| C1-A02 | Expand the normalized native/Wasm oracle and machine-readable support matrix, including discovery-only Elixir inventories. | `c1-oracle`, `c1-support-matrix`, `c1-elixir-discovery` | Decomposition pending | C1-A01 | Not run / blocked. |
| C1-GATE | No unresolved module, native, import, loader, or capability edge in the admitted profile. | Complete C1 closure and oracle evidence | Decomposition pending | C1-A01 and C1-A02 | Not run / blocked. |

## Retained work and evidence obligations

- [ ] Expand and automate the POC module, instruction, native, `on_load`, import,
  and capability closure for each proposed profile.
- [ ] Select candidate exact Elixir patches for discovery only and inventory
  each compiler, runtime module, emitted BEAM, application dependency, native
  edge, `on_load`, configuration assumption, and browser capability before any
  Elixir artifact is eligible for admission.
- [ ] Expand the normalized native/Wasm differential harness and
  machine-readable support matrix.
- [ ] Extend the already enforced module names, hashes, dependencies, and direct
  bypass-negative tests at the lowest practical ERTS loader boundary.

## Ordered phases

Decomposition pending accepted P6 evidence and frozen product budgets.
Expected seams are candidate closure/discovery inventory and differential
oracle/support-matrix expansion, but actual P6 artifacts and chosen profile
must establish the phases.

## Milestone exit

**Gate:** no unresolved module, native, import, loader, or capability edge in
the admitted profile.

Closure requires machine-readable closure and support artifacts, reproducible
native/Wasm traces, direct bypass negatives, exact discovery-only Elixir
identities, and independent review at a named revision.

## Index

### Subdirectories

- None yet.

### Documents

- None yet; decomposition pending accepted P6 evidence and frozen budgets.

## Maintaining this index

Retain every work item unchecked and the gate not run until decomposition and
evidence exist. Discovery does not authorize Elixir admission.
