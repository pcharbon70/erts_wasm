---
title: "P2 — Interpreter artifact and outer loader"
kind: map
created: "2026-09-14"
tags:
  - c
  - directory-index
  - emscripten
  - implementation-planning
  - runtime-loading
  - webassembly
aliases: []
---

# P2 — Interpreter artifact and outer loader

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.proof_of_concept.p2
entities:
  - id: planning.erts_wasm.proof_of_concept.p2
    kind: milestone
    source_anchor: '#p2-interpreter-artifact-and-outer-loader'
  - id: planning.erts_wasm.proof_of_concept.p2.plan
    kind: plan
    source_anchor: '#ordered-phases'
relations:
  - subject: planning.erts_wasm.proof_of_concept.p2
    predicate: belongs_to
    object: planning.erts_wasm.proof_of_concept
  - subject: planning.erts_wasm.proof_of_concept.p2
    predicate: contains
    object: planning.erts_wasm.proof_of_concept.p2.plan
  - subject: planning.erts_wasm.proof_of_concept.p2
    predicate: precedes
    object: planning.erts_wasm.proof_of_concept.p3
```

## Purpose

Cross-build and instantiate upstream interpreter-only ERTS with the smallest
browser system, host-progress, and generation-cleanup layer.

## What belongs here

Cross-configuration, interpreter preservation, narrow C platform seams,
strict TypeScript loader/supervision, controlled entry, fixed shared memory,
bounded host progress, generated-artifact review, sanitizers, manifest closure,
and pre-boot cleanup belong here. OTP boot and semantic claims do not.

## Planning and delivery state

Milestone definition: retained and reviewable. Phase plan: `decomposition
pending` accepted P1 evidence. Execution and tests: not started. All fourteen
source checkboxes, including the gate, remain unchecked.

## Authoritative inputs

- [P1 plan](../p1-target-and-dependency-probes/README.md) must provide accepted target, ABI, Worker, memory, startup, and delivery evidence.
- [ERTS build and BEAM interpreter](../../../20-notes/components/erts-build-and-beam-interpreter.md) defines the upstream semantic boundary.
- [Artifact loader and runtime generations](../../../20-notes/components/artifact-loader-and-runtime-generations.md) defines controlled startup and generation ownership.
- [ADR-0001](../../../20-notes/architecture-decisions/adr-0001-implementation-languages-and-beam-qualification-sequence.md) governs C and strict TypeScript ownership unless P1 reopens it.

## Entry decisions and dependencies

P2 cannot be decomposed or executed until P1 passes and localizes every patch.
The implementation location remains unresolved. Any required Rust or new
handwritten C++ blocks the affected work pending a component-specific ADR.
Topology remains a candidate input; P3 selects it only after full-runtime
measurement.

## Gate-to-phase and artifact mapping

| Gate / acceptance ID | Required combined result | Artifact IDs | Owning phase and task IDs | Entry dependencies | Evidence and gate state |
| --- | --- | --- | --- | --- | --- |
| P2-A01 | Preserve the interpreter while implementing only the bounded target, platform, controlled-start, memory, and cleanup seams. | `p2-interpreter-artifact`, `p2-platform-layer`, `p2-host-control` | Decomposition pending | Accepted P1-GATE | Not run / blocked. |
| P2-A02 | Bind every Wasm, JavaScript, Worker, memory, import, and build identity to one verified generation and reject bounded-input failures before OTP boot. | `p2-generation-manifest`, `p2-negative-matrix` | Decomposition pending | P2-A01 | Not run / blocked. |
| P2-GATE | Artifact repeatedly compiles, links, instantiates, and terminates in Chrome and Firefox with no undeclared import or unowned Worker. | Complete P2 artifact and execution record | Decomposition pending | P2-A01 and P2-A02 | Not run / blocked. |

## Retained work and evidence obligations

- [ ] Cross-configure using the exact same-release native bootstrap.
- [ ] Preserve the generated BEAM interpreter and core runtime; disable BeamAsm,
  dynamic native loading, distribution, OS processes, shell, terminal, raw
  sockets, and other prohibited authority.
- [ ] Add only target/build fixes plus thread, time, poll/wakeup, entropy,
  diagnostics, release-byte, and fatal-exit platform seams.
- [ ] Keep ERTS and target/platform changes in upstream-compatible C and the
  maintained loader/supervisor in strict TypeScript compiled separately to
  pinned JavaScript. Any required Rust or new handwritten C++ stops P2 for a
  component-specific ADR rather than entering as incidental glue.
- [ ] Pre-create a conservative source-inventory-based pthread pool for
  interpreter instantiation; defer the measured full-runtime `N`/`N-1` claim
  until ERTS actually starts its thread graph in P3.
- [ ] Suppress automatic `main`, export only the necessary explicit ERTS entry,
  and make the outer loader enforce one invocation after the verified release
  mount. Bind the exact emsdk-controlled-start settings to the manifest.
- [ ] Instantiate fixed shared Wasm memory with identical initial/maximum
  values and treat allocation failure or a Wasm trap as generation-fatal.
- [ ] Implement the minimum bounded request/completion, atomic-wakeup,
  cancellation, and idempotent partial-generation cleanup path required before
  OTP boot.
- [ ] Review Wasm imports/exports, memory/table declarations, JavaScript glue,
  Worker scripts, flags, generated sources, and patch footprint.
- [ ] Produce assertion/debug plus supported native and Emscripten
  AddressSanitizer/UndefinedBehaviorSanitizer and fuzz-target builds; record
  unsupported combinations instead of silently dropping them.

## Runtime-loading obligations

- [ ] Bind Wasm, generated JavaScript, Worker assets, memory settings, imports,
  and build identity to one verified manifest generation.
- [ ] Exercise success, mismatch, cancellation, timeout, and partial-start
  cleanup before attempting OTP boot.
- [ ] Reject oversized or truncated manifests and artifacts, excessive Worker
  or memory declarations, queue overflow, and decompression expansion before
  the affected decode, allocation, Worker creation, or instantiation.

## Ordered phases

Decomposition pending accepted P1 evidence. Expected seams are cross-build and
platform adaptation, controlled-start/generation ownership, and integrated
browser instantiation, but these are not phase files or accepted task
boundaries. P1 results must determine their exact scope and dependencies.

## Milestone exit

- [ ] The artifact repeatedly compiles, links, instantiates, and terminates in
  Chrome and Firefox with no undeclared import or unowned Worker.

**Claim unlocked:** compile/link/instantiate evidence only.

**Stop trigger:** the patch spreads materially into scheduler, process, GC, or
loader semantics instead of remaining a reviewable target/platform layer.

Closure requires exact native and browser commands, artifact identities,
generated-glue and import/export audits, negative results, resource ownership,
and reviewed stop-condition disposition.

## Index

### Subdirectories

- None yet.

### Documents

- None yet; decomposition pending accepted P1 evidence.

## Maintaining this index

Retain every obligation and unchecked state until phase decomposition maps it
to stable task IDs. Add no phase before P1 evidence resolves its actual seam.
