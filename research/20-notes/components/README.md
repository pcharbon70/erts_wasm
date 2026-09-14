---
title: "Architecture component notes"
kind: map
created: "2026-09-14"
tags:
  - archive-navigation
  - directory-index
aliases: []
---

# Architecture component notes (`components`)

## Purpose

Hold implementation-oriented deep dives for every component in the canonical
ERTS WebAssembly architecture.

## What belongs here

Cross-source component syntheses that define responsibilities, boundaries,
proof-of-concept implementation choices, later compatibility work, evidence
gates, and unresolved risks. General architecture remains in the parent note;
bibliographic claims remain in `30-sources`.

## Index

### Subdirectories

- None yet.

### Documents

- [Artifact loader and runtime generations](artifact-loader-and-runtime-generations.md)
- [Browser platform time, poll, and progress](browser-platform-time-poll-and-progress.md)
- [Capability broker and browser services](capability-broker-and-browser-services.md)
- [ERTS build and BEAM interpreter](erts-build-and-beam-interpreter.md)
- [Memory, garbage collection, and shared state](memory-garbage-collection-and-shared-state.md)
- [OTP and Elixir compatibility profile](otp-and-elixir-compatibility-profile.md)
- [OTP boot and BEAM code loading](otp-boot-and-beam-code-loading.md)
- [Processes, schedulers, signals, and timers](processes-schedulers-signals-and-timers.md)
- [Renderer, accessibility, and page lifecycle](renderer-accessibility-and-page-lifecycle.md)
- [Security, observability, and supply chain](security-observability-and-supply-chain.md)
- [Worker and pthread topology](worker-and-pthread-topology.md)

## Maintaining this index

Keep this inventory exhaustive. A component note must retain the POC/later
split, state what it does not prove, and update the component map and canonical
architecture when research changes a boundary.
