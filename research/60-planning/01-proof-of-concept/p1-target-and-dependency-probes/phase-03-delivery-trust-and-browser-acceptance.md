---
title: "Phase 3 — Delivery trust and browser acceptance"
kind: note
created: "2026-09-14"
maturity: developing
tags:
  - browser
  - implementation-planning
  - proof-of-concept
  - runtime-loading
  - security
aliases: []
---

# Phase 3 — Delivery trust and browser acceptance

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.proof_of_concept.p1.phase_03
entities:
  - id: planning.erts_wasm.proof_of_concept.p1.phase_03
    kind: phase
    source_anchor: '#phase-3-delivery-trust-and-browser-acceptance'
relations:
  - subject: planning.erts_wasm.proof_of_concept.p1.phase_03
    predicate: belongs_to
    object: planning.erts_wasm.proof_of_concept.p1.plan
```

Rerun the production-shaped pthread probe through the proposed manifest,
delivery, verification, cancellation, and root-trust path, then decide whether
the browser/toolchain runway is sufficient for P2.

Back to milestone: [P1 plan](README.md).

## Entry, scope, and dependencies

Entry requires accepted `p1-p02-handoff` evidence from [Phase 2](phase-02-worker-memory-and-controlled-start-probes.md).
Plan review is pending; execution and tests have not started. Browser-host,
build/release, and research evidence areas participate; implementation
locations and named reviewers remain unresolved.

This phase does not use an inline developer loader, select a final P3 topology,
or claim ERTS compilation or boot. It must apply the P0 trust anchor and bounds
to actual browser delivery in pinned Chrome and Firefox.

## Research and acceptance traceability

- [Planning conventions](../../README.md)
- [Artifact loader and runtime generations](../../../20-notes/components/artifact-loader-and-runtime-generations.md)
- [Worker and pthread topology](../../../20-notes/components/worker-and-pthread-topology.md)
- [Security, observability, and supply chain](../../../20-notes/components/security-observability-and-supply-chain.md)
- P1-A03 and P1-GATE in the [milestone plan](README.md)

## Task identity, ownership, and dependencies

| Task ID | Area | Responsible owner | Requires | Requirement / artifact / acceptance IDs | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| p1-p03-manifest-delivery | build-release | Loader/delivery reviewer unassigned | [p1-p02-handoff](phase-02-worker-memory-and-controlled-start-probes.md) | P1-A03; `p1-delivery-matrix` | Manifest-bound positive, cancellation, and bounds evidence; not run. |
| p1-p03-bootstrap-trust | browser-host | Security reviewer unassigned | [p1-p02-handoff](phase-02-worker-memory-and-controlled-start-probes.md) | P1-A03; `p1-bootstrap-negative-matrix` | Trust-root, cache, Worker, streaming, and generation-negative evidence; not run. |
| p1-p03-integration | cross-cutting | Independent reviewer unassigned | p1-p03-manifest-delivery, p1-p03-bootstrap-trust | P1-GATE | Full Chrome/Firefox P1 matrix and stop-condition assessment; not run. |
| p1-p03-handoff | research-tools | Milestone reviewer unassigned | p1-p03-integration | P1-GATE | Dated execution record and proceed/revise/blocked decision; not run. |

## Planned work

- [ ] 3 Phase — Delivery trust and browser acceptance.

  Prove that the same bounded probe artifacts traverse the intended production
  delivery and trust boundary, remain responsive, and terminate without a
  mixed or stale generation.

  - [ ] 3.1 Section — Exercise manifest delivery and executable-root trust.

    Apply the P0 contracts to actual URLs, response policy, verification,
    Workers, Wasm compilation, cancellation, caches, and generation identity.

    - [ ] 3.1.1 Task [id: p1-p03-manifest-delivery] [area: build-release] [after: p1-p02-handoff] — Load the probe through the proposed manifest, URL, header, MIME, cache, verification, Worker, and cancellation paths rather than a developer-only inline loader.

      Package and serve a version-closed generation using the declared bounds
      and loading state machine. Completion requires observable success,
      cancellation, timeout, and cleanup at each delivery transition.

      - [ ] 3.1.1.1 Subtask — Execute the manifest-bound delivery and cancellation matrix.

        Record manifest and artifact hashes, response headers, URLs, browser
        versions, cache state, Worker graph, load events, cancellation points,
        resource settlement, and normalized outcomes.

    - [ ] 3.1.2 Task [id: p1-p03-bootstrap-trust] [area: browser-host] [after: p1-p02-handoff] — Test the P0 bootstrap trust rule, redirects, cache and service-worker policy, generation mixing, Worker executable delivery, and pre-verification versus streaming behavior.

      Attack the executable-root and generation boundary using the exact P0
      policy. Completion requires deterministic rejection or explicitly
      bounded fallback for every case without self-authentication claims.

      - [ ] 3.1.2.1 Subtask — Run the bootstrap, delivery-policy, and mixed-generation negative matrix.

        Exercise allowed and disallowed origins, redirects, headers, cache/SW
        states, stale Worker scripts, skewed Wasm/glue, verification failures,
        and streaming fallback; retain actual network and loader traces.

  - [ ] 3.2 Section — Phase 3 Integration Tests.

    Run the complete production-shaped pthread probe across both candidate
    topologies and pinned browsers through the real delivery path, including
    abort, restart, and settlement.

    - [ ] 3.2.1 Task [id: p1-p03-integration] [area: cross-cutting] [after: p1-p03-manifest-delivery, p1-p03-bootstrap-trust] — The production-shaped pthread probe successfully loads, stays UI-responsive, aborts, restarts, and completely cleans up in pinned Chrome and Firefox; otherwise the program records a stop condition. A reproducible matrix records every command, artifact, import, Worker, pass, failure, and localized patch.

      This is the original P1 gate. Pass only if the Phase 1 ABI and authority
      results and Phase 2 Worker/memory/start behavior also hold through actual
      delivery; isolated component successes are insufficient.

      - [ ] 3.2.1.1 Subtask — Run the full positive, abort, restart, and cleanup matrix.

        Use the pinned P0 environment and predeclared limits; capture complete
        commands, artifacts, imports, Workers, events, UI heartbeat, resource
        samples, normalized results, failures, and localized patches.

      - [ ] 3.2.1.2 Subtask — Exercise all mandatory P1 negative and stop cases.

        Include target/ABI faults, missing isolation, pool and memory
        exhaustion, automatic entry, malformed manifests, wrong MIME/headers,
        redirects, cache/SW skew, mixed generations, cancellation, timeout,
        stale callbacks, and incomplete cleanup.

    - [ ] 3.2.2 Task [id: p1-p03-handoff] [area: research-tools] [after: p1-p03-integration] — Record evidence and decide the P1-to-P2 handoff.

      Publish the tested revisions, dirty state, exact tools and browsers,
      commands, artifacts, matrices, limitations, patch localization, ADR-0001
      review input, and proceed/revise/blocked decision.

      - [ ] 3.2.2.1 Subtask — Publish the dated P1 execution record.

        Link P1-A01 through P1-GATE and all stable task IDs to actual evidence;
        identify unsupported combinations and active stop triggers.

      - [ ] 3.2.2.2 Subtask — Review milestone closure and update planning state.

        Mark P1 complete only when the original gate passes. A successful P1
        unlocks browser/toolchain runway and P2 decomposition, not an ERTS
        build, boot, topology decision, or compatibility claim.
