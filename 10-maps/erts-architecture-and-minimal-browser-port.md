---
title: "ERTS architecture and minimum browser-port map"
kind: map
created: "2026-09-14"
tags:
  - architecture
  - beam
  - browser
  - erlang
  - erts
  - otp
  - porting
  - webassembly
aliases:
  - "Minimum ERTS browser-port map"
---

# ERTS architecture and minimum browser-port map

## Scope

This map answers two connected questions: what ERTS contains, and which pieces
must be preserved, adapted, or prohibited for an upstream, browser-hosted
WebAssembly runtime. The emphasis is a minimal browser platform contract, not
a new minimal virtual machine.

## Start here

- [ERTS architecture and the minimum browser WebAssembly
  port](../20-notes/erts-architecture-and-minimal-browser-webassembly-port.md)
  is the complete deep-dive synthesis, implementation inventory, five-rung
  evidence model, and recommendation.
- [What is the minimum browser platform contract for upstream
  ERTS?](../40-inquiries/what-is-the-minimum-browser-platform-contract-for-upstream-erts.md)
  turns the proposed boundary into falsifiable compile, boot, semantics,
  capability, and teardown gates.
- [2026-09-14 ERTS architecture and minimum WebAssembly-port deep
  dive](../50-journal/2026-09-14-erts-architecture-and-minimal-webassembly-port-deep-dive.md)
  records revisions, commands, observations, and limits.

## Component trails

### Runtime execution and boot

- [The BEAM Book](../30-sources/stenman-2025-beam-book.md) — whole-runtime
  conceptual model.
- [ERTS build, runtime, and source
  architecture](../30-sources/erlang-otp-project-2026-erts-build-runtime-and-source.md)
  — pinned platform seams, startup, build, scheduler, interpreter, and memory
  evidence.
- [OTP boot, security, and browser
  compatibility](../30-sources/erlang-otp-project-2026-otp-boot-security-and-compatibility.md)
  — boot script, preloads, loader, release, and compatibility constraints.

### Process and memory semantics

- [Efficient memory management for message-passing
  programs](../30-sources/sagonas-wilhelmsson-2006-erlang-memory-management.md)
  — process-local heaps, message copying, shared areas, and collector tradeoffs.
- [Scaling Reliably](../30-sources/trinder-et-al-2017-scaling-reliably-erlang.md)
  — scheduler, ETS, timer, time, and shared-state interactions.

### Browser platform and Worker substrate

- [Emscripten browser porting
  runtime](../30-sources/emscripten-project-2026-browser-porting-runtime.md)
  — pthread Workers, event-loop constraints, filesystems, async mechanisms,
  networking, and sanitizers.
- [WebAssembly browser security and threading
  standards](../30-sources/webassembly-standards-2026-browser-security-and-threads.md)
  — shared memory, cross-origin isolation, CSP, and containment.
- [WASI and threading
  status](../30-sources/webassembly-project-2026-wasi-and-threading-status.md)
  — why WASI is not the initial browser ABI.
- [Browsix](../30-sources/powers-vilk-berger-2017-browsix.md) — evidence that
  broad Unix compatibility is an OS-sized alternative, not a minimal adapter.

### Comparative runtime evidence

- [AtomVM runtime architecture and WebAssembly
  port](../30-sources/atomvm-project-2026-runtime-and-webassembly-port.md) —
  independent evidence for off-main-thread runtime execution and queued browser
  events, constrained by a deliberately different semantic profile.
- [Erlang/OTP WebAssembly
  demonstration](../30-sources/vasetenkov-erlang-otp-webassembly-demo.md) —
  public upstream-OTP feasibility signal without a reproducible implementation
  record.

### Performance and security

- [Not So Fast](../30-sources/jangda-et-al-2019-webassembly-performance.md) —
  subsystem-oriented native/Wasm benchmarking discipline.
- [Everything Old Is New
  Again](../30-sources/lehmann-kinder-pradel-2020-webassembly-binary-security.md)
  — unsafe-language vulnerabilities inside Wasm.
- [Swivel](../30-sources/narayan-et-al-2021-swivel.md) — speculative-execution
  risk beyond architectural Wasm bounds checks.

## Decision boundary

The current evidence supports investigating a narrow platform port. It does not
yet support an implementation schedule, compatibility claim, browser support
matrix, or product adoption decision. Advance only through the linked inquiry's
measured gates.
