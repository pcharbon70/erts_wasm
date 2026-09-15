---
title: "P5 — Bounded host progress and lifecycle"
kind: map
created: "2026-09-14"
tags:
  - browser
  - directory-index
  - implementation-planning
  - lifecycle
  - runtime-loading
  - security
aliases: []
---

# P5 — Bounded host progress and lifecycle

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.proof_of_concept.p5
entities:
  - id: planning.erts_wasm.proof_of_concept.p5
    kind: milestone
    source_anchor: '#p5-bounded-host-progress-and-lifecycle'
  - id: planning.erts_wasm.proof_of_concept.p5.plan
    kind: plan
    source_anchor: '#ordered-phases'
relations:
  - subject: planning.erts_wasm.proof_of_concept.p5
    predicate: belongs_to
    object: planning.erts_wasm.proof_of_concept
  - subject: planning.erts_wasm.proof_of_concept.p5
    predicate: contains
    object: planning.erts_wasm.proof_of_concept.p5.plan
  - subject: planning.erts_wasm.proof_of_concept.p5
    predicate: precedes
    object: planning.erts_wasm.proof_of_concept.p6
```

## Purpose

Prove asynchronous liveness, cancellation, forced recovery, and complete
generation ownership.

## What belongs here

Bounded host progress, timer/process liveness, failure injection at every load
and runtime state, full resource accounting, independently schedulable watchdog
termination, browser lifecycle events, queue/ownership fuzzing, generation
tokens, and repeated settlement slopes belong here. Optional application
capabilities and production claims do not.

## Planning and delivery state

Milestone definition: retained and reviewable. Phase plan: `decomposition
pending` accepted P4 evidence. Execution and tests: not started. All eleven
source checkboxes, including the gate, remain unchecked.

## Authoritative inputs

- [P4 plan](../p4-tier-0-semantic-capsule/README.md) must supply accepted Tier-0 semantics and the `ready` transition.
- [Browser platform time, poll, and progress](../../../20-notes/components/browser-platform-time-poll-and-progress.md) defines nonblocking progress behavior.
- [Worker and pthread topology](../../../20-notes/components/worker-and-pthread-topology.md) defines generation ownership and watchdog responsibilities.
- [Capability broker and browser services](../../../20-notes/components/capability-broker-and-browser-services.md) defines the bounded bootstrap request boundary.

## Entry decisions and dependencies

P5 cannot be decomposed or executed until P4 passes. Detection, termination,
settling, and noise limits must come from P0 rather than observed P5 results.
Browser scheduling suspension cannot be represented as a wall-clock cleanup
guarantee; the next lifecycle opportunity must reject the old generation.

## Gate-to-phase and artifact mapping

| Gate / acceptance ID | Required combined result | Artifact IDs | Owning phase and task IDs | Entry dependencies | Evidence and gate state |
| --- | --- | --- | --- | --- | --- |
| P5-A01 | Preserve process/timer progress and bounded host request behavior while accounting for every generation-owned resource. | `p5-progress-trace`, `p5-resource-ledger` | Decomposition pending | Accepted P4-GATE | Not run / blocked. |
| P5-A02 | Force termination across loading, running, waiting, wedged, frozen, navigated, and stale-completion states; fuzz ownership and cleanup. | `p5-failure-matrix`, `p5-lifecycle-matrix`, `p5-fuzz-corpus` | Decomposition pending | P5-A01 | Not run / blocked. |
| P5-GATE | Independently scheduled supervision terminates or rejects the complete old generation within declared active-time/lifecycle rules and leaves no positive resource slope. | Complete P5 lifecycle evidence | Decomposition pending | P5-A01 and P5-A02 | Not run / blocked. |

## Retained work and evidence obligations

- [ ] Harden and adversarially test the P2 bounded bootstrap
  request/completion, atomic-wakeup, cancellation, and cleanup path needed for
  clocks, timers, entropy, diagnostics, and control.
- [ ] Prove process and timer progress while host work is pending.
- [ ] Hard-stop during fetch, verification, compilation, Worker startup,
  instantiation, release mount, preload, boot, idle wait, timer wait, allocation,
  GC, and CPU-bound execution.
- [ ] Account for Workers, pthread registry, MessagePorts, timers, listeners,
  requests, shared memory/views, mounts, loading promises, and generation data.
- [ ] Place a watchdog/supervisor outside the ERTS scheduling and failure
  domain, prove that it remains independently schedulable while its browser
  agent runs, and set maximum active/supervisor-scheduled detection and
  complete-termination deadlines before the test.
- [ ] Prove active-time deadline-bounded termination while ERTS is CPU-bound,
  wedged, and waiting with an outstanding host request or occupied queue slot.
- [ ] Freeze, navigate, discard where test automation permits, and restore from
  bfcache; do not promise wall-clock cleanup while the browser schedules no
  supervisor work, and never reuse the old generation at the next lifecycle
  opportunity.
- [ ] Fuzz bounded queue frames, ownership transitions, cancellation, duplicate
  and late completions, generation rollover, and cleanup idempotence.

## Runtime-loading obligations

- [ ] Every callback and message carries its runtime generation; stopping closes
  admission, and late or duplicate completions cannot reach a replacement.
- [ ] Run the predefined boot/dispose series and settling interval after both
  successful and failed loads.

## Ordered phases

Decomposition pending accepted P4 evidence. Expected seams are bounded host
progress, watchdog and browser-lifecycle fault injection, and settlement/fuzz
qualification. Actual runtime scheduling and ownership traces must determine
their scope and ordering.

## Milestone exit

- [ ] While the supervisor is scheduled, its watchdog terminates the complete
  Worker graph within the declared active-time deadline; after freeze/discard,
  the next lifecycle opportunity rejects and replaces the old generation. No
  owned resource survives settlement, and Worker/memory metrics have no
  positive slope outside the declared noise envelope.

**Claim unlocked:** basic disposable browser-runtime evidence.

**Stop trigger:** any partial generation cannot be revoked, or stale completion
crosses into a new generation.

Closure requires complete fault and lifecycle matrices, resource time series,
fuzz results, predeclared limits, browser scheduling qualifications, and a
reviewed stop-condition disposition.

## Index

### Subdirectories

- None yet.

### Documents

- None yet; decomposition pending accepted P4 evidence.

## Maintaining this index

Retain every obligation and unchecked state until phase decomposition maps it
to stable task IDs. Keep active-time guarantees distinct from periods when the
browser schedules no supervisory work.
