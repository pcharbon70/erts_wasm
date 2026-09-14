---
title: "Systematic testing for detecting concurrency errors in Erlang programs"
kind: source
created: "2026-09-14"
authors:
  - "Maria Christakis"
  - "Alkis Gotovos"
  - "Konstantinos Sagonas"
published: 2013
citation_key: "christakis-et-al-2013-concuerror"
container: "Sixth IEEE International Conference on Software Testing, Verification and Validation"
edition: null
isbn: null
doi: "10.1109/ICST.2013.50"
url: "https://people.csail.mit.edu/alkisg/files/christakis13systematic.pdf"
accessed: "2026-09-14"
tags:
  - concurrency
  - erlang
  - model-checking
  - testing
aliases:
  - "Concuerror paper"
---

# Systematic testing for detecting concurrency errors in Erlang programs

## Reference

Maria Christakis, Alkis Gotovos, and Konstantinos Sagonas.
[“Systematic Testing for Detecting Concurrency Errors in Erlang
Programs”](https://people.csail.mit.edu/alkisg/files/christakis13systematic.pdf).
Sixth IEEE International Conference on Software Testing, Verification and
Validation, 2013. DOI
[10.1109/ICST.2013.50](https://doi.org/10.1109/ICST.2013.50).

## Research question or contribution

How can a tool explore and reproduce process interleavings in Erlang programs
without depending on a single scheduler run?

## Method

Concuerror performs stateless systematic exploration of relevant process
interleavings for existing Erlang tests. It reports abnormal exits, stuck
processes, and assertion failures with an execution trace that reproduces the
error. The paper describes scheduling points, dependency analysis, and
evaluation on Erlang programs.

## Findings

- A passing concurrent test under one scheduler trace is weak evidence because
  many legal process interleavings remain unexplored.
- Systematic exploration can identify a smaller reproducible ordering that
  exposes a failure, making concurrency regressions diagnosable rather than
  merely probabilistic.
- The tool controls Erlang-level scheduling and observes program failures. It
  does not verify the C scheduler, atomics, garbage collector, browser Worker
  implementation, or WebAssembly memory model.

## Relevance

The native-oracle semantic capsule should combine three layers: fixed examples
for exact ordering and failure behavior, randomized/property workloads for
state-space breadth, and systematic Erlang-level interleavings for small
process/link/monitor/timer scenarios. The same resulting BEAM workloads and
expected outcome sets can then run on native OTP and ERTS-Wasm.

Concuerror cannot certify the runtime port. It is useful for ensuring that the
test programs themselves describe more than one happy scheduler trace and for
producing adversarial interleavings that stress signal and mailbox semantics.

## Limits

State-space exploration scales poorly and uses an execution model with its own
supported subset. Browser throttling, C-level data races, Worker creation,
memory ordering, and lifecycle failure need independent tests. The paper
predates OTP 29 and does not establish current tool compatibility.

## Derived work

- [Processes, schedulers, signals, and timers](../20-notes/components/processes-schedulers-signals-and-timers.md)
- [Security, observability, and supply chain](../20-notes/components/security-observability-and-supply-chain.md)
