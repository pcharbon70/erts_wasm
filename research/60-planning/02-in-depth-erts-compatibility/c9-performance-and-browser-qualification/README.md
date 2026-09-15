---
title: "C9 — Performance and browser qualification"
kind: map
created: "2026-09-14"
tags:
  - browser
  - directory-index
  - implementation-planning
  - performance
  - qualification
aliases: []
---

# C9 — Performance and browser qualification

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.in_depth_compatibility.c9
entities:
  - id: planning.erts_wasm.in_depth_compatibility.c9
    kind: milestone
    source_anchor: '#c9-performance-and-browser-qualification'
  - id: planning.erts_wasm.in_depth_compatibility.c9.plan
    kind: plan
    source_anchor: '#ordered-phases'
relations:
  - subject: planning.erts_wasm.in_depth_compatibility.c9
    predicate: belongs_to
    object: planning.erts_wasm.in_depth_compatibility
  - subject: planning.erts_wasm.in_depth_compatibility.c9
    predicate: contains
    object: planning.erts_wasm.in_depth_compatibility.c9.plan
  - subject: planning.erts_wasm.in_depth_compatibility.c9
    predicate: precedes
    object: planning.erts_wasm.in_depth_compatibility.c10
```

## Purpose

Measure each loading/runtime stage and the full supported browser/deployment
matrix against budgets frozen before C1, using reproducible distributions and
failure evidence rather than a warm demonstration.

## What belongs here

Fetch, verification, compilation, instantiation, Worker readiness, release
mount, ERTS initialization, OTP boot, module loading, warm restart, update,
artifact size, transient/steady memory, UI long tasks, idle CPU, wake/timer/host
latency, scheduler workloads, cleanup slopes, and the complete browser, OS,
cache, network, and deployment matrix belong here. Post-result threshold
selection does not.

## Planning and delivery state

Milestone definition: retained and reviewable. Phase plan: `decomposition
pending` accepted C8 evidence and frozen qualification matrix. Execution and
tests: not started. Three source work items remain unchecked; the source gate
is not run.

## Authoritative inputs

- [C8 plan](../c8-security-and-supply-chain-hardening/README.md) must supply the frozen and security-qualified candidate profile.
- [Compatibility stream](../README.md) defines the pre-C1 product-budget rule.
- [Runtime roadmap](../../erts-webassembly-runtime-milestones.md) prohibits inference from one browser, one boot, or a warm cache.

## Entry decisions and dependencies

C9 cannot be decomposed or executed until C8 passes. The exact support matrix,
benchmark fixtures, sampling and statistical method, automation, implementation
location, and review authority remain unresolved, but thresholds must remain
the pre-C1 values or derivation method.

## Gate-to-phase and artifact mapping

| Gate / acceptance ID | Required combined result | Artifact IDs | Owning phase and task IDs | Entry dependencies | Evidence and gate state |
| --- | --- | --- | --- | --- | --- |
| C9-A01 | Measure all declared load/update stages and runtime/resource dimensions with cold/warm separation and cleanup slopes. | `c9-stage-distributions`, `c9-runtime-distributions` | Decomposition pending | Accepted C8-GATE | Not run / blocked. |
| C9-A02 | Execute the complete supported browser, OS, cache, network, and deployment matrix against precommitted budgets. | `c9-support-matrix`, `c9-budget-verdicts` | Decomposition pending | C9-A01 | Not run / blocked. |
| C9-GATE | Every support claim and budget has reproducible distributions and failure evidence, not a single warm demo result. | Complete C9 qualification evidence | Decomposition pending | C9-A01 and C9-A02 | Not run / blocked. |

## Retained work and evidence obligations

- [ ] Measure fetch, verify, compile, instantiate, Worker readiness, release
  mount, ERTS init, OTP boot, module load, warm restart, and update separately.
- [ ] Measure artifact sizes, transient/steady memory, UI long tasks, idle CPU,
  wake/timer/host latency, scheduler workloads, and cleanup slopes.
- [ ] Run the complete supported browser, OS, cache, network, and deployment
  matrix against the budgets or approval method frozen before C1; do not select
  thresholds from the completed C9 results.

## Ordered phases

Decomposition pending accepted C8 evidence and a frozen qualification matrix.
Expected seams are stage/runtime distribution measurement, then full supported
matrix and budget verdicts. The precommitted experiment design must define the
actual phases before results exist.

## Milestone exit

**Gate:** every support claim and budget has reproducible distributions and
failure evidence, not a single warm demo result.

Closure requires exact fixtures, environments, revisions, tools, sampling and
analysis methods, raw and summarized distributions, failure results, budget
identities, support/exclusion matrix, and independent review.

## Index

### Subdirectories

- None yet.

### Documents

- None yet; decomposition pending accepted C8 evidence and a frozen matrix.

## Maintaining this index

Retain every work item unchecked and the gate not run until decomposition and
evidence exist. Keep cold/warm states and every load phase separate, and never
fit budgets to completed measurements.
