---
title: "ERTS WebAssembly component implementation map"
kind: map
created: "2026-09-14"
tags:
  - architecture
  - components
  - erlang
  - erts
  - implementation
  - otp
  - webassembly
aliases:
  - "ERTS-Wasm component map"
---

# ERTS WebAssembly component implementation map

## Scope

This map provides an exhaustive route through the implementation-oriented deep
dives derived from the canonical architecture. Each component separates the
minimal proof-of-concept choice from the later in-depth compatibility target
and keeps runtime loading visible at its boundary.

## Start here

- [Component implementation deep dive](../20-notes/erts-webassembly-component-implementation-deep-dive.md)
  gives the system-wide result, dependency model, POC refinements, and complete
  component matrix.
- [Canonical architecture](../20-notes/erts-webassembly-runtime-architecture-and-milestones.md)
  remains the authority for scope, invariants, proof claims, and milestone
  boundaries.
- [ADR-0001 — Implementation languages and BEAM qualification
  sequence](../20-notes/architecture-decisions/adr-0001-implementation-languages-and-beam-qualification-sequence.md)
  assigns C, TypeScript, Erlang, and later Elixir to explicit ownership and
  evidence boundaries while deferring Rust and new C++ pending measured need.
- [Planning roadmap](../60-planning/erts-webassembly-runtime-milestones.md),
  [proof-of-concept stream](../60-planning/01-proof-of-concept/README.md), and
  [compatibility stream](../60-planning/02-in-depth-erts-compatibility/README.md)
  retain every gate unchecked until executable evidence exists.
- [Component-seam inquiry](../40-inquiries/which-component-seams-block-the-first-erts-wasm-proof.md)
  turns the remaining uncertainties into stop/go experiments.

## Implementation trails

### Establish one trustworthy generation

1. [Artifact loader and runtime generations](../20-notes/components/artifact-loader-and-runtime-generations.md)
   defines root trust, manifest coherence, stateful startup, attestation,
   cancellation, and all-or-nothing disposal.
2. [Security, observability, and supply chain](../20-notes/components/security-observability-and-supply-chain.md)
   defines the trusted base, limits of Wasm containment, evidence envelope,
   fuzzing, reproducibility, SBOM, provenance, and update ownership.

### Construct a browser-hosted ERTS

1. [ERTS build and BEAM interpreter](../20-notes/components/erts-build-and-beam-interpreter.md)
   retains the complete generated interpreter while localizing the cross-port.
2. [Worker and pthread topology](../20-notes/components/worker-and-pthread-topology.md)
   derives the irreducible thread graph and topology experiment.
3. [Browser platform time, poll, and progress](../20-notes/components/browser-platform-time-poll-and-progress.md)
   supplies the narrow system contract without general POSIX emulation.
4. [Memory, garbage collection, and shared state](../20-notes/components/memory-garbage-collection-and-shared-state.md)
   binds `wasm32`, fixed shared memory, GC, allocators, binaries, atoms, ETS,
   and persistent terms.

### Boot and prove semantics

1. [OTP boot and BEAM code loading](../20-notes/components/otp-boot-and-beam-code-loading.md)
   preserves the real boot/loader/code-index path and closes admission before
   readiness.
2. [Processes, schedulers, signals, and timers](../20-notes/components/processes-schedulers-signals-and-timers.md)
   defines the differential Tier-0 semantic capsule and concurrency evidence.
3. [OTP and Elixir compatibility profile](../20-notes/components/otp-and-elixir-compatibility-profile.md)
   expands from Kernel/STDLIB to core OTP and exact-version Elixir closures.

### Add optional product capabilities

1. [Capability broker and browser services](../20-notes/components/capability-broker-and-browser-services.md)
   adds Fetch, WebSocket, persistence, cryptography, and future browser APIs as
   independent least-authority grants.
2. [Renderer, accessibility, and page lifecycle](../20-notes/components/renderer-accessibility-and-page-lifecycle.md)
   adds a semantic DOM adapter, interaction/accessibility semantics,
   backpressure, and lifecycle-safe ownership.

## Open questions

- Can the [component-seam inquiry](../40-inquiries/which-component-seams-block-the-first-erts-wasm-proof.md)
  close every POC seam without broad Unix emulation or changes to common ERTS
  semantics?
- Which [minimum browser platform contract](../40-inquiries/what-is-the-minimum-browser-platform-contract-for-upstream-erts.md)
  functions fail first in the pinned build?
- Does the resulting evidence justify the long-term ownership question in the
  [original feasibility inquiry](../40-inquiries/can-blazex-build-and-own-an-erts-webassembly-runtime-stack.md)?
