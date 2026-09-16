---
title: "Phase 2 — Worker, memory, and controlled-start probes"
kind: note
created: "2026-09-14"
maturity: developing
tags:
  - browser
  - emscripten
  - implementation-planning
  - pthreads
  - runtime-loading
aliases: []
---

# Phase 2 — Worker, memory, and controlled-start probes

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.proof_of_concept.p1.phase_02
entities:
  - id: planning.erts_wasm.proof_of_concept.p1.phase_02
    kind: phase
    source_anchor: '#phase-2-worker-memory-and-controlled-start-probes'
relations:
  - subject: planning.erts_wasm.proof_of_concept.p1.phase_02
    predicate: belongs_to
    object: planning.erts_wasm.proof_of_concept.p1.plan
  - subject: planning.erts_wasm.proof_of_concept.p1.phase_02
    predicate: precedes
    object: planning.erts_wasm.proof_of_concept.p1.phase_03
```

Measure both Worker topology candidates, pthread-pool behavior, fixed shared
memory, UI responsiveness, abort cleanup, and the seam that prevents automatic
ERTS entry.

Back to milestone: [P1 plan](README.md).

## Entry, scope, and dependencies

Entry requires accepted `p1-p01-handoff` evidence from [Phase 1](phase-01-target-abi-and-language-probes.md).
Plan review is pending; execution and tests have not started. Browser-host and
C-runtime areas share the probe, while the implementation repository remains
unresolved. Pascal Charbonneau (`pcharbon70`) is assigned as experiment owner
and reviewer; work and review have not started.

This phase compares candidates; it does not select the final Worker topology
or claim the full ERTS pool size. It uses fixed memory for the first proof and
does not qualify memory growth.

## Research and acceptance traceability

- [Planning conventions](../../README.md)
- [Worker and pthread topology](../../../20-notes/components/worker-and-pthread-topology.md)
- [Memory, garbage collection, and shared state](../../../20-notes/components/memory-garbage-collection-and-shared-state.md)
- [Artifact loader and runtime generations](../../../20-notes/components/artifact-loader-and-runtime-generations.md)
- P1-D02, P1-D03, P1-A02, and P1-GATE in the [milestone plan](README.md)

## Task identity, ownership, and dependencies

| Task ID | Area | Responsible owner | Requires | Requirement / artifact / acceptance IDs | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| p1-p02-worker-topologies | browser-host | Pascal Charbonneau (`pcharbon70`), experiment owner and runtime/concurrency reviewer | [p1-p01-handoff](phase-01-target-abi-and-language-probes.md) | P1-D02, P1-A02; `p1-worker-probes` | Both production-shaped topology probe results; not run. |
| p1-p02-worker-accounting | browser-host | Pascal Charbonneau (`pcharbon70`), experiment owner and lifecycle reviewer | p1-p02-worker-topologies | P1-A02; `p1-worker-accounting` | Isolation, exhaustion, responsiveness, abort, retry, and ownership metrics; not run. |
| p1-p02-fixed-memory | c-runtime | Pascal Charbonneau (`pcharbon70`), experiment owner and memory reviewer | [p1-p01-handoff](phase-01-target-abi-and-language-probes.md) | P1-D03, P1-A02; `p1-memory-probe` | Fixed-memory layout and deterministic ceiling failure evidence; not run. |
| p1-p02-controlled-start | cross-cutting | Pascal Charbonneau (`pcharbon70`), experiment owner and loader/runtime reviewer | [p1-p01-handoff](phase-01-target-abi-and-language-probes.md) | P1-D03, P1-A02; `p1-controlled-start-probe` | Instrumented proof that factory/instantiation does not call `main` or `erl_init`; not run. |
| p1-p02-integration | cross-cutting | Pascal Charbonneau (`pcharbon70`), independent reviewer | p1-p02-worker-topologies, p1-p02-worker-accounting, p1-p02-fixed-memory, p1-p02-controlled-start | P1-A02 | Integrated Worker/memory/start result; not run. |
| p1-p02-handoff | research-tools | Pascal Charbonneau (`pcharbon70`), milestone reviewer | p1-p02-integration | P1-A02 | Dated execution record and proceed/revise/blocked decision; not run. |

## Planned work

- [ ] 2 Phase — Worker, memory, and controlled-start probes.

  Produce comparable evidence for both browser Worker topologies under the
  same ABI, memory, startup, responsiveness, failure, and cleanup conditions.

  - [ ] 2.1 Section — Exercise concurrency, shared memory, and startup control.

    Build the production-shaped synthetic runtime shell and measure the
    browser behaviors required before a full ERTS artifact is attempted.

    - [ ] 2.1.1 Task [id: p1-p02-worker-topologies] [area: browser-host] [after: p1-p01-handoff] — Run a production-shaped pthread Wasm loader probe through both Worker topology candidates in Chrome and Firefox.

      Use identical artifacts, memory, pool assumptions, and lifecycle events
      for both candidates. Completion requires separate cold/warm results in
      each pinned browser without selecting a winner.

      - [ ] 2.1.1.1 Subtask — Execute the two-topology browser matrix.

        Record exact URLs, headers, browser versions, flags, Worker graphs,
        startup events, UI-heartbeat observations, failures, and cleanup for
        every candidate/browser combination.

    - [ ] 2.1.2 Task [id: p1-p02-worker-accounting] [area: browser-host] [after: p1-p02-worker-topologies] — Verify `crossOriginIsolated` inside every Worker, synthetic pthread-pool exhaustion mechanics, UI heartbeat responsiveness, abort/retry, and direct resource accounting. This probe does not establish the full ERTS pool size.

      Instrument every Worker host and supervisory resource so success and
      failure can be attributed directly. Completion requires prompt bounded
      exhaustion and cleanup rather than a scheduler-count inference.

      - [ ] 2.1.2.1 Subtask — Run isolation, exhaustion, responsiveness, and ownership cases.

        Vary synthetic pool demand around its declared capacity, abort at each
        state, retry with a fresh generation, and retain Worker, port, listener,
        timer, memory, and callback counts through settlement.

    - [ ] 2.1.3 Task [id: p1-p02-fixed-memory] [area: c-runtime] [after: p1-p01-handoff] — Probe fixed shared Wasm memory with `INITIAL_MEMORY == MAXIMUM_MEMORY`, including static data, all candidate Worker stacks, queue storage, and deliberate allocation failure at the declared ceiling.

      Account for all known regions and prove deterministic failure at the P0
      ceiling. Completion requires no hidden growth assumption or stale
      JavaScript view after termination.

      - [ ] 2.1.3.1 Subtask — Build and exhaust the fixed-memory fixture.

        Record linker settings and memory layout, exercise allocations below
        and at the ceiling across both topologies, and verify fatal generation
        cleanup for the deliberate failure.

    - [ ] 2.1.4 Task [id: p1-p02-controlled-start] [area: cross-cutting] [after: p1-p01-handoff] — Probe `-sINVOKE_RUN=0` with modularized output and the documented `noInitialRun` alternative under both Worker topologies. Instrument `main` and `erl_init` so factory/instantiation resolution proves neither ran.

      Compare both controlled-start mechanisms in actual generated glue and
      ensure the loader, not factory resolution, owns the sole future entry.
      Completion requires event traces proving no automatic entry.

      - [ ] 2.1.4.1 Subtask — Run instrumented factory, instantiate, abort, and retry paths.

        Capture generated configuration and traces for success and failure
        under both topologies, including duplicate factory resolution and stale
        generation attempts.

  - [ ] 2.2 Section — Phase 2 Integration Tests.

    Exercise each topology with the fixed-memory and controlled-start fixtures
    assembled, preserving UI progress and complete resource ownership across
    success, exhaustion, abort, and retry.

    - [ ] 2.2.1 Task [id: p1-p02-integration] [area: cross-cutting] [after: p1-p02-worker-topologies, p1-p02-worker-accounting, p1-p02-fixed-memory, p1-p02-controlled-start] — Verify the integrated Worker, memory, and controlled-start result.

      Pass only if both candidates run in both browsers, all Workers report the
      required isolation state, UI heartbeat remains observable, fixed-memory
      exhaustion and pool exhaustion are bounded, automatic entry is absent,
      and abort/retry settle all owned resources.

      - [ ] 2.2.1.1 Subtask — Run the assembled positive and bounded-failure matrix.

        Use pinned fixtures and predeclared limits; retain exact revisions,
        commands, browser automation, traces, resource samples, artifacts, and
        normalized outcomes.

      - [ ] 2.2.1.2 Subtask — Exercise stale, duplicate, exhaustion, and startup failures.

        Inject duplicate factory/start requests, missing isolation, pool N+1,
        memory-ceiling failure, cancellation, and late callbacks; require
        generation-local rejection and complete cleanup.

    - [ ] 2.2.2 Task [id: p1-p02-handoff] [area: research-tools] [after: p1-p02-integration] — Record evidence and decide the Phase 2 handoff.

      Publish comparable candidate evidence and decide whether both, one, or no
      topology may enter the delivery-path experiment. Do not select the final
      P3 topology in this handoff.

      - [ ] 2.2.2.1 Subtask — Publish the dated P1 Phase 2 execution record.

        Link artifacts and results to P1-A02 and task IDs with exact flags,
        browsers, Worker inventories, memory settings, limits, and failures.

      - [ ] 2.2.2.2 Subtask — Review completion and update the milestone.

        Keep unsupported, failed, or unrun cases visible and state precisely
        what Phase 3 must rerun through the manifest-bound delivery path.
