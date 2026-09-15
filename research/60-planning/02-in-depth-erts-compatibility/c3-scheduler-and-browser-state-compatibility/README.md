---
title: "C3 — Scheduler and browser-state compatibility"
kind: map
created: "2026-09-14"
tags:
  - browser
  - directory-index
  - implementation-planning
  - scheduler
  - semantics
aliases: []
---

# C3 — Scheduler and browser-state compatibility

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.in_depth_compatibility.c3
entities:
  - id: planning.erts_wasm.in_depth_compatibility.c3
    kind: milestone
    source_anchor: '#c3-scheduler-and-browser-state-compatibility'
  - id: planning.erts_wasm.in_depth_compatibility.c3.plan
    kind: plan
    source_anchor: '#ordered-phases'
relations:
  - subject: planning.erts_wasm.in_depth_compatibility.c3
    predicate: belongs_to
    object: planning.erts_wasm.in_depth_compatibility
  - subject: planning.erts_wasm.in_depth_compatibility.c3
    predicate: contains
    object: planning.erts_wasm.in_depth_compatibility.c3.plan
  - subject: planning.erts_wasm.in_depth_compatibility.c3
    predicate: precedes
    object: planning.erts_wasm.in_depth_compatibility.c4
```

## Purpose

Qualify scheduler, timer, topology, and ownership behavior across the supported
browser-state matrix against approved native/Wasm tolerances.

## What belongs here

Scheduler, dirty/async/poll configurations, fairness, reductions, timer
ordering, topology, foreground/background throttling, suspension, visibility,
navigation, bfcache policy, and manifest-bound browser requirements belong
here. Threadless claims and unprofiled browser behavior do not.

## Planning and delivery state

Milestone definition: retained and reviewable. Phase plan: `decomposition
pending` accepted C2 evidence. Execution and tests: not started. Two source work
items remain unchecked; the source gate is not run.

## Authoritative inputs

- [C2 plan](../c2-hardened-code-lifecycle/README.md) must supply accepted code and generation lifecycle behavior.
- [Processes, schedulers, signals, and timers](../../../20-notes/components/processes-schedulers-signals-and-timers.md) defines scheduler semantic responsibilities.
- [Worker and pthread topology](../../../20-notes/components/worker-and-pthread-topology.md) defines browser ownership and lifecycle boundaries.
- [Browser platform time, poll, and progress](../../../20-notes/components/browser-platform-time-poll-and-progress.md) defines timer and suspension constraints.

## Entry decisions and dependencies

C3 cannot be decomposed or executed until C2 passes. Supported scheduler and
browser-state configurations, tolerances, automation reach, and implementation
location remain unresolved. Wall-clock behavior while the browser schedules no
supervisory work must remain separately qualified.

## Gate-to-phase and artifact mapping

| Gate / acceptance ID | Required combined result | Artifact IDs | Owning phase and task IDs | Entry dependencies | Evidence and gate state |
| --- | --- | --- | --- | --- | --- |
| C3-A01 | Exercise the selected scheduler/poll/timer/topology configurations across foreground, background, suspension, visibility, navigation, and bfcache states. | `c3-scheduler-matrix`, `c3-browser-state-matrix` | Decomposition pending | Accepted C2-GATE | Not run / blocked. |
| C3-A02 | Bind the qualified topology and required browser features to the release manifest. | `c3-manifest-profile` | Decomposition pending | C3-A01 | Not run / blocked. |
| C3-GATE | Native/Wasm observable behavior and resource ownership remain inside approved tolerances across the supported browser-state matrix. | Complete C3 traces and ownership evidence | Decomposition pending | C3-A01 and C3-A02 | Not run / blocked. |

## Retained work and evidence obligations

- [ ] Qualify scheduler/dirty/async/poll configurations, fairness, reductions,
  timer ordering, topology, foreground/background throttling, suspension,
  visibility changes, navigation, and bfcache policy.
- [ ] Bind topology and required browser features to the load manifest.

## Ordered phases

Decomposition pending accepted C2 evidence. Expected seams are scheduler and
poll configuration qualification, then browser-state and manifest-profile
qualification. Actual supported configurations and automation constraints
must determine the phases.

## Milestone exit

**Gate:** native/Wasm observable behavior and resource ownership remain inside
approved tolerances across the supported browser-state matrix.

Closure requires exact configurations, native/Wasm traces, browser-state and
resource-ownership matrices, manifest profile, limits, exclusions, and
independent review at a named revision.

## Index

### Subdirectories

- None yet.

### Documents

- None yet; decomposition pending accepted C2 evidence.

## Maintaining this index

Retain every work item unchecked and the gate not run until decomposition and
evidence exist. Keep browser scheduling exclusions explicit rather than hiding
them in broad timing tolerances.
