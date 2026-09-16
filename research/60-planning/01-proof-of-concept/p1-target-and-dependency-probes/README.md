---
title: "P1 — Target and dependency probes"
kind: map
created: "2026-09-14"
tags:
  - browser
  - directory-index
  - emscripten
  - implementation-planning
  - runtime-loading
  - webassembly
aliases: []
---

# P1 — Target and dependency probes

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.proof_of_concept.p1
entities:
  - id: planning.erts_wasm.proof_of_concept.p1
    kind: milestone
    source_anchor: '#p1-target-and-dependency-probes'
  - id: planning.erts_wasm.proof_of_concept.p1.plan
    kind: plan
    source_anchor: '#ordered-phases'
relations:
  - subject: planning.erts_wasm.proof_of_concept.p1
    predicate: belongs_to
    object: planning.erts_wasm.proof_of_concept
  - subject: planning.erts_wasm.proof_of_concept.p1
    predicate: contains
    object: planning.erts_wasm.proof_of_concept.p1.plan
  - subject: planning.erts_wasm.proof_of_concept.p1
    predicate: precedes
    object: planning.erts_wasm.proof_of_concept.p2
```

## Purpose

Discover the real Wasm, thread, language-boundary, and browser-platform gaps
before a full ERTS link attempt. The phases isolate target/ABI risks, test
Worker-memory-controlled-start behavior, then exercise the production-shaped
delivery and trust path in pinned browsers.

## What belongs here

Small C/Emscripten and strict TypeScript probes, generated-glue inspection,
synthetic pthread and memory experiments, controlled-start verification,
manifest-bound delivery, cancellation, and browser cleanup evidence belong
here. A full ERTS build, OTP boot, topology selection, or compatibility claim
does not.

## Planning and delivery state

Plan: authored, review pending. Execution: blocked on accepted P0 evidence.
Tests and P1 gate: not run. Every original obligation and all structural tasks
remain unchecked. Pascal Charbonneau (`pcharbon70`) is the assigned experiment
owner and reviewer; work and review have not started. The renderer remains
deferred to C7. If Pascal personally produces an evidence record, the
[assignment independence rule](../../../assets/p0-governed-baseline/phase-03/p0-role-assignments.json)
requires a different independent reviewer before that record can close a task
or gate.

## Authoritative inputs

- [P0 plan](../p0-governed-baseline-and-proof-contract/README.md) supplies the required pins, bounds, loader contract, and trust rule.
- [Proof-of-concept stream](../README.md) defines milestone order and claim scope.
- [Runtime roadmap](../../erts-webassembly-runtime-milestones.md) prohibits choosing topology before measurement.
- [ERTS build and BEAM interpreter](../../../20-notes/components/erts-build-and-beam-interpreter.md) identifies the upstream C seams.
- [Browser platform time, poll, and progress](../../../20-notes/components/browser-platform-time-poll-and-progress.md) defines nonblocking progress risks.
- [ADR-0001](../../../20-notes/architecture-decisions/adr-0001-implementation-languages-and-beam-qualification-sequence.md) remains proposed pending these probes.

## Entry decisions and dependencies

| Decision ID | Choice and evaluation criteria | Resolution task / location | Responsible owner | Blocks | State and evidence |
| --- | --- | --- | --- | --- | --- |
| P1-D01 | Determine whether the pinned C/Emscripten target and narrow fixed-width host ABI are viable without semantic-machine edits. | `p1-p01-target-probe`, `p1-p01-host-abi` | Pascal Charbonneau (`pcharbon70`), ERTS C-port reviewer | P2 cross-build | Open; no evidence. |
| P1-D02 | Compare both Worker topology candidates using loading, responsiveness, ownership, abort, and cleanup evidence; do not select one in P1. | `p1-p02-worker-topologies`, `p1-p03-integration` | Pascal Charbonneau (`pcharbon70`), runtime/concurrency reviewer | P3 topology selection | Open; no evidence. |
| P1-D03 | Confirm a controlled-start seam and fixed shared-memory experiment profile under the exact generated glue. | `p1-p02-fixed-memory`, `p1-p02-controlled-start` | Pascal Charbonneau (`pcharbon70`), browser/Wasm reviewer | P2 loader design | Open; no evidence. |

## Gate-to-phase and artifact mapping

| Gate / acceptance ID | Required combined result | Artifact IDs | Owning phase and task IDs | Entry dependencies | Evidence and gate state |
| --- | --- | --- | --- | --- | --- |
| P1-A01 | Reproducible target, generated-interpreter C, host-ABI, and strict TypeScript authority probes. | `p1-target-matrix`, `p1-host-abi-probe`, `p1-ts-authority-probe` | [Phase 1](phase-01-target-abi-and-language-probes.md): `p1-p01-target-probe`, `p1-p01-host-abi`, `p1-p01-typescript-authority` | `p0-p03-handoff` | Not run / blocked on P0. |
| P1-A02 | Both pthread topology probes expose isolation, pool, memory, UI, abort, resource, and controlled-start behavior. | `p1-worker-probes`, `p1-memory-probe`, `p1-controlled-start-probe` | [Phase 2](phase-02-worker-memory-and-controlled-start-probes.md): `p1-p02-worker-topologies` through `p1-p02-controlled-start` | `p1-p01-handoff` | Not run / blocked. |
| P1-A03 | The production-shaped probe traverses the declared trust and delivery path and rejects skew, stale generations, and delivery-policy failures. | `p1-delivery-matrix`, `p1-bootstrap-negative-matrix` | [Phase 3](phase-03-delivery-trust-and-browser-acceptance.md): `p1-p03-manifest-delivery`, `p1-p03-bootstrap-trust` | `p1-p02-handoff` | Not run / blocked. |
| P1-GATE | Production-shaped pthread probe loads, remains responsive, aborts, restarts, cleans up, and records the complete reproducible matrix in pinned Chrome and Firefox. | All P1 artifacts and execution record | [Phase 3](phase-03-delivery-trust-and-browser-acceptance.md): `p1-p03-integration`, `p1-p03-handoff` | P1-A01 through P1-A03 | Not run / blocked. |

## Ordered phases

| Phase | Outcome | Entry dependency | Plan / execution state | Evidence |
| --- | --- | --- | --- | --- |
| [Phase 1 — Target, ABI, and language probes](phase-01-target-abi-and-language-probes.md) | Localize C/Emscripten target, ABI, and TypeScript authority risks. | Accepted `p0-p03-handoff` | Authored / blocked on P0 | None. |
| [Phase 2 — Worker, memory, and controlled-start probes](phase-02-worker-memory-and-controlled-start-probes.md) | Measure both topology candidates, fixed memory, and suppressed automatic entry. | `p1-p01-handoff` | Authored / not started | None. |
| [Phase 3 — Delivery trust and browser acceptance](phase-03-delivery-trust-and-browser-acceptance.md) | Exercise the production-shaped trust path and decide P1. | `p1-p02-handoff` | Authored / not started | None. |

P1 cannot begin until P0 passes. Within P1, Phase 1 localizes compile and
authority faults before Worker experiments; Phase 3 then reruns the assembled
probe through the actual delivery contract rather than a developer-only path.

## Milestone exit

P1 passes only when the production-shaped pthread probe successfully loads,
stays UI-responsive, aborts, restarts, and completely cleans up in pinned
Chrome and Firefox; otherwise the program records a stop condition. A
reproducible matrix records every command, artifact, import, Worker, pass,
failure, and localized patch.

**Claim unlocked:** browser/toolchain runway only.

**Stop trigger:** mandatory thread, memory, function-pointer, or deployment
behavior has no narrow platform-layer remedy.

Closure requires reviewed native and browser evidence at exact revisions. A
change to P0 pins or contracts, emsdk flags, ABI, generated glue, Worker
delivery, browser versions, or trust policy reopens the affected gate.

## Index

### Subdirectories

- None yet.

### Documents

- [Phase 1 — Target, ABI, and language probes](phase-01-target-abi-and-language-probes.md) — isolates target, C/host ABI, and TypeScript authority questions.
- [Phase 2 — Worker, memory, and controlled-start probes](phase-02-worker-memory-and-controlled-start-probes.md) — measures concurrency, memory, and startup seams.
- [Phase 3 — Delivery trust and browser acceptance](phase-03-delivery-trust-and-browser-acceptance.md) — exercises delivery, trust, abort, restart, and cleanup.

## Maintaining this index

Inventory every phase and keep P0 dependencies, exact flags, browser targets,
task IDs, generated artifacts, and evidence state synchronized. A passing probe
must not be restated as an ERTS build, boot, topology selection, or compatibility
claim.
