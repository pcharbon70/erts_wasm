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

Formal entry requires the reviewed `p0-p01-handoff` record from [Phase 1](phase-01-baseline-authority-and-runtime-inventory.md).
That review remains pending. The user authorized draft progression with the
dependency open; contract drafting and local validation are in progress, while
independent acceptance and runtime tests have not started. This phase defines
research and test contracts, not implementation or product approval.

The experimental ceilings protect the proof environment. They do not assert
performance or become product budgets. P0 freezes only the product-budget
derivation and anti-gaming method; numeric product values and their accountable
authority are deliberately deferred until after P6 and before C1. Future
implementation and evidence locations remain unresolved.

## Research and acceptance traceability

- [Planning conventions](../../README.md)
- [Canonical runtime architecture](../../../20-notes/erts-webassembly-runtime-architecture-and-milestones.md)
- [Minimum browser platform-contract inquiry](../../../40-inquiries/what-is-the-minimum-browser-platform-contract-for-upstream-erts.md)
- P0-D03, P0-A02, and P0-GATE in the [milestone plan](README.md)

## Task identity, ownership, and dependencies

| Task ID | Area | Responsible owner | Requires | Requirement / artifact / acceptance IDs | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| p0-p02-experiment-bounds | research-tools | Pascal Charbonneau (`pcharbon70`), measurement reviewer | [p0-p01-handoff](phase-01-baseline-authority-and-runtime-inventory.md) | P0-D03, P0-A02; `p0-experiment-bounds` | Reviewed premeasurement protocol; not run. |
| p0-p02-unsupported-bounds | research-tools | Pascal Charbonneau (`pcharbon70`), ERTS C-port and security reviewer | [p0-p01-handoff](phase-01-baseline-authority-and-runtime-inventory.md) | P0-A02; `p0-unsupported-matrix`, `p0-loader-bounds` | Machine-readable inventories and schema checks; not run. |
| p0-p02-product-budget-method | research-tools | Pascal Charbonneau (`pcharbon70`), method reviewer; final product authority deferred post-P6/pre-C1 | p0-p02-experiment-bounds | P0-D03, P0-A02; `p0-product-budget-method` | Independently reviewed method and explicit downstream approval point; product numbers are not P0 evidence. |
| p0-p02-evidence-profiles | unresolved | Pascal Charbonneau (`pcharbon70`), test/evidence reviewer | [p0-p01-handoff](phase-01-baseline-authority-and-runtime-inventory.md) | P0-A02; `p0-evidence-profile` | Reviewed native/Wasm evidence schema and profiles; not run. |
| p0-p02-integration | research-tools | Pascal Charbonneau (`pcharbon70`), independent reviewer | p0-p02-experiment-bounds, p0-p02-unsupported-bounds, p0-p02-product-budget-method, p0-p02-evidence-profiles | P0-A02 | Integrated limits and evidence-contract report; not run. |
| p0-p02-handoff | research-tools | Pascal Charbonneau (`pcharbon70`), milestone reviewer | p0-p02-integration | P0-A02 | Dated execution record and proceed/revise/blocked decision; not run. |

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

      - [x] 2.1.1.1 Subtask — Publish the premeasurement experiment protocol.

        Record every count, interval, ceiling, tolerance, measurement method,
        and breach disposition; verify timestamps and revision history show the
        values were frozen before results.

    - [ ] 2.1.2 Task [id: p0-p02-unsupported-bounds] [area: research-tools] [after: p0-p01-handoff] — Create a finite machine-readable unsupported-operation inventory for the POC and a loader/startup bounds matrix naming each resource's owner, unit, limit, enforcement point, mechanism, and breach action.

      Turn negative scope and resource ownership into enumerable inputs rather
      than prose-only promises. Completion requires schema-valid inventories
      with no unbounded or ownerless entry.

      - [x] 2.1.2.1 Subtask — Define, populate, and negatively validate both inventories.

        Include unsupported operations and every pre-ready artifact, byte,
        Worker, memory, queue, request, timer, and path bound; reject missing
        units, ambiguous owners, duplicate IDs, and absent breach actions.

    - [ ] 2.1.3 Task [id: p0-p02-product-budget-method] [area: research-tools] [after: p0-p02-experiment-bounds] — Define how product qualification budgets will be approved from named POC and native baselines before Program B, so later thresholds cannot be chosen to fit a completed implementation.

      Separate experimental safety from product acceptance and name the inputs,
      approval point, and anti-gaming rule. P0 completion requires independent
      review of this method, not appointment of the later product authority or
      numeric product values.

      - [x] 2.1.3.1 Subtask — Record the product-budget derivation and approval contract.

        Specify baseline identities, allowed derivations, required reviewer,
        freeze point, and change/reopening process without inventing numeric
        product values or an approver.

    - [ ] 2.1.4 Task [id: p0-p02-evidence-profiles] [area: unresolved] [after: p0-p01-handoff] — Define native and Wasm assertion/sanitizer/fuzz profiles, seed-corpus and coverage retention, failure minimization, and the POC SBOM/provenance schema.

      Define supported and unsupported instrumentation combinations and the
      evidence needed to reproduce, minimize, and compare failures across
      native and Wasm builds.

      - [x] 2.1.4.1 Subtask — Specify the evidence matrix and retention schema.

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

      - [x] 2.2.1.1 Subtask — Run schema, cross-reference, and consistency checks.

        Validate machine-readable inputs, resolve task/artifact IDs, and record
        the exact corpus revision, commands, outputs, and unresolved authority.

      - [x] 2.2.1.2 Subtask — Exercise anti-gaming and malformed-contract cases.

        Reject post-result threshold edits, missing owners or units, infinite
        test series, silent sanitizer omission, orphaned fuzz failures, and
        product budgets copied from experimental safety ceilings.

    - [ ] 2.2.2 Task [id: p0-p02-handoff] [area: research-tools] [after: p0-p02-integration] — Record evidence and decide the Phase 2 handoff.

      Preserve actual validation output and a proceed/revise/blocked decision.
      The product authority and numeric values remain explicitly deferred; they
      block C1 only if still absent after P6, not P0 or P1.

      - [x] 2.2.2.1 Subtask — Publish the dated Phase 2 execution record.

        Link evidence to P0-A02 and task IDs with exact revisions, commands,
        schema versions, results, failures, and limitations.

      - [ ] 2.2.2.2 Subtask — Review completion and update the milestone.

        Confirm Phase 3 receives immutable experiment and evidence contracts;
        leave any unproved or unapproved item unchecked.
