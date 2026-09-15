---
title: "C4 — Memory and shared-state compatibility"
kind: map
created: "2026-09-14"
tags:
  - directory-index
  - implementation-planning
  - memory
  - resource-bounds
  - webassembly
aliases: []
---

# C4 — Memory and shared-state compatibility

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.in_depth_compatibility.c4
entities:
  - id: planning.erts_wasm.in_depth_compatibility.c4
    kind: milestone
    source_anchor: '#c4-memory-and-shared-state-compatibility'
  - id: planning.erts_wasm.in_depth_compatibility.c4.plan
    kind: plan
    source_anchor: '#ordered-phases'
relations:
  - subject: planning.erts_wasm.in_depth_compatibility.c4
    predicate: belongs_to
    object: planning.erts_wasm.in_depth_compatibility
  - subject: planning.erts_wasm.in_depth_compatibility.c4
    predicate: contains
    object: planning.erts_wasm.in_depth_compatibility.c4.plan
  - subject: planning.erts_wasm.in_depth_compatibility.c4
    predicate: precedes
    object: planning.erts_wasm.in_depth_compatibility.c5
```

## Purpose

Qualify memory behavior, bounded failure, shared-state safety, quotas, and full
process/generation reclamation against approved product budgets.

## What belongs here

Process heaps, GC generations, binaries, literals, atoms, allocators,
mailboxes, ETS, persistent terms, fragmentation, fixed-ceiling failure,
optional separately selected growth, artifact/module preloading budgets,
runtime quotas, and reclamation distributions belong here. Unqualified memory
growth and post-result budget selection do not.

## Planning and delivery state

Milestone definition: retained and reviewable. Phase plan: `decomposition
pending` accepted C3 evidence. Execution and tests: not started. Two source work
items remain unchecked; the source gate is not run.

## Authoritative inputs

- [C3 plan](../c3-scheduler-and-browser-state-compatibility/README.md) must supply accepted scheduler and browser-state behavior.
- [Memory, garbage collection, and shared state](../../../20-notes/components/memory-garbage-collection-and-shared-state.md) defines the memory and JavaScript-view risks.
- [Compatibility stream](../README.md) requires budgets frozen before C1 rather than selected from C4 results.

## Entry decisions and dependencies

C4 cannot be decomposed or executed until C3 passes. Linear-memory growth is
excluded unless a separate profile decision selects and bounds it. Exact
stress fixtures, quota owners, implementation location, and review authority
remain unresolved.

## Gate-to-phase and artifact mapping

| Gate / acceptance ID | Required combined result | Artifact IDs | Owning phase and task IDs | Entry dependencies | Evidence and gate state |
| --- | --- | --- | --- | --- | --- |
| C4-A01 | Stress all declared ERTS/OTP memory classes under fixed-ceiling failure and prove process/generation reclamation; qualify growth only if separately selected. | `c4-memory-matrix`, `c4-reclamation-traces` | Decomposition pending | Accepted C3-GATE | Not run / blocked. |
| C4-A02 | Enforce artifact/module bounds before loading and runtime quotas after readiness. | `c4-quota-profile`, `c4-boundary-negative-matrix` | Decomposition pending | C4-A01 | Not run / blocked. |
| C4-GATE | Peak, steady, post-GC, post-code-lifecycle, and post-disposal memory distributions and slopes meet approved budgets. | Complete C4 distributions and evidence | Decomposition pending | C4-A01 and C4-A02 | Not run / blocked. |

## Retained work and evidence obligations

- [ ] Stress process heaps, GC generations, binaries, literals, atoms,
  allocators, mailboxes, ETS, persistent terms, fragmentation, fixed-ceiling
  failure, and process/generation reclamation. Qualify linear-memory growth only
  if a separately selected profile admits it.
- [ ] Enforce artifact and module budgets before loading and runtime quotas after
  readiness.

## Ordered phases

Decomposition pending accepted C3 evidence. Expected seams are memory stress
and reclamation, then pre-load bounds and post-ready quotas. The selected
fixed/growing-memory profile and actual runtime observables must determine the
phase boundaries.

## Milestone exit

**Gate:** peak, steady, post-GC, post-code-lifecycle, and post-disposal memory
distributions and slopes meet approved budgets.

Closure requires exact fixtures, distributions rather than single samples,
fixed-ceiling and quota-negative evidence, reclamation and settlement traces,
approved budget identities, and independent review at a named revision.

## Index

### Subdirectories

- None yet.

### Documents

- None yet; decomposition pending accepted C3 evidence.

## Maintaining this index

Retain every work item unchecked and the gate not run until decomposition and
evidence exist. Do not fit limits to completed C4 results or infer reclamation
from one successful GC or disposal.
