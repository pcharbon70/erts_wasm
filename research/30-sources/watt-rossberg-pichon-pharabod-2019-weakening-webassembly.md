---
title: "Weakening WebAssembly"
kind: source
created: "2026-09-14"
authors:
  - "Conrad Watt"
  - "Andreas Rossberg"
  - "Jean Pichon-Pharabod"
published: 2019
citation_key: "watt-rossberg-pichon-pharabod-2019-weakening-webassembly"
container: "Proceedings of the ACM on Programming Languages, OOPSLA"
edition: null
isbn: null
doi: "10.1145/3360559"
url: "https://people.mpi-sws.org/~rossberg/papers/Watt%2C%20Rossberg%2C%20Pichon-Pharabod%20-%20Weakening%20WebAssembly%20%5BExtended%5D.pdf"
accessed: "2026-09-14"
tags:
  - atomics
  - concurrency
  - memory-model
  - threads
  - webassembly
aliases:
  - "WebAssembly relaxed memory model paper"
---

# Weakening WebAssembly

## Reference

Conrad Watt, Andreas Rossberg, and Jean Pichon-Pharabod.
[“Weakening WebAssembly”](https://people.mpi-sws.org/~rossberg/papers/Watt%2C%20Rossberg%2C%20Pichon-Pharabod%20-%20Weakening%20WebAssembly%20%5BExtended%5D.pdf).
Proceedings of the ACM on Programming Languages 3, OOPSLA, 2019. DOI
[10.1145/3360559](https://doi.org/10.1145/3360559).

## Research question or contribution

What relaxed-memory semantics can safely and portably support shared-memory
threads and atomics in WebAssembly, including concurrent memory growth?

## Method

The authors give operational and axiomatic semantics for shared-memory Wasm,
prove sequential consistency for data-race-free programs, develop litmus tests,
and compare the model with JavaScript's shared-memory behavior. The work is a
basis for the WebAssembly threads specification's relaxed-memory chapter.

## Findings

- Bounds checking does not remove the need for a memory model. Concurrent
  programs still need defined ordering for atomic and ordinary accesses,
  wait/notify queues, and memory growth.
- Data-race-free programs receive the expected sequential-consistency property.
  Racy programs are not simply made deterministic by WebAssembly validation.
- WebAssembly wait and notify operate on shared-memory locations with specified
  queue behavior, while thread creation remains an embedder concern.
- JavaScript and WebAssembly interoperability imposes constraints that are not
  visible when reasoning only from a native pthread implementation.

## Relevance

ERTS already contains carefully designed atomics, locks, thread progress, and
publication protocols. The port should preserve those abstractions and prove
that Emscripten maps them to Wasm atomics with the required widths, alignment,
and ordering; it should not replace them with ad hoc JavaScript flags. Shared
broker rings likewise need explicit atomic ownership and publication rules.

The POC should hold shared memory at a fixed declared maximum where practical,
test ERTS atomic primitives and wait/notify in isolation, run litmus and stress
tests in both target browsers, and use ThreadSanitizer or native race tooling
where supported. Browser results must be tied to the pinned emsdk and browser
versions.

## Limits

The paper specifies a language memory model, not Emscripten pthread completeness
or ERTS correctness. It does not establish Worker startup, forward progress,
fairness, lifecycle, or performance. Current WebAssembly specifications and
engines have evolved since 2019, so the pinned target must be checked against
the current normative tests.

## Derived work

- [Worker and pthread topology](../20-notes/components/worker-and-pthread-topology.md)
- [Processes, schedulers, signals, and timers](../20-notes/components/processes-schedulers-signals-and-timers.md)
- [Memory, garbage collection, and shared state](../20-notes/components/memory-garbage-collection-and-shared-state.md)
