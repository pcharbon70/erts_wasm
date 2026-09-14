---
title: "Which component seams block the first ERTS-Wasm proof?"
kind: inquiry
created: "2026-09-14"
status: open
tags:
  - architecture
  - blockers
  - components
  - erts
  - proof-of-concept
  - webassembly
aliases:
  - "ERTS-Wasm component blocker inquiry"
---

# Which component seams block the first ERTS-Wasm proof?

## Why this matters

The component research produces a coherent proposed architecture, but its
highest-risk assumptions meet at boundaries: generated interpreter to
toolchain, pthreads to Workers, ERTS wait/poll to browser progress, fixed
linear memory to allocator behavior, verified release to native BEAM parsing,
and Worker termination to complete generation reclamation. A successful demo
can bypass each seam and still fail the project goal.

## Operational question

Can OTP 29.0.6 / ERTS 17.0.6, at commit
`e07fd07837e5aa845657f5fa340637121e451d47`, pass all of the following with a
localized browser platform layer and no unreviewed semantic fork?

1. compile the complete generated interpreter with fixed shared memory and
   suppress automatic `main` until the verified release is mounted;
2. start the measured mandatory pthread graph in both topology candidates;
3. preserve atomics, thread progress, clock, timer, poll, and wake semantics;
4. boot an authenticated embedded Kernel/STDLIB/application release;
5. admit one ordinary pre-ready module below every loader bypass and then close
   admission;
6. match Tier-0 native semantic outcomes; and
7. terminate successful, failed, cancelled, OOM, CPU-bound, and wedged
   generations with no stale effect or positive resource slope?

Any seam that requires broad POSIX authority, rewriting a preserved subsystem,
or an unbounded/hanging failure blocks the proposed POC and triggers a recorded
redesign decision.

## Working hypotheses

- The generated switch-dispatch interpreter will compile before a tuned
  computed-goto variant is necessary.
- The actual minimum ERTS thread graph will fit a statically pre-created
  Emscripten pool, but it will be materially larger than `+S 1:1` suggests.
- Existing Emscripten pthread atomics and condvar/futex paths will satisfy most
  `ethread` behavior; poll, lifecycle, and genuine `mmap` assumptions will need
  target-specific work.
- A verified MEMFS release tree can be enough for the first boot if a lower
  adapter denies write/create/rename/unlink/truncate and undeclared paths;
  a manifest-backed primitive loader may later reduce surface.
- Fixed linear memory plus malloc-backed carriers is adequate for Tier 0; broad
  workloads will require allocator and possibly bounded-growth work.
- Whole-generation replacement can remain the default update model even if
  constrained BEAM bundles are supported later.

Each statement is provisional and must be rejected when executable evidence
contradicts it.

## Paths to explore

### Build and interpreter seam

- Compile `NO_JUMP_TABLE` and computed-goto variants from identical generated
  sources; capture compiler failures, Wasm size, browser compile/tier-up time,
  and differential instruction results.
- Audit every configure cache decision and every symbol/import against the
  [build/interpreter component](../20-notes/components/erts-build-and-beam-interpreter.md).

### Thread and progress seam

- Instrument the exact startup graph, run pool `N`/`N-1`, atomic/event/TLS and
  thread-progress probes, and compare both [Worker topologies](../20-notes/components/worker-and-pthread-topology.md).
- Drive completion-queue saturation, wake-before-publish, cancellation, and
  background/freeze states through the [platform component](../20-notes/components/browser-platform-time-poll-and-progress.md).

### Memory seam

- Measure static/stack/release/code headroom and allocator behavior at a fixed
  ceiling; stress `wasm32` literal, GC, binary, atom, ETS, and persistent-term
  paths described by the [memory component](../20-notes/components/memory-garbage-collection-and-shared-state.md).

### Loading and semantic seam

- Delete each transitive release edge, corrupt each BEAM/boot structure class,
  exercise the pre-ready module, and attempt every bypass in the [boot/loader
  component](../20-notes/components/otp-boot-and-beam-code-loading.md).
- Execute fixed, property-generated, and systematically interleaved native/Wasm
  workloads from the [process/scheduler component](../20-notes/components/processes-schedulers-signals-and-timers.md).

### Ownership seam

- Fail or cancel every state in the [generation loader](../20-notes/components/artifact-loader-and-runtime-generations.md),
  inject OOM and a wedged scheduler, and prove independently observed resource
  settlement through the [assurance component](../20-notes/components/security-observability-and-supply-chain.md).

## Findings

Research inspection establishes the seams and proposed probes but supplies no
passing target result. The current estimate of the minimum thread graph, fixed-
memory recommendation, pre-ready loader proof, and conservative lifecycle
policy are inputs to P0/P1, not closed findings about browser feasibility.

## Outcome

Open. Resolve only when the accepted P6 package links exact artifacts and
results for every operational clause, or when a stop trigger produces an
approved replacement architecture.
