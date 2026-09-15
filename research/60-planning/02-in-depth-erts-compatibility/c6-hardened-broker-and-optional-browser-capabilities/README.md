---
title: "C6 — Hardened broker and optional browser capabilities"
kind: map
created: "2026-09-14"
tags:
  - browser
  - capabilities
  - directory-index
  - implementation-planning
  - security
aliases: []
---

# C6 — Hardened broker and optional browser capabilities

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.in_depth_compatibility.c6
entities:
  - id: planning.erts_wasm.in_depth_compatibility.c6
    kind: milestone
    source_anchor: '#c6-hardened-broker-and-optional-browser-capabilities'
  - id: planning.erts_wasm.in_depth_compatibility.c6.plan
    kind: plan
    source_anchor: '#ordered-phases'
relations:
  - subject: planning.erts_wasm.in_depth_compatibility.c6
    predicate: belongs_to
    object: planning.erts_wasm.in_depth_compatibility
  - subject: planning.erts_wasm.in_depth_compatibility.c6
    predicate: contains
    object: planning.erts_wasm.in_depth_compatibility.c6.plan
  - subject: planning.erts_wasm.in_depth_compatibility.c6
    predicate: precedes
    object: planning.erts_wasm.in_depth_compatibility.c7
```

## Purpose

Prove the generic bounded capability broker boundary before adding optional
browser services one at a time with independent authority and security gates.

## What belongs here

Overflow-safe frames, immutable metadata snapshots, producer/consumer
ownership, response copying, atomic slots, saturation and backpressure,
cancellation, concurrent shared-memory mutation resistance, nonblocking bridge
progress, and separately removable Fetch/WebSocket, persistence, cryptography,
or other admitted services belong here. Ambient browser authority does not.

## Planning and delivery state

Milestone definition: retained and reviewable. Phase plan: `decomposition
pending` accepted C5 evidence and selected optional capabilities. Execution and
tests: not started. Five source work items remain unchecked; the source gate is
not run.

## Authoritative inputs

- [C5 plan](../c5-core-otp-and-pinned-elixir-profile/README.md) must supply the accepted runtime profile before optional application powers open.
- [Capability broker and browser services](../../../20-notes/components/capability-broker-and-browser-services.md) defines the bounded deny-by-default protocol.
- [Memory, garbage collection, and shared state](../../../20-notes/components/memory-garbage-collection-and-shared-state.md) defines hostile shared-memory mutation risks.
- [Browser platform time, poll, and progress](../../../20-notes/components/browser-platform-time-poll-and-progress.md) defines the nonblocking progress requirement.

## Entry decisions and dependencies

C6 cannot be decomposed or executed until C5 passes. The generic broker must
pass before selecting or granting the first optional capability. Each service
then receives its own phase and security gate; no list here preauthorizes it.
Bridge design, selected capabilities, implementation location, quotas, and
review authority remain unresolved.

## Gate-to-phase and artifact mapping

| Gate / acceptance ID | Required combined result | Artifact IDs | Owning phase and task IDs | Entry dependencies | Evidence and gate state |
| --- | --- | --- | --- | --- | --- |
| C6-A01 | Prove bounded frames, copy/ownership rules, slots, saturation, cancellation, mutation resistance, and nonblocking progress for the generic broker. | `c6-broker-protocol`, `c6-broker-adversarial-matrix` | Decomposition pending | Accepted C5-GATE | Not run / blocked. |
| C6-CAPABILITY | Add one selected capability with typed schemas, purpose/origin restrictions, quotas, backpressure, cancellation, teardown, removability, and separate review. | Per-capability manifest and evidence | Decomposition pending after C6-A01 | Accepted generic broker gate | Not run / blocked. |
| C6-GATE | Generic broker passes before the first optional capability; each admitted capability passes separately and rejects undeclared or stale generations. | Complete broker and per-capability evidence | Decomposition pending | C6-A01 plus each selected capability gate | Not run / blocked. |

## Retained work and evidence obligations

- [ ] Before granting an optional capability, prove overflow-safe frames,
  private JavaScript snapshots of Wasm-authored metadata, producer-owned
  immutable publication, ERTS-owned response copies, atomic slot ownership,
  queue saturation/backpressure, cancellation, and concurrent shared-memory
  mutation resistance.
- [ ] Prove a dedicated or otherwise non-blocking bridge path preserves process
  and timer progress at `+S 1:1` while host work is pending.
- [ ] Add Fetch/WebSocket, persistence, cryptography, and other services one at
  a time with typed schemas, origin/purpose restrictions, quotas, cancellation,
  backpressure, teardown, and adversarial tests.
- [ ] Make each capability removable from imports, modules, manifest, and build.
- [ ] Keep optional application capability-handle creation closed until the
  generation reaches `ready`; pre-ready internal clock, wake, entropy,
  diagnostics, and release services remain fixed bootstrap imports, while
  hard termination remains supervisor-owned out-of-band authority.

## Ordered phases

Decomposition pending accepted C5 evidence. The first substantive phase must
qualify the generic broker. Each later phase adds exactly one selected optional
capability with its own closed graph and gate; no dummy capability phases are
created in advance.

## Milestone exit

**Gate:** the generic broker gate passes before the first optional capability;
then each capability passes a separate security review and cannot be invoked by
an undeclared or stale generation.

Closure requires generic-protocol and mutation evidence, liveness under pending
host work, and complete per-capability manifests, quotas, security tests,
removability proofs, teardown results, and independent reviews.

## Index

### Subdirectories

- None yet.

### Documents

- None yet; decomposition pending accepted C5 evidence and selected capabilities.

## Maintaining this index

Retain every work item unchecked and the gate not run until decomposition and
evidence exist. Do not create a capability phase or import before the generic
broker and that capability's explicit selection and authority review.
