---
title: "C2 — Hardened code lifecycle"
kind: map
created: "2026-09-14"
tags:
  - code-loading
  - directory-index
  - implementation-planning
  - runtime-loading
  - security
aliases: []
---

# C2 — Hardened code lifecycle

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.in_depth_compatibility.c2
entities:
  - id: planning.erts_wasm.in_depth_compatibility.c2
    kind: milestone
    source_anchor: '#c2-hardened-code-lifecycle'
  - id: planning.erts_wasm.in_depth_compatibility.c2.plan
    kind: plan
    source_anchor: '#ordered-phases'
relations:
  - subject: planning.erts_wasm.in_depth_compatibility.c2
    predicate: belongs_to
    object: planning.erts_wasm.in_depth_compatibility
  - subject: planning.erts_wasm.in_depth_compatibility.c2
    predicate: contains
    object: planning.erts_wasm.in_depth_compatibility.c2.plan
  - subject: planning.erts_wasm.in_depth_compatibility.c2
    predicate: precedes
    object: planning.erts_wasm.in_depth_compatibility.c3
```

## Purpose

Select and verify the supported code-lifecycle policy so every admitted path
is manifest-enforced, transactional at its declared boundary, and free of stale
code, literal, capability, or generation state.

## What belongs here

The immutable-versus-constrained-lifecycle ADR, BEAM validation fuzzing,
prepare/commit rollback, `on_load`, code-index and literal effects, purging,
concurrency, cancellation, cache skew, generation replacement, signed manifest
sequencing, trust-root rotation, revocation, and rollback belong here. Hot
loading is optional rather than presumed.

## Planning and delivery state

Milestone definition: retained and reviewable. Phase plan: `decomposition
pending` accepted C1 evidence. Execution and tests: not started. Three source
work items remain unchecked; the source gate is not run.

## Authoritative inputs

- [C1 plan](../c1-compatibility-inventory-and-native-oracle/README.md) must supply a closed admitted profile and expanded oracle.
- [OTP boot and BEAM code loading](../../../20-notes/components/otp-boot-and-beam-code-loading.md) defines loader and code-index mechanisms.
- [Artifact loader and runtime generations](../../../20-notes/components/artifact-loader-and-runtime-generations.md) defines update-by-generation and trust sequencing.

## Entry decisions and dependencies

C2 cannot be decomposed or executed until C1 passes. The first phase must own
the required ADR and block policy-dependent tasks until it selects immutable,
signed bundles, or constrained replace/purge behavior. An immutable result is
valid; no hot-loading outcome is assumed.

## Gate-to-phase and artifact mapping

| Gate / acceptance ID | Required combined result | Artifact IDs | Owning phase and task IDs | Entry dependencies | Evidence and gate state |
| --- | --- | --- | --- | --- | --- |
| C2-A01 | Decide the supported lifecycle and verify its BEAM/code-index/literal/concurrency behavior under faults and cancellation. | `c2-lifecycle-adr`, `c2-lifecycle-matrix`, `c2-fuzz-corpus` | Decomposition pending | Accepted C1-GATE | Not run / blocked. |
| C2-A02 | Verify signed manifest and trust-root sequencing, revocation, downgrade, cache skew, and rollback where the selected policy applies. | `c2-update-trust-matrix` | Decomposition pending | C2-A01 | Not run / blocked. |
| C2-GATE | Every loading path is manifest-enforced, transactional at its declared boundary, and leaves no stale code, literal, capability, or generation state. | Complete C2 lifecycle evidence | Decomposition pending | C2-A01 and C2-A02 | Not run / blocked. |

## Retained work and evidence obligations

- [ ] Decide through an ADR whether the supported runtime remains immutable or
  admits signed bundles or constrained replace/purge behavior.
- [ ] Fuzz BEAM validation and test prepare/commit rollback, `on_load`, atom and
  export effects, code indices, literals, funs, purging, concurrent calls,
  cancellation, downgrade, cache skew, and generation replacement.
- [ ] Exercise signed manifest sequencing, trust-root rotation, revocation, and
  rollback where applicable.

## Ordered phases

Decomposition pending accepted C1 evidence. Expected seams are lifecycle-policy
decision and transactional validation, then update/trust sequencing. The ADR
must precede work whose acceptance differs by selected policy.

## Milestone exit

**Gate:** every loading path is manifest-enforced, transactional at its declared
boundary, and leaves no stale code, literal, capability, or generation state.

An immutable result is valid. Hot loading remains optional.

Closure requires the accepted ADR, reproducible lifecycle and update matrices,
fuzz corpus and minimized failures, state-settlement evidence, and independent
review at a named revision.

## Index

### Subdirectories

- None yet.

### Documents

- None yet; decomposition pending accepted C1 evidence.

## Maintaining this index

Retain every work item unchecked and the gate not run until decomposition and
evidence exist. Never write policy-dependent tasks as though an unresolved
lifecycle choice were accepted.
