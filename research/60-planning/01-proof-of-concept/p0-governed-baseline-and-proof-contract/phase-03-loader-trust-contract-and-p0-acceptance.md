---
title: "Phase 3 — Loader trust contract and P0 acceptance"
kind: note
created: "2026-09-14"
maturity: developing
tags:
  - implementation-planning
  - proof-of-concept
  - runtime-loading
  - security
aliases: []
---

# Phase 3 — Loader trust contract and P0 acceptance

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.proof_of_concept.p0.phase_03
entities:
  - id: planning.erts_wasm.proof_of_concept.p0.phase_03
    kind: phase
    source_anchor: '#phase-3-loader-trust-contract-and-p0-acceptance'
relations:
  - subject: planning.erts_wasm.proof_of_concept.p0.phase_03
    predicate: belongs_to
    object: planning.erts_wasm.proof_of_concept.p0.plan
```

Freeze the manifest, generation, and executable-root trust contracts, then
evaluate whether the complete governance baseline is fit to enter P1.

Back to milestone: [P0 plan](README.md).

## Entry, scope, and dependencies

Formal entry requires accepted `p0-p02-handoff` evidence from [Phase 2](phase-02-bounds-budgets-and-evidence-contracts.md).
That evidence remains open. The user authorized draft progression with the
dependency open; contract drafting and local validation are in progress, while
independent acceptance and browser execution have not started. This phase owns
the loader and delivery contract in the corpus, not a browser loader
implementation.

The root trust choice remains open until its decision task is reviewed. A
secure context, cross-origin isolation, recursive Worker delivery policy, and
the required trust boundary are mandatory; inability to support them triggers
the P0 stop condition rather than a silent scope reduction.

## Research and acceptance traceability

- [Planning conventions](../../README.md)
- [Runtime roadmap and ordering rules](../../erts-webassembly-runtime-milestones.md)
- [Artifact loader and runtime generations](../../../20-notes/components/artifact-loader-and-runtime-generations.md)
- [Canonical runtime architecture](../../../20-notes/erts-webassembly-runtime-architecture-and-milestones.md)
- P0-D02, P0-A03, and P0-GATE in the [milestone plan](README.md)

## Task identity, ownership, and dependencies

| Task ID | Area | Responsible owner | Requires | Requirement / artifact / acceptance IDs | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| p0-p03-loader-contract | research-tools | Loader/protocol reviewer unassigned | [p0-p02-handoff](phase-02-bounds-budgets-and-evidence-contracts.md) | P0-A03; `p0-loader-contract` | Contract drafted and locally validated; independent review pending. |
| p0-p03-bootstrap-trust | research-tools | Security reviewer unassigned | [p0-p02-handoff](phase-02-bounds-budgets-and-evidence-contracts.md) | P0-D02, P0-A03; `p0-bootstrap-trust` | First-proof choice locally validated; security/deployment review pending. |
| p0-p03-integration | cross-cutting | Independent reviewer unassigned | p0-p03-loader-contract, p0-p03-bootstrap-trust | P0-GATE | Local contract/negative report blocked on formal evidence and review. |
| p0-p03-handoff | research-tools | Milestone reviewer unassigned | p0-p03-integration | P0-GATE | [Dated blocked execution record](../../../50-journal/2026-09-15-p0-phase-03-loader-trust-and-acceptance-execution.md); no closure evidence. |

## Planned work

- [ ] 3 Phase — Loader trust contract and P0 acceptance.

  Establish the preimplementation loading authority and prove that all P0
  contracts compose without an unowned asset, transition, resource, or trust
  assumption.

  - [ ] 3.1 Section — Freeze loading authority and delivery trust.

    Specify what the browser may load, in what order, under whose authority,
    and how every failure or stale generation is rejected before runtime
    execution.

    - [ ] 3.1.1 Task [id: p0-p03-loader-contract] [area: research-tools] [after: p0-p02-handoff] — Specify the manifest schema, fixed argv/environment/root/path/cwd, topology-specific loader partial order, immutable module set, loading failure matrix, runtime identity attestation, and generation ownership rules.

      Bind every preflight input and loader transition to a versioned schema,
      owner, bound, and failure action. Completion requires explicit states and
      testable rejection behavior without assuming a topology winner.

      - [x] 3.1.1.1 Subtask — Author and validate the complete loader contract.

        Define manifest fields, state transitions, identities, partial orders,
        module closure, generation tokens, cleanup ownership, and malformed,
        stale, duplicate, skewed, and out-of-bounds cases.

    - [ ] 3.1.2 Task [id: p0-p03-bootstrap-trust] [area: research-tools] [after: p0-p02-handoff] — Select the root executable trust anchor and document origin, header, redirect, cache, service-worker, CSP, Worker-integrity, and Wasm streaming policy. Do not claim that a generated loader authenticates itself.

      Compare feasible root-trust choices against the deployment and attacker
      model. Completion requires an explicit decision, trusted-base inventory,
      delivery matrix, and rejection of circular self-authentication.

      - [x] 3.1.2.1 Subtask — Resolve and adversarially review the bootstrap trust rule.

        Record the selected root, authority chain, required headers and browser
        features, redirect/cache/service-worker behavior, Worker delivery, and
        streaming-versus-verification tradeoff with negative cases.

  - [ ] 3.2 Section — Phase 3 Integration Tests.

    Evaluate the complete P0 baseline and the loader/trust contract in a
    reproducible empty target environment before any P1 probe begins.

    - [ ] 3.2.1 Task [id: p0-p03-integration] [area: cross-cutting] [after: p0-p03-loader-contract, p0-p03-bootstrap-trust] — Reviewed baseline, asset/dependency/patch ledger, trust anchor, bounds and unsupported-operation inventories, loader protocol, and reproducible empty target environment exist.

      This is the original P0 gate. Pass only if every earlier P0 artifact is
      present, mutually consistent, independently reviewable, and reproducible;
      an unresolved required item or active stop trigger fails or blocks it.

      - [x] 3.2.1.1 Subtask — Run the integrated P0 acceptance review.

        Assemble P0-A01 through P0-A03 at exact revisions, validate schemas and
        links, reproduce the empty environment, and record every pass, failure,
        limitation, command, and artifact identity.

      - [x] 3.2.1.2 Subtask — Exercise trust, bounds, and contradiction failures.

        Require deterministic rejection for missing or floating inputs,
        circular loader trust, mixed identities, ownerless resources, bounds
        without breach actions, undeclared modules, and unsupported deployment
        prerequisites.

    - [ ] 3.2.2 Task [id: p0-p03-handoff] [area: research-tools] [after: p0-p03-integration] — Record evidence and decide the P0-to-P1 handoff.

      Publish the plan baseline, tested corpus revision and dirty state,
      environment recipe, commands, results, review, and proceed/revise/blocked
      decision. This handoff unlocks probes, not a runtime claim.

      - [x] 3.2.2.1 Subtask — Publish the dated P0 execution record.

        Link all P0 artifacts and acceptance IDs, record the root-trust
        decision and unresolved owners, and distinguish validation from unrun
        C/Emscripten behavior.

      - [ ] 3.2.2.2 Subtask — Review milestone closure and update planning state.

        Mark P0 complete only after the original gate passes; otherwise retain
        unchecked work and record the precise revision or decision needed.
