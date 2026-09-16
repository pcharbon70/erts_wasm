---
title: "Phase 1 — Baseline authority and runtime inventory"
kind: note
created: "2026-09-14"
maturity: developing
tags:
  - governance
  - implementation-planning
  - proof-of-concept
  - runtime-loading
aliases: []
---

# Phase 1 — Baseline authority and runtime inventory

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.proof_of_concept.p0.phase_01
entities:
  - id: planning.erts_wasm.proof_of_concept.p0.phase_01
    kind: phase
    source_anchor: '#phase-1-baseline-authority-and-runtime-inventory'
relations:
  - subject: planning.erts_wasm.proof_of_concept.p0.phase_01
    predicate: belongs_to
    object: planning.erts_wasm.proof_of_concept.p0.plan
  - subject: planning.erts_wasm.proof_of_concept.p0.phase_01
    predicate: precedes
    object: planning.erts_wasm.proof_of_concept.p0.phase_02
```

Freeze the exact upstream, toolchain, browser, authority, runtime-dependency,
and thread-census inputs that later probes must use.

Back to milestone: [P0 plan](README.md).

## Entry, scope, and dependencies

Entry requires only the accepted research-corpus scope. Plan review,
contract drafting, local validation, exact input materialization, and
pinned-source reproduction are complete; C/Emscripten implementation probes
have not started. This phase owns planning
and source-audit artifacts in the research corpus. The future C/Emscripten
implementation location remains unresolved. Pascal Charbonneau (`pcharbon70`)
accepted the explicit owner-review packet and its recorded limitations on
2026-09-16; pass-closing evidence now binds the accepted result.

The phase materializes and verifies the same-source native OTP bootstrap but
does not compile ERTS for WebAssembly or accept ADR-0001. It freezes the
candidate inputs and the measurements that P1 must perform without granting
ambient host authority or broadening the proof claim.

## Research and acceptance traceability

- [Planning conventions](../../README.md)
- [Runtime roadmap](../../erts-webassembly-runtime-milestones.md)
- [Canonical runtime architecture](../../../20-notes/erts-webassembly-runtime-architecture-and-milestones.md)
- [ADR-0001](../../../20-notes/architecture-decisions/adr-0001-implementation-languages-and-beam-qualification-sequence.md)
- P0 acceptance cases P0-A01 and P0-GATE in the [milestone plan](README.md)

## Task identity, ownership, and dependencies

| Task ID | Area | Responsible owner | Requires | Requirement / artifact / acceptance IDs | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| p0-p01-pins | research-tools | Pascal Charbonneau (`pcharbon70`), build/reproducibility reviewer | None | P0-A01; `p0-baseline` | Exact inputs materialized, owner-accepted, and evidence-bound. |
| p0-p01-trust-boundary | research-tools | Pascal Charbonneau (`pcharbon70`), security reviewer | None | P0-A01; `p0-trust-model` | Boundary and contradiction matrix owner-accepted and evidence-bound. |
| p0-p01-language-ownership | research-tools | Pascal Charbonneau (`pcharbon70`), architecture reviewer | None | P0-D01; `p0-language-ownership` | P0 contract owner-accepted; ADR-0001 remains proposed pending P1. |
| p0-p01-runtime-inventory | cross-cutting | Pascal Charbonneau (`pcharbon70`), ERTS C-port reviewer | p0-p01-pins | P0-A01; `p0-runtime-inventory` | Reproduced, corrected, owner-accepted, and evidence-bound. |
| p0-p01-thread-census | unresolved | Pascal Charbonneau (`pcharbon70`), runtime/concurrency reviewer | p0-p01-runtime-inventory | P0-A01; `p0-thread-census-contract` | N/N-1 contract owner-accepted; runtime execution remains deferred. |
| p0-p01-integration | research-tools | Pascal Charbonneau (`pcharbon70`), independent reviewer | p0-p01-pins, p0-p01-trust-boundary, p0-p01-language-ownership, p0-p01-runtime-inventory, p0-p01-thread-census | P0-A01 | Integrated validation owner-accepted and evidence-bound. |
| p0-p01-handoff | research-tools | Pascal Charbonneau (`pcharbon70`), milestone reviewer | p0-p01-integration | P0-A01 | P0-A01 handoff accepted and evidence-bound. |

## Planned work

- [x] 1 Phase — Baseline authority and runtime inventory.

  Establish a single reproducible identity and ownership baseline, plus the
  inventories and census contract needed to make later C/Emscripten results
  comparable and falsifiable.

  - [x] 1.1 Section — Freeze authority, source, and runtime inputs.

    Define what later probes are allowed to vary and identify the runtime edges
    they must measure without treating inspection as execution evidence.

    - [x] 1.1.1 Task [id: p0-p01-pins] [area: research-tools] [after: none] — Pin OTP 29.0.6 / ERTS 17.0.6 commit `e07fd07837e5aa845657f5fa340637121e451d47`, the same-release native bootstrap, emsdk/LLVM/Binaryen, build image, Chrome, and Firefox.

      Produce one reviewable ledger of exact versions, revisions, hashes, and
      acquisition origins. Completion requires that a clean environment can
      resolve the same identities without substituting floating versions.

      - [x] 1.1.1.1 Subtask — Record and independently resolve every pinned identity.

        Capture source and binary identities, expected digests, tool version
        commands, browser channels, and any unresolved acquisition limitation;
        verify the ledger from a clean target description.

    - [x] 1.1.2 Task [id: p0-p01-trust-boundary] [area: research-tools] [after: none] — Review trust zones, protected assets, attackers, non-goals, topology candidates, import ABI, quotas, patch policy, and stop conditions.

      Reconcile the architecture's security boundary with the intended browser
      deployment. Completion requires explicit ownership, authority, and stop
      criteria for every listed concern.

      - [x] 1.1.2.1 Subtask — Produce the reviewed trust and scope matrix.

        Map assets, actors, boundaries, candidate topologies, imported powers,
        quotas, patch ownership, and rejection conditions; test the document
        against contradictory authority and deployment examples.

    - [x] 1.1.3 Task [id: p0-p01-language-ownership] [area: research-tools] [after: none] — Review [ADR-0001](../../../20-notes/architecture-decisions/adr-0001-implementation-languages-and-beam-qualification-sequence.md) and record language/toolchain ownership, compiler and package-manager pins, generated artifacts, ABI owners, and evidence that would trigger a new decision. The ADR remains proposed until P1 passes.

      Keep source ownership distinct from emitted artifact formats and security
      validation. Completion requires a trace from every proposed language and
      generated output to its P1 acceptance evidence and review trigger.

      - [x] 1.1.3.1 Subtask — Reconcile ADR-0001 with the pinned build and ABI ledger.

        Record C, TypeScript/JavaScript, Erlang/BEAM, and deferred-language
        ownership; flag any missing pin or owner without accepting the ADR.

    - [x] 1.1.4 Task [id: p0-p01-runtime-inventory] [area: cross-cutting] [after: p0-p01-pins] — Inventory startup threads, syscalls, `sys.h` services, preloads, boot modules, allocator/poll/time dependencies, native edges, loader entry points, code indices, literals, purgers, and required `on_load` hooks.

      Derive a reproducible inventory from the pinned upstream revision and
      distinguish source facts, inferred reachability, and unresolved runtime
      behavior. Completion requires every category to have a search method and
      recorded result, including negative findings.

      - [x] 1.1.4.1 Subtask — Run and retain the pinned-source inventory procedure.

        Record exact search commands, source paths and revisions, classified
        edges, unknowns, and review notes so P1 can localize probe failures.

    - [x] 1.1.5 Task [id: p0-p01-thread-census] [area: unresolved] [after: p0-p01-runtime-inventory] — Record the pinned-source candidate ERTS/POSIX thread roles and define separate instrumented censuses for logical roles, actual Emscripten pthread Worker hosts/pool slots, and page/root supervisory agents. Require a measured pool-size `N`/`N-1` full-runtime boot test rather than deriving `N` from `+S`.

      Define distinct identities and measurements for ERTS roles, pthread
      hosts, pool capacity, and browser supervisors. Completion requires an
      executable census contract and an explicit prohibition on inferring N
      from scheduler count.

      - [x] 1.1.5.1 Subtask — Specify census events, counters, owners, and N/N-1 outcomes.

        Name the instrumentation seam, output schema, lifecycle interval, and
        expected prompt failure and cleanup at N-1; leave the implementation
        location unresolved until selected.

  - [x] 1.2 Section — Phase 1 Integration Tests.

    Review the combined baseline as a contract: every downstream identity and
    authority must resolve exactly once, and every runtime/thread concern must
    have a measurable disposition without claiming a compile or boot.

    - [x] 1.2.1 Task [id: p0-p01-integration] [area: research-tools] [after: p0-p01-pins, p0-p01-trust-boundary, p0-p01-language-ownership, p0-p01-runtime-inventory, p0-p01-thread-census] — Verify the integrated baseline and inventory contract.

      Assemble the pin ledger, trust model, language ownership, source
      inventory, and census contract. Pass only if there are no conflicting
      identities, missing owners, silent runtime categories, or circular
      assumptions between topology and thread count.

      - [x] 1.2.1.1 Subtask — Run the integrated contract-consistency review.

        Use the pinned corpus revision and declared review checklist to verify
        completeness, links, identities, negative findings, and explicit
        unknowns; retain the result by P0-A01 and task ID.

      - [x] 1.2.1.2 Subtask — Exercise contradiction and omission cases.

        Inject a floating or unmaterialized tool version, missing browser
        digest, duplicate authority, missing TypeScript pin, missing or stale
        runtime inventory data, topology-selected census, and `+S 1:1`-derived
        pool size; require deterministic rejection by the review contract.

    - [x] 1.2.2 Task [id: p0-p01-handoff] [area: research-tools] [after: p0-p01-integration] — Record evidence and decide the Phase 1 handoff.

      Record the exact plan and corpus revisions, dirty state, commands,
      reviewed artifacts, failures, limitations, and proceed/revise/blocked
      decision. Unresolved required input blocks Phase 2.

      - [x] 1.2.2.1 Subtask — Publish the dated Phase 1 execution record.

        Link the journal evidence to P0-A01 and every task ID, distinguishing
        inspected facts from unrun implementation probes.

      - [x] 1.2.2.2 Subtask — Review completion and update the milestone.

        Roll up the task, section, and phase checkboxes only after their
        descendants and required review evidence are complete; record which
        exact inputs Phase 2 may consume.

Pass-closing evidence: [`p0-phase-01-acceptance.planning-evidence.json`](../../../assets/p0-governed-baseline/phase-01/p0-phase-01-acceptance.planning-evidence.json)
binds all seven Phase 1 tasks and P0-A01 to clean reviewed revision `aaff05d`.
It does not accept ADR-0001 or any Phase 2, Phase 3, or runtime result.
