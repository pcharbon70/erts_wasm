---
title: "ERTS WebAssembly runtime milestones"
kind: note
created: "2026-09-14"
maturity: developing
tags:
  - browser
  - compatibility
  - erlang
  - erts
  - implementation-planning
  - milestones
  - otp
  - proof-of-concept
  - runtime-loading
  - webassembly
aliases:
  - "ERTS-Wasm implementation roadmap"
---

# ERTS WebAssembly runtime milestones

## Status and use

This is the stable roadmap companion to the [canonical runtime
architecture](../20-notes/erts-webassembly-runtime-architecture-and-milestones.md).
Detailed obligations, phase ownership, gates, and evidence state live in the
numbered planning hierarchy. This roadmap authorizes no implementation and
records no completed work.

The runtime program remains prospective. P0 now has locally validated contract
drafts but a blocked gate; every P0–P6 and C1–C10 stable task and gate is
unchecked or not run until its named executable evidence exists and has been
reviewed.

## Program A — minimal proof of concept

[Program A](01-proof-of-concept/README.md) establishes one minimal, pinned,
meaningful proof of concept.

| Milestone | Outcome | Planning state |
| --- | --- | --- |
| [P0](01-proof-of-concept/p0-governed-baseline-and-proof-contract/README.md) | Governed baseline and proof contract | P0.1/P0.2 accepted and P0-A01/P0-A02 passed; P0-GATE remains blocked on P0-A03 review and clean experiment readiness—not downstream implementation results. |
| [P1](01-proof-of-concept/p1-target-and-dependency-probes/README.md) | Target and dependency probes | Three authored phases; not started. |
| [P2](01-proof-of-concept/p2-interpreter-artifact-and-outer-loader/README.md) | Interpreter artifact and outer loader | Decomposition pending P1 evidence. |
| [P3](01-proof-of-concept/p3-immutable-erts-and-otp-cold-boot/README.md) | Immutable ERTS and OTP cold boot | Decomposition pending P2 evidence. |
| [P4](01-proof-of-concept/p4-tier-0-semantic-capsule/README.md) | Tier-0 semantic capsule | Decomposition pending P3 evidence. |
| [P5](01-proof-of-concept/p5-bounded-host-progress-and-lifecycle/README.md) | Bounded host progress and lifecycle | Decomposition pending P4 evidence. |
| [P6](01-proof-of-concept/p6-proof-of-concept-qualification-package/README.md) | Proof-of-concept qualification package | Decomposition pending P5 evidence. |

Only accepted P6 evidence unlocks Program B.

## Program B — in-depth ERTS compatibility

[Program B](02-in-depth-erts-compatibility/README.md) may expand an accepted
proof into an in-depth, maintained ERTS-Wasm compatibility profile.

| Milestone | Outcome | Planning state |
| --- | --- | --- |
| [C1](02-in-depth-erts-compatibility/c1-compatibility-inventory-and-native-oracle/README.md) | Compatibility inventory and native oracle | Decomposition pending accepted P6 evidence. |
| [C2](02-in-depth-erts-compatibility/c2-hardened-code-lifecycle/README.md) | Hardened code lifecycle | Decomposition pending C1 evidence. |
| [C3](02-in-depth-erts-compatibility/c3-scheduler-and-browser-state-compatibility/README.md) | Scheduler and browser-state compatibility | Decomposition pending C2 evidence. |
| [C4](02-in-depth-erts-compatibility/c4-memory-and-shared-state-compatibility/README.md) | Memory and shared-state compatibility | Decomposition pending C3 evidence. |
| [C5](02-in-depth-erts-compatibility/c5-core-otp-and-pinned-elixir-profile/README.md) | Core OTP and pinned Elixir profile | Decomposition pending C4 evidence. |
| [C6](02-in-depth-erts-compatibility/c6-hardened-broker-and-optional-browser-capabilities/README.md) | Hardened broker and optional browser capabilities | Decomposition pending C5 evidence. |
| [C7](02-in-depth-erts-compatibility/c7-renderer-and-application-lifecycle/README.md) | Renderer and application lifecycle | Decomposition pending C6 evidence. |
| [C8](02-in-depth-erts-compatibility/c8-security-and-supply-chain-hardening/README.md) | Security and supply-chain hardening | Decomposition pending C7 evidence. |
| [C9](02-in-depth-erts-compatibility/c9-performance-and-browser-qualification/README.md) | Performance and browser qualification | Decomposition pending C8 evidence. |
| [C10](02-in-depth-erts-compatibility/c10-maintained-erts-wasm-release-profile/README.md) | Maintained ERTS-Wasm release profile | Decomposition pending C9 evidence. |

Before C1, product owners freeze qualification budgets or approve a
non-gameable method that derives them from named POC and native baselines. P0
experimental safety ceilings are not product performance budgets.

## Runtime-loading invariant

Runtime loading is part of every milestone. It includes browser artifact
delivery, Wasm and Worker startup, ERTS/OTP release boot, BEAM admission and
code lifecycle, update integrity, cancellation, and generation teardown. A
milestone cannot defer its loading consequences to a later integration pass.

## Preservation ledger

The hierarchy preserves all source obligations from the former monolithic
plan: P0.1 tasks and P0-A01 are evidence-closed while later P0–P6 tasks and
gates remain open; 35 unchecked C1–C10 work items, and ten C1–C10
gate statements. It also preserves every objective, runtime-loading
obligation, claim boundary, stop trigger, Program B entry rule, and global
ordering rule. Structural phase, integration, and handoff tasks add planning
detail but do not weaken or complete those obligations.

## Global ordering rules

- Never call compile, instantiate, `init`, or a visual demo the POC.
- Establish a minimal verified manifest and module boundary before first boot;
  do not retrofit loader authority afterward.
- Do not build the renderer or optional browser capabilities before Tier-0
  semantics and generation teardown.
- Do not choose a Worker topology before measuring loading responsiveness,
  actual ERTS threads, ownership, and forced cleanup.
- Do not call `+S 1:1` threadless.
- Do not optimize, split, or lazy-load the generation before correctness and
  atomic version closure are established.
- Do not add a service worker casually; if used, it becomes part of the loading
  and update trusted base and must prevent mixed generations.
- Do not set budgets after observing the result or hide a positive slope behind
  a generous absolute threshold. Freeze P0 safety ceilings before the POC and
  the product-budget values or derivation method before C1.
- Do not infer compatibility from dependency presence, one browser, one boot,
  or a warm developer cache.

## Connections

- [Planning conventions and index](README.md)
- [ADR-0001 — Implementation languages and BEAM qualification sequence](../20-notes/architecture-decisions/adr-0001-implementation-languages-and-beam-qualification-sequence.md)
- [Canonical runtime architecture](../20-notes/erts-webassembly-runtime-architecture-and-milestones.md)
- [Component implementation deep dive](../20-notes/erts-webassembly-component-implementation-deep-dive.md)
- [Component implementation map](../10-maps/erts-webassembly-component-implementation.md)
- [Component-seam inquiry](../40-inquiries/which-component-seams-block-the-first-erts-wasm-proof.md)
- [Minimum browser platform-contract inquiry](../40-inquiries/what-is-the-minimum-browser-platform-contract-for-upstream-erts.md)
- [First-party feasibility inquiry](../40-inquiries/can-blazex-build-and-own-an-erts-webassembly-runtime-stack.md)
- [Runtime-stack map](../10-maps/erts-webassembly-runtime-stack.md)
