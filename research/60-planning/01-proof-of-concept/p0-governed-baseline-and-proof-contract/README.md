---
title: "P0 — Governed baseline and proof contract"
kind: map
created: "2026-09-14"
tags:
  - archive-navigation
  - directory-index
  - governance
  - implementation-planning
  - proof-of-concept
  - runtime-loading
aliases: []
---

# P0 — Governed baseline and proof contract

```planning-meta
profile: planning.authoring.v1
document_id: planning.erts_wasm.proof_of_concept.p0
entities:
  - id: planning.erts_wasm.proof_of_concept.p0
    kind: milestone
    source_anchor: '#p0-governed-baseline-and-proof-contract'
  - id: planning.erts_wasm.proof_of_concept.p0.plan
    kind: plan
    source_anchor: '#ordered-phases'
relations:
  - subject: planning.erts_wasm.proof_of_concept.p0
    predicate: belongs_to
    object: planning.erts_wasm.proof_of_concept
  - subject: planning.erts_wasm.proof_of_concept.p0
    predicate: contains
    object: planning.erts_wasm.proof_of_concept.p0.plan
  - subject: planning.erts_wasm.proof_of_concept.p0
    predicate: precedes
    object: planning.erts_wasm.proof_of_concept.p1
```

## Purpose

Freeze exactly what the proof may establish before building it. The phases
establish pinned authority and source inventories, quantitative bounds and
evidence contracts, then the loader and root-trust contract required before
the first implementation probe.

## What belongs here

Toolchain and browser pins, trust and authority decisions, source/runtime
inventories, experimental bounds, unsupported-operation contracts, evidence
profiles, manifest and generation rules, and root executable trust belong
here. Compile, instantiate, boot, or compatibility claims do not.

## Planning and delivery state

Plan: authored, review pending. Execution: not started. Tests and P0 gate: not
run. Every task and source obligation remains unchecked. ADR-0001 remains
proposed until P1 evidence supplies its review trigger.

## Authoritative inputs

- [Proof-of-concept stream](../README.md) defines milestone order and claim scope.
- [Runtime roadmap](../../erts-webassembly-runtime-milestones.md) preserves the global loading and ordering rules.
- [Canonical runtime architecture](../../../20-notes/erts-webassembly-runtime-architecture-and-milestones.md) defines the target system and trust boundaries.
- [ADR-0001](../../../20-notes/architecture-decisions/adr-0001-implementation-languages-and-beam-qualification-sequence.md) proposes C, strict TypeScript, Erlang-first proof artifacts, and staged Elixir qualification.
- [Minimum browser platform-contract inquiry](../../../40-inquiries/what-is-the-minimum-browser-platform-contract-for-upstream-erts.md) defines falsifiable proof dimensions.

## Entry decisions and dependencies

| Decision ID | Choice and evaluation criteria | Resolution task / location | Responsible owner | Blocks | State and evidence |
| --- | --- | --- | --- | --- | --- |
| P0-D01 | Accept or revise language/toolchain ownership using successful ABI and authority-boundary probes. | `p0-p01-language-ownership`, then P1 evidence | Unassigned architecture reviewer | P2 implementation ownership | Proposed in ADR-0001; not tested. |
| P0-D02 | Select the root executable trust anchor and delivery policy without claiming that generated glue authenticates itself. | `p0-p03-bootstrap-trust` | Unassigned security reviewer | P1 delivery probe | Open; no evidence. |
| P0-D03 | Freeze experimental safety ceilings now and a non-gameable product-budget derivation method before C1. | `p0-p02-experiment-bounds`, `p0-p02-product-budget-method` | Product-budget authority unassigned | P1 measurement and Program B | Open; no evidence. |

## Gate-to-phase and artifact mapping

| Gate / acceptance ID | Required combined result | Artifact IDs | Owning phase and task IDs | Entry dependencies | Evidence and gate state |
| --- | --- | --- | --- | --- | --- |
| P0-A01 | Pinned source, toolchain, browser, trust, language, runtime, and thread-census baseline. | `p0-baseline`, `p0-runtime-inventory`, `p0-thread-census-contract` | [Phase 1](phase-01-baseline-authority-and-runtime-inventory.md): `p0-p01-pins` through `p0-p01-thread-census` | None | Not run / open. |
| P0-A02 | Frozen experimental limits, unsupported and bounds inventories, product-budget method, and evidence profiles. | `p0-experiment-bounds`, `p0-unsupported-matrix`, `p0-evidence-profile` | [Phase 2](phase-02-bounds-budgets-and-evidence-contracts.md): `p0-p02-experiment-bounds` through `p0-p02-evidence-profiles` | `p0-p01-handoff` | Not run / open. |
| P0-A03 | Manifest, generation, root-trust, and delivery contracts reject contradictory or out-of-bounds inputs. | `p0-loader-contract`, `p0-bootstrap-trust` | [Phase 3](phase-03-loader-trust-contract-and-p0-acceptance.md): `p0-p03-loader-contract`, `p0-p03-bootstrap-trust` | `p0-p02-handoff` | Not run / open. |
| P0-GATE | Reviewed baseline, asset/dependency/patch ledger, trust anchor, bounds and unsupported-operation inventories, loader protocol, and reproducible empty target environment exist. | All P0 artifacts and the P0 execution record | [Phase 3](phase-03-loader-trust-contract-and-p0-acceptance.md): `p0-p03-integration`, `p0-p03-handoff` | P0-A01 through P0-A03 | Not run / open. |

## Ordered phases

| Phase | Outcome | Entry dependency | Plan / execution state | Evidence |
| --- | --- | --- | --- | --- |
| [Phase 1 — Baseline authority and runtime inventory](phase-01-baseline-authority-and-runtime-inventory.md) | Freeze identities, ownership boundaries, and the runtime/thread inventory contract. | None | Authored / not started | None. |
| [Phase 2 — Bounds, budgets, and evidence contracts](phase-02-bounds-budgets-and-evidence-contracts.md) | Freeze experiment bounds, unsupported behavior, budget derivation, and evidence profiles. | `p0-p01-handoff` | Authored / not started | None. |
| [Phase 3 — Loader trust contract and P0 acceptance](phase-03-loader-trust-contract-and-p0-acceptance.md) | Freeze loading and root-trust authority, then evaluate the combined P0 gate. | `p0-p02-handoff` | Authored / not started | None. |

The dependency order prevents probe results from choosing their own limits or
silently changing the trust model. Documentation review may proceed in
parallel inside a phase only where task dependencies say `none`.

## Milestone exit

P0 passes only when the reviewed baseline, asset/dependency/patch ledger, trust
anchor, bounds and unsupported-operation inventories, loader protocol, and
reproducible empty target environment exist. The integrated contract review
must detect missing ownership, unresolved runtime edges, contradictory limits,
and deployment assumptions that violate the intended trust boundary.

**Claim unlocked:** none; this is governance evidence.

**Stop trigger:** the intended deployment cannot support a secure context,
cross-origin isolation, recursive Worker delivery policy, or the required
trust boundary.

Closure requires an execution record tied to the reviewed plan revision and a
proceed/revise/blocked decision. Any change to source, toolchain, browser,
trust anchor, topology candidates, manifest schema, or experimental limits
reopens the affected acceptance case.

## Index

### Subdirectories

- None yet.

### Documents

- [Phase 1 — Baseline authority and runtime inventory](phase-01-baseline-authority-and-runtime-inventory.md) — freezes source, authority, and inventory inputs.
- [Phase 2 — Bounds, budgets, and evidence contracts](phase-02-bounds-budgets-and-evidence-contracts.md) — freezes quantitative and evidence contracts.
- [Phase 3 — Loader trust contract and P0 acceptance](phase-03-loader-trust-contract-and-p0-acceptance.md) — freezes loader authority and evaluates the milestone gate.

## Maintaining this index

Inventory every phase, keep stable task and acceptance IDs synchronized, and
retain every gate unchecked until linked evidence passes. P0 wording and claim
boundaries remain authoritative unless an explicit decision supersedes them.
