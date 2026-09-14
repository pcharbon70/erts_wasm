---
title: "Erlang/OTP testing, time, and runtime observability"
kind: source
created: "2026-09-14"
authors:
  - "Erlang/OTP Project"
published: 2026
citation_key: "erlang-otp-project-2026-testing-time-observability"
container: "Erlang/OTP 29 documentation"
edition: "OTP 29 series"
isbn: null
doi: null
url: "https://www.erlang.org/doc/apps/erts/time_correction.html"
accessed: "2026-09-14"
tags:
  - common-test
  - observability
  - testing
  - time
  - timers
aliases:
  - "OTP time and conformance evidence"
---

# Erlang/OTP testing, time, and runtime observability

## Reference

Erlang/OTP Project documentation, accessed 2026-09-14:

- [Time and Time Correction in Erlang](https://www.erlang.org/doc/apps/erts/time_correction.html);
- [Common Test introduction](https://www.erlang.org/doc/apps/common_test/introduction.html);
- [Common Test property testing](https://www.erlang.org/doc/apps/common_test/ct_property_test.html);
- [`erlang:system_info/1`](https://www.erlang.org/doc/apps/erts/erlang.html);
- [runtime system tools](https://www.erlang.org/doc/apps/runtime_tools/index.html); and
- [DTrace and Erlang/OTP](https://www.erlang.org/doc/apps/runtime_tools/dtrace.html).

## Research question or contribution

Which upstream time semantics and test/diagnostic mechanisms can define a
native oracle and observable qualification harness for ERTS-Wasm?

## Method

The current ERTS time model was compared with browser clocks and suspension.
The official test and tracing documentation was reviewed for mechanisms that
can execute the same workload or collect comparable state without making the
full diagnostics surface part of the product profile.

## Findings

- Erlang monotonic time is ERTS's internal time engine. Receive timeouts and
  other timers are triggered relative to it; Erlang system time is monotonic
  time plus a time offset.
- Current ERTS defaults to multi-time-warp mode. Its behavior depends on the
  properties ERTS declares for the operating-system monotonic and wall clocks.
- Erlang timers have millisecond-level semantics and must not fire before their
  timeout; load can make them late. Browser suspension is therefore primarily
  a late-progress and policy problem, not permission to report an early timer.
- Common Test can run automated white-box Erlang/OTP suites and emit structured
  events. Property-test integration can expand generated cases but depends on
  external tools.
- ERTS exposes extensive tracing and system information. Those mechanisms are
  useful for qualification but can be high-volume or reveal application data,
  so a production browser profile should not grant them without policy.

## Relevance

The browser system layer should map a qualified common-base Worker clock—such
as one provider or validated `performance.timeOrigin + performance.now()`
normalization—to OS monotonic time and a separately sampled wall clock to OS
system time, then report the exact source properties through `system_info`.
The port must declare whether elapsed time includes browser or machine
suspension and test overdue timer ordering after resume or generation
replacement.

The conformance harness should run a curated upstream subset and a smaller
purpose-built capsule on both native OTP and ERTS-Wasm. Observations should be
structured by generation, test identity, monotonic sequence, process/scheduler
identity, and event type. Exact invariants and predeclared environmental
tolerances must be separated before comparing traces.

## Limits

Not every upstream suite is meaningful in the browser profile, and skipped
tests are not evidence of support. ERTS tracing perturbs scheduling and cannot
prove the absence of races. No upstream suite has run on an ERTS-Wasm artifact
in this corpus.

## Derived work

- [Browser platform time, poll, and progress](../20-notes/components/browser-platform-time-poll-and-progress.md)
- [Processes, schedulers, signals, and timers](../20-notes/components/processes-schedulers-signals-and-timers.md)
- [Security, observability, and supply chain](../20-notes/components/security-observability-and-supply-chain.md)
