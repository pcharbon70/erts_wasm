---
title: "Proof-of-concept implementation stream"
kind: map
created: "2026-09-14"
tags:
  - archive-navigation
  - directory-index
  - implementation-planning
  - proof-of-concept
aliases:
  - "01 — Proof of concept"
---

# Proof-of-concept implementation stream

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.proof_of_concept
entities:
  - id: planning.erts_wasm.proof_of_concept
    kind: planning_stream
    source_anchor: '#proof-of-concept-implementation-stream'
relations: []
```

## Purpose

Establish one minimal, pinned, meaningful browser proof using upstream
interpreter ERTS, matching OTP modules, explicit runtime loading, a Tier-0
native/Wasm semantic oracle, and deterministic generation teardown.

## What belongs here

P0–P6 planning, gates, and evidence mappings belong here. General OTP or
Elixir compatibility, optional browser capabilities, rendering, production
readiness, and long-term support do not belong in the proof claim.

## Program state and ordering

P0.1 through P0.3 are accepted and P0-A01 through P0-A03 pass. P0-GATE remains
blocked on clean-environment readiness evidence. P0 Phases 4 through 6 now
decompose the required harness, clean input/container replay, pinned browser,
and evidence-handoff work; they are authored and unrun. Pascal Charbonneau
(`pcharbon70`) has accepted the remaining review and experiment-owner roles.
Runtime implementation results are explicitly deferred to P1–P6. P1 has
authored phase plans. P2–P6 retain substantive milestone definitions but remain
`decomposition pending` until predecessor evidence localizes the next work.

Milestones execute in ID order. A later milestone may be researched, but its
implementation cannot claim entry until the preceding milestone gate is
accepted. Runtime loading remains an acceptance dimension in every milestone.

## Index

### Subdirectories

- [P0 — Governed baseline and proof contract](p0-governed-baseline-and-proof-contract/README.md) — freezes pins, authority, bounds, evidence, and loading contracts.
- [P1 — Target and dependency probes](p1-target-and-dependency-probes/README.md) — tests C/Emscripten, ABI, Worker, memory, controlled-start, and delivery assumptions.
- [P2 — Interpreter artifact and outer loader](p2-interpreter-artifact-and-outer-loader/README.md) — cross-builds and instantiates the bounded interpreter artifact.
- [P3 — Immutable ERTS and OTP cold boot](p3-immutable-erts-and-otp-cold-boot/README.md) — boots the verified release to `booted-for-qualification`.
- [P4 — Tier-0 semantic capsule](p4-tier-0-semantic-capsule/README.md) — compares foundational ERTS semantics and the single-use admission path.
- [P5 — Bounded host progress and lifecycle](p5-bounded-host-progress-and-lifecycle/README.md) — proves asynchronous progress, revocation, and resource settlement.
- [P6 — Proof-of-concept qualification package](p6-proof-of-concept-qualification-package/README.md) — produces the bounded go/no-go evidence package.

### Documents

- None yet.

## Maintaining this index

Keep milestone order, predecessor gates, loading obligations, claim boundaries,
and evidence state synchronized with the [runtime roadmap](../erts-webassembly-runtime-milestones.md).
Create phase files only when their work, dependencies, integration gate, and
evidence handoff are substantive.
