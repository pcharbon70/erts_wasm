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

Plan: authored. Execution: P0.1 through P0.3 are accepted and P0-A01 through
P0-A03 pass after material corrections. Phases 4 through 6 now decompose the
remaining harness, clean-input/container, and exact-browser readiness work;
they are authored but have not run. Tests: contract and negative checks pass
locally, while the experiment-readiness reproduction remains incomplete.
Pascal Charbonneau
(`pcharbon70`) is assigned to the remaining P0 review and experiment-owner
roles. P0 gate: blocked; formal P1 entry is not unlocked. Runtime
implementation evidence and numeric product budgets are explicitly downstream
and do not block P0. ADR-0001 remains proposed until P1 evidence supplies its
review trigger. The [expectation correction](../../../50-journal/2026-09-15-p0-expectation-correction.md)
records why the gate boundary changed.

## Authoritative inputs

- [Proof-of-concept stream](../README.md) defines milestone order and claim scope.
- [Runtime roadmap](../../erts-webassembly-runtime-milestones.md) preserves the global loading and ordering rules.
- [Canonical runtime architecture](../../../20-notes/erts-webassembly-runtime-architecture-and-milestones.md) defines the target system and trust boundaries.
- [ADR-0001](../../../20-notes/architecture-decisions/adr-0001-implementation-languages-and-beam-qualification-sequence.md) proposes C, strict TypeScript, Erlang-first proof artifacts, and staged Elixir qualification.
- [Minimum browser platform-contract inquiry](../../../40-inquiries/what-is-the-minimum-browser-platform-contract-for-upstream-erts.md) defines falsifiable proof dimensions.

## Entry decisions and dependencies

| Decision ID | Choice and evaluation criteria | Resolution task / location | Responsible owner | Blocks | State and evidence |
| --- | --- | --- | --- | --- | --- |
| P0-D01 | Accept or revise language/toolchain ownership using successful ABI and authority-boundary probes. | `p0-p01-language-ownership`, then P1 evidence | Pascal Charbonneau (`pcharbon70`), architecture reviewer | P2 implementation ownership | P0 ownership contract accepted; ADR-0001 remains proposed until P1 executable evidence. |
| P0-D02 | Select the root executable trust anchor and delivery policy without claiming that generated glue authenticates itself. | `p0-p03-bootstrap-trust` | Pascal Charbonneau (`pcharbon70`), security reviewer and deployment owner | P1 delivery probe | Owner accepted `secure-origin-tcb-v1` with an externally pinned manifest digest; executable deployment evidence remains pending. |
| P0-D03 | Freeze experimental safety ceilings now and a non-gameable product-budget derivation method before C1. | `p0-p02-experiment-bounds`, `p0-p02-product-budget-method` | Pascal Charbonneau (`pcharbon70`), P0 method reviewer; product authority deferred post-P6/pre-C1 | P1 measurement and Program B | Safety ceilings and method accepted through P0-A02; numeric product approval is a downstream pre-C1 gate, not a P0 blocker. |
| P0-D04 | Select enforceable local TLS, browser-result, egress-isolation, process-ownership, timeout, and teardown mechanisms for the clean readiness replay. | `p0-p04-harness-contract` | Pascal Charbonneau (`pcharbon70`), security and integration reviewer | P0 clean-environment reproduction | Open; Phase 4 must resolve exact dependencies and privileges before acquisition or browser execution. |

## Gate-to-phase and artifact mapping

| Gate / acceptance ID | Required combined result | Artifact IDs | Owning phase and task IDs | Entry dependencies | Evidence and gate state |
| --- | --- | --- | --- | --- | --- |
| P0-A01 | Pinned source, toolchain, browser, trust, language, runtime, and thread-census baseline. | `p0-baseline`, `p0-runtime-inventory`, `p0-thread-census-contract` | [Phase 1](phase-01-baseline-authority-and-runtime-inventory.md): `p0-p01-pins` through `p0-p01-thread-census` | None | **Passed 2026-09-16.** [Independent contract evidence](../../../assets/p0-governed-baseline/phase-01/p0-phase-01-acceptance.planning-evidence.json) binds the owner-accepted baseline and limitations to clean revision `aaff05d`. |
| P0-A02 | Frozen experimental limits, unsupported and bounds inventories, product-budget method, and evidence profiles. | `p0-experiment-bounds`, `p0-unsupported-matrix`, `p0-evidence-profile` | [Phase 2](phase-02-bounds-budgets-and-evidence-contracts.md): `p0-p02-experiment-bounds` through `p0-p02-evidence-profiles` | `p0-p01-handoff` | **Passed 2026-09-16.** [Independent contract evidence](../../../assets/p0-governed-baseline/phase-02/p0-phase-02-acceptance.planning-evidence.json) binds the owner-accepted contracts and limitations to clean revision `d502eae`. Instrumentation results and product-budget approval remain deferred to their owning gates. |
| P0-A03 | Manifest, generation, root-trust, and delivery contracts reject contradictory or out-of-bounds inputs. | `p0-loader-contract`, `p0-bootstrap-trust` | [Phase 3](phase-03-loader-trust-contract-and-p0-acceptance.md): `p0-p03-loader-contract`, `p0-p03-bootstrap-trust` | `p0-p02-handoff` | **Passed 2026-09-16.** [Independent contract evidence](../../../assets/p0-governed-baseline/phase-03/p0-phase-03-acceptance.planning-evidence.json) binds the owner-accepted manifest, loader, and trust contracts to clean revision `57b73b2`. |
| P0-GATE | Reviewed baseline, forecast asset/dependency ledger, canonical empty patch baseline, trust anchor, bounds and unsupported-operation inventories, loader protocol, and reproducible P1 experiment-readiness environment exist. | All P0 contracts, harness contract and fixture, clean replay receipt, browser readiness receipt, and the P0 execution record | [Phases 4–6](phase-04-readiness-harness-and-isolation-contract.md): `p0-p04-harness-contract` through `p0-p06-handoff`; then [Phase 3](phase-03-loader-trust-contract-and-p0-acceptance.md): `p0-p03-integration`, `p0-p03-handoff` | P0-A01 through P0-A03 | P0-A01 through P0-A03 pass; Phases 4–6 and final Phase 3 integration remain unrun. Clean experiment-readiness reproduction remains open in the [corrected acceptance report](../../../assets/p0-governed-baseline/phase-03/p0-acceptance-report.json). P1–P6 outcomes are deferred. |

## Ordered phases

| Phase | Outcome | Entry dependency | Plan / execution state | Evidence |
| --- | --- | --- | --- | --- |
| [Phase 1 — Baseline authority and runtime inventory](phase-01-baseline-authority-and-runtime-inventory.md) | Freeze identities, ownership boundaries, and the runtime/thread inventory contract. | None | Accepted; P0-A01 passed on 2026-09-16 | [Contract evidence](../../../assets/p0-governed-baseline/phase-01/p0-phase-01-acceptance.planning-evidence.json) and [execution record](../../../50-journal/2026-09-15-p0-phase-01-baseline-authority-execution.md). |
| [Phase 2 — Bounds, budgets, and evidence contracts](phase-02-bounds-budgets-and-evidence-contracts.md) | Freeze experiment bounds, unsupported behavior, budget derivation, and evidence profiles. | `p0-p01-handoff` | Accepted; P0-A02 passed on 2026-09-16 | [Contract evidence](../../../assets/p0-governed-baseline/phase-02/p0-phase-02-acceptance.planning-evidence.json) and [execution record](../../../50-journal/2026-09-15-p0-phase-02-bounds-contracts-execution.md). |
| [Phase 3 — Loader trust contract and P0 acceptance](phase-03-loader-trust-contract-and-p0-acceptance.md) | Freeze loading and root-trust authority, then evaluate the combined P0 gate. | `p0-p02-handoff` | Section 3.1 and P0-A03 passed; Section 3.2 and P0-GATE clean-environment reproduction remain open | [P0-A03 evidence](../../../assets/p0-governed-baseline/phase-03/p0-phase-03-acceptance.planning-evidence.json) and [2026-09-15 execution record](../../../50-journal/2026-09-15-p0-phase-03-loader-trust-and-acceptance-execution.md). |
| [Phase 4 — Readiness harness and isolation contract](phase-04-readiness-harness-and-isolation-contract.md) | Resolve isolation and fixture choices, then implement the dependency-minimal HTTPS and browser harness without qualification-browser execution. | P0-A03 | Authored; not run | Planned contract, fixture, tests, and execution record; no evidence yet. |
| [Phase 5 — Clean input and container replay](phase-05-clean-input-and-container-replay.md) | Acquire exact inputs, verify the pinned linux/amd64 toolchain, rebuild the native bootstrap, and prove network-disabled execution isolation. | `p0-p04-handoff` | Authored; not run | Planned replay receipt and contract-research evidence; no evidence yet. |
| [Phase 6 — Pinned browser readiness and P0 gate evidence](phase-06-pinned-browser-readiness-and-p0-gate.md) | Run the static readiness fixture in exact Chrome and Firefox builds, retain negative cases, and return a reviewed receipt to Phase 3. | `p0-p05-handoff` | Authored; not run | Planned browser-runtime evidence and readiness receipt; no evidence yet. |

The execution order deliberately splits Phase 3: its completed Section 3.1 and
P0-A03 feed Phases 4, 5, and 6; accepted `p0-p06-handoff` then permits Phase 3
Section 3.2 to resume and evaluate P0-GATE. This preserves the delivered Phase
3 task identities while making the missing environment work executable. The
dependency order prevents probe results from choosing their own limits or
silently changing the trust model. Documentation review may proceed in
parallel inside a phase only where task dependencies say `none`.

## Milestone exit

P0 passes only when the reviewed baseline, asset/dependency/patch ledger, trust
anchor, bounds and unsupported-operation inventories, loader protocol, and
reproducible experiment-readiness environment exist. The integrated contract
review must detect missing immediate ownership, unresolved contract edges,
contradictory limits, and deployment assumptions that violate the intended
trust boundary.

P0 does not require successful C/Emscripten compilation, built runtime assets,
ERTS/OTP boot, browser-runtime behavior, a nonempty patch stack, sanitizer or
fuzz results, semantic compatibility, lifecycle evidence, or numeric product
budgets. Those outcomes belong to P1–P6 or the post-P6/pre-C1 product gate.

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
- [Phase 4 — Readiness harness and isolation contract](phase-04-readiness-harness-and-isolation-contract.md) — specifies and implements the bounded local readiness harness.
- [Phase 5 — Clean input and container replay](phase-05-clean-input-and-container-replay.md) — reproduces exact source, toolchain, native-bootstrap, and isolation inputs.
- [Phase 6 — Pinned browser readiness and P0 gate evidence](phase-06-pinned-browser-readiness-and-p0-gate.md) — qualifies exact browsers and returns the clean readiness receipt.

## Maintaining this index

Inventory every phase, keep stable task and acceptance IDs synchronized, and
retain every gate unchecked until linked evidence passes. P0 wording and claim
boundaries remain authoritative unless an explicit decision supersedes them.
