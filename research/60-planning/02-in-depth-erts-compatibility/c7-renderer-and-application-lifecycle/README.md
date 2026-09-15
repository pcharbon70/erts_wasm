---
title: "C7 — Renderer and application lifecycle"
kind: map
created: "2026-09-14"
tags:
  - accessibility
  - browser
  - directory-index
  - implementation-planning
  - renderer
aliases: []
---

# C7 — Renderer and application lifecycle

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.in_depth_compatibility.c7
entities:
  - id: planning.erts_wasm.in_depth_compatibility.c7
    kind: milestone
    source_anchor: '#c7-renderer-and-application-lifecycle'
  - id: planning.erts_wasm.in_depth_compatibility.c7.plan
    kind: plan
    source_anchor: '#ordered-phases'
relations:
  - subject: planning.erts_wasm.in_depth_compatibility.c7
    predicate: belongs_to
    object: planning.erts_wasm.in_depth_compatibility
  - subject: planning.erts_wasm.in_depth_compatibility.c7
    predicate: contains
    object: planning.erts_wasm.in_depth_compatibility.c7.plan
  - subject: planning.erts_wasm.in_depth_compatibility.c7
    predicate: precedes
    object: planning.erts_wasm.in_depth_compatibility.c8
```

## Purpose

Add a strict, separately authorized DOM renderer and prove functional,
accessible, bounded, stale-safe application lifecycle without granting the
runtime generic DOM or JavaScript authority.

## What belongs here

Strict TypeScript DOM isolation, emitted-JavaScript audit, runtime validation,
bounded declarative operations, sink allowlists, atomic batches, focus,
selection, accessibility, backpressure, stale-update rejection, same-trust
multi-component behavior, bundle admission, navigation, watchdog recovery,
and disposal belong here. Generic DOM/JavaScript escape hatches do not.

## Planning and delivery state

Milestone definition: retained and reviewable. Phase plan: `decomposition
pending` accepted C6 evidence and a selected renderer protocol. Execution and
tests: not started. Three source work items remain unchecked; the source gate
is not run.

## Authoritative inputs

- [C6 plan](../c6-hardened-broker-and-optional-browser-capabilities/README.md) must supply the accepted bounded broker and relevant declared capabilities.
- [Renderer, accessibility, and page lifecycle](../../../20-notes/components/renderer-accessibility-and-page-lifecycle.md) defines the semantic rendering boundary.
- [ADR-0001](../../../20-notes/architecture-decisions/adr-0001-implementation-languages-and-beam-qualification-sequence.md) assigns strict TypeScript to the browser control plane while requiring runtime validation.

## Entry decisions and dependencies

C7 cannot be decomposed or executed until C6 passes. The rendering protocol,
sink schema, component admission model, implementation location, browser
accessibility matrix, and review authority remain unresolved. DOM authority
must be unavailable to shared-protocol and runtime-Worker code by construction
and verified in emitted output.

## Gate-to-phase and artifact mapping

| Gate / acceptance ID | Required combined result | Artifact IDs | Owning phase and task IDs | Entry dependencies | Evidence and gate state |
| --- | --- | --- | --- | --- | --- |
| C7-A01 | Implement and audit the strict TypeScript renderer target with runtime validation and no DOM authority in shared/runtime Worker code. | `c7-renderer-build`, `c7-authority-audit` | Decomposition pending | Accepted C6-GATE | Not run / blocked. |
| C7-A02 | Prove bounded declarative rendering, accessibility, backpressure, stale rejection, component admission, navigation, recovery, and disposal. | `c7-render-protocol`, `c7-functional-matrix`, `c7-lifecycle-matrix` | Decomposition pending | C7-A01 | Not run / blocked. |
| C7-GATE | Functional, accessibility, loading, scaling, ownership, and teardown evidence passes without generic DOM or JavaScript authority. | Complete C7 renderer evidence | Decomposition pending | C7-A01 and C7-A02 | Not run / blocked. |

## Retained work and evidence obligations

- [ ] Implement the renderer in a strict TypeScript target whose DOM authority
  is unavailable to shared-protocol and runtime-Worker code; audit the emitted
  JavaScript and retain runtime validation at every event/operation boundary.
- [ ] Add a bounded declarative rendering protocol, sink allowlist, atomic
  batches, focus/selection/accessibility behavior, backpressure, and stale-update
  rejection.
- [ ] Test multiple same-trust components, component bundle admission,
  navigation, watchdog recovery, and page/runtime disposal.

## Ordered phases

Decomposition pending accepted C6 evidence and a selected renderer protocol.
Expected seams are renderer authority/protocol construction, then functional,
accessibility, multi-component, and lifecycle qualification. Actual protocol
and accessibility fixtures must establish the phase boundaries.

## Milestone exit

**Gate:** functional, accessibility, loading, scaling, ownership, and teardown
evidence passes without generic DOM or JavaScript authority.

Closure requires exact TypeScript and emitted-JavaScript identities, authority
audit, runtime validation negatives, functional/accessibility/browser matrices,
resource/backpressure measurements, and lifecycle/teardown evidence.

## Index

### Subdirectories

- None yet.

### Documents

- None yet; decomposition pending accepted C6 evidence and a selected protocol.

## Maintaining this index

Retain every work item unchecked and the gate not run until decomposition and
evidence exist. Renderer success never authorizes DOM access from ERTS, shared
protocol code, or runtime Workers.
