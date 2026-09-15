---
title: "Phase 2 — Bounds, budgets, and evidence contracts"
kind: note
created: "2026-09-14"
maturity: developing
tags:
  - governance
  - implementation-planning
  - proof-of-concept
  - resource-bounds
aliases: []
---

# Phase 2 — Bounds, budgets, and evidence contracts

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.proof_of_concept.p0.phase_02
entities:
  - id: planning.erts_wasm.proof_of_concept.p0.phase_02
    kind: phase
    source_anchor: '#phase-2-bounds-budgets-and-evidence-contracts'
relations:
  - subject: planning.erts_wasm.proof_of_concept.p0.phase_02
    predicate: belongs_to
    object: planning.erts_wasm.proof_of_concept.p0.plan
  - subject: planning.erts_wasm.proof_of_concept.p0.phase_02
    predicate: precedes
    object: planning.erts_wasm.proof_of_concept.p0.phase_03
```

Freeze the experimental safety envelope, unsupported-operation and resource
bounds, future product-budget method, and reproducible evidence profiles before
measurements can influence them.

Back to milestone: [P0 plan](README.md).

## Entry, scope, and dependencies

Entry requires the reviewed `p0-p01-handoff` record from [Phase 1](phase-01-baseline-authority-and-runtime-inventory.md).
Plan review is pending; execution and tests have not started. This phase
defines research and test contracts, not implementation or product approval.

The experimental ceilings protect the proof environment. They do not assert
performance or become product budgets. Product authority remains unassigned,
and the future implementation and evidence locations remain unresolved.

## Research and acceptance traceability

- [Planning conventions](../../README.md)
- [Canonical runtime architecture](../../../20-notes/erts-webassembly-runtime-architecture-and-milestones.md)
- [Minimum browser platform-contract inquiry](../../../40-inquiries/what-is-the-minimum-browser-platform-contract-for-upstream-erts.md)
- P0-D03, P0-A02, and P0-GATE in the [milestone plan](README.md)

## Task identity, ownership, and dependencies

| Task ID | Area | Responsible owner | Requires | Requirement / artifact / acceptance IDs | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| p0-p02-experiment-bounds | research-tools | Measurement reviewer unassigned | [p0-p01-handoff](phase-01-baseline-authority-and-runtime-inventory.md) | P0-D03, P0-A02; `p0-experiment-bounds` | Reviewed premeasurement protocol; not run. |
| p0-p02-unsupported-bounds | research-tools | ERTS C-port and security reviewers unassigned | [p0-p01-handoff](phase-01-baseline-authority-and-runtime-inventory.md) | P0-A02; `p0-unsupported-matrix`, `p0-loader-bounds` | Machine-readable inventories and schema checks; not run. |
| p0-p02-product-budget-method | research-tools | Product-budget authority unassigned | p0-p02-experiment-bounds | P0-D03, P0-A02; `p0-product-budget-method` | Approved method or explicit blocker; not run. |
| p0-p02-evidence-profiles | unresolved | Test/evidence reviewer unassigned | [p0-p01-handoff](phase-01-baseline-authority-and-runtime-inventory.md) | P0-A02; `p0-evidence-profile` | Reviewed native/Wasm evidence schema and profiles; not run. |
| p0-p02-integration | research-tools | Independent reviewer unassigned | p0-p02-experiment-bounds, p0-p02-unsupported-bounds, p0-p02-product-budget-method, p0-p02-evidence-profiles | P0-A02 | Integrated limits and evidence-contract report; not run. |
| p0-p02-handoff | research-tools | Milestone reviewer unassigned | p0-p02-integration | P0-A02 | Dated execution record and proceed/revise/blocked decision; not run. |

## Planned work

- [ ] 2 Phase — Bounds, budgets, and evidence contracts.

  Establish immutable premeasurement rules so later success, failure, size,
  latency, resource, sanitizer, and fuzz results cannot silently redefine the
  proof.

  - [ ] 2.1 Section — Define bounded experiments and evidence ownership.

    Specify quantitative limits, breach behavior, unsupported facilities,
    product-budget governance, and retention requirements as one coherent
    contract.

    - [ ] 2.1.1 Task [id: p0-p02-experiment-bounds] [area: research-tools] [after: p0-p01-handoff] — Set the finite boot/dispose cycle count, settling interval, noise envelope, experimental safety ceilings, and semantic comparison rules before measurement. These ceilings protect the experiment; they are not product qualification budgets.

      Define units, sampling, warm/cold separation, tolerated environmental
      variation, stop behavior, and review authority. Completion requires a
      versioned protocol whose values precede all P1 runs.

      - [ ] 2.1.1.1 Subtask — Publish the premeasurement experiment protocol.

        Record every count, interval, ceiling, tolerance, measurement method,
        and breach disposition; verify timestamps and revision history show the
        values were frozen before results.

    - [ ] 2.1.2 Task [id: p0-p02-unsupported-bounds] [area: research-tools] [after: p0-p01-handoff] — Create a finite machine-readable unsupported-operation inventory for the POC and a loader/startup bounds matrix naming each resource's owner, unit, limit, enforcement point, mechanism, and breach action.

      Turn negative scope and resource ownership into enumerable inputs rather
      than prose-only promises. Completion requires schema-valid inventories
      with no unbounded or ownerless entry.

      - [ ] 2.1.2.1 Subtask — Define, populate, and negatively validate both inventories.

        Include unsupported operations and every pre-ready artifact, byte,
        Worker, memory, queue, request, timer, and path bound; reject missing
        units, ambiguous owners, duplicate IDs, and absent breach actions.

    - [ ] 2.1.3 Task [id: p0-p02-product-budget-method] [area: research-tools] [after: p0-p02-experiment-bounds] — Define how product qualification budgets will be approved from named POC and native baselines before Program B, so later thresholds cannot be chosen to fit a completed implementation.

      Separate experimental safety from product acceptance and name the inputs,
      approval point, and anti-gaming rule. Completion requires approval by the
      actual authority or an explicit unresolved blocker.

      - [ ] 2.1.3.1 Subtask — Record the product-budget derivation and approval contract.

        Specify baseline identities, allowed derivations, required reviewer,
        freeze point, and change/reopening process without inventing numeric
        product values or an approver.

    - [ ] 2.1.4 Task [id: p0-p02-evidence-profiles] [area: unresolved] [after: p0-p01-handoff] — Define native and Wasm assertion/sanitizer/fuzz profiles, seed-corpus and coverage retention, failure minimization, and the POC SBOM/provenance schema.

      Define supported and unsupported instrumentation combinations and the
      evidence needed to reproduce, minimize, and compare failures across
      native and Wasm builds.

      - [ ] 2.1.4.1 Subtask — Specify the evidence matrix and retention schema.

        Name build variants, flags, tool versions, seed identities, coverage
        outputs, minimization records, SBOM fields, provenance links, and the
        handling of unsupported combinations.

  - [ ] 2.2 Section — Phase 2 Integration Tests.

    Validate the bounds and evidence contracts together so each measurable
    resource, unsupported behavior, test profile, and future product decision
    has one owner and non-circular acceptance rule.

    - [ ] 2.2.1 Task [id: p0-p02-integration] [area: research-tools] [after: p0-p02-experiment-bounds, p0-p02-unsupported-bounds, p0-p02-product-budget-method, p0-p02-evidence-profiles] — Verify the integrated bounds, budget, and evidence contract.

      Pass only if every value is frozen before measurement, experimental and
      product criteria are distinct, all bounded resources and unsupported
      operations are enumerable, and every required result has a retention
      path.

      - [ ] 2.2.1.1 Subtask — Run schema, cross-reference, and consistency checks.

        Validate machine-readable inputs, resolve task/artifact IDs, and record
        the exact corpus revision, commands, outputs, and unresolved authority.

      - [ ] 2.2.1.2 Subtask — Exercise anti-gaming and malformed-contract cases.

        Reject post-result threshold edits, missing owners or units, infinite
        test series, silent sanitizer omission, orphaned fuzz failures, and
        product budgets copied from experimental safety ceilings.

    - [ ] 2.2.2 Task [id: p0-p02-handoff] [area: research-tools] [after: p0-p02-integration] — Record evidence and decide the Phase 2 handoff.

      Preserve actual validation output and a proceed/revise/blocked decision.
      A missing product authority may remain visible without fabricating
      approval, but the required pre-C1 freeze remains blocking.

      - [ ] 2.2.2.1 Subtask — Publish the dated Phase 2 execution record.

        Link evidence to P0-A02 and task IDs with exact revisions, commands,
        schema versions, results, failures, and limitations.

      - [ ] 2.2.2.2 Subtask — Review completion and update the milestone.

        Confirm Phase 3 receives immutable experiment and evidence contracts;
        leave any unproved or unapproved item unchecked.
