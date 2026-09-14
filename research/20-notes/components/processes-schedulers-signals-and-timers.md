---
title: "Processes, schedulers, signals, and timers"
kind: note
created: "2026-09-14"
maturity: developing
tags:
  - concurrency
  - erlang
  - erts
  - processes
  - scheduling
  - signals
  - timers
aliases:
  - "ERTS actor runtime component"
---

# Processes, schedulers, signals, and timers

## Decision

Preserve ERTS process, signal, mailbox, reduction, run-queue, scheduler,
thread-progress, timer-wheel, link, monitor, and exit machinery. The browser
port adapts pthread event/wakeup and poll sources beneath it; JavaScript never
implements or mutates an Erlang mailbox or scheduler queue.

## Why this is the semantic core

ERTS processes execute for a reductions budget and return to scheduler control.
Normal schedulers have run queues; dirty CPU/I/O work and auxiliary progress
have distinct paths. Thread progress provides epochs/grace periods for safe
publication and delayed reclamation. Scheduler sleep coordinates timers,
polling, wakeups, and auxiliary work.[^erts-source][^scaling]

Messages, exits, links, monitors, process-info requests, and control operations
use the process-signal machinery. Signals from one sender to one receiver obey
defined ordering, but many-sender arrival is not globally ordered. Selective
receive scans the mailbox under those rules. Message terms interact with heap
ownership, off-heap fragments, and shared binaries, so a JavaScript “actor
shim” would bypass exactly the semantics this project intends to preserve.

Timers use ERTS monotonic time and scheduler timer wheels. A late browser wake
may make multiple timers overdue; it does not change their deadlines or allow
early delivery. Timer expiry, cancellation, receive timeout, signal arrival,
and process exit have real races whose allowed outcomes must be compared with
native ERTS rather than serialized into one convenient order.[^otp-time]

## POC implementation

Use the pinned runtime's smallest accepted explicit settings—starting from one
normal scheduler and minimum dirty CPU, dirty I/O, poll, async, and auxiliary
work—and record the actual thread graph. Reduce or disable scheduler busy wait
where supported to limit browser idle CPU, but qualify wake latency and
fairness before keeping the setting.

The platform poll backend and completion queue expose events as ordinary port
or runtime work. A statically linked bridge validates a browser completion,
copies bytes into ERTS-owned memory, constructs the port/signal event through
documented ERTS APIs, and wakes the appropriate runtime path. Host code never
retains a pointer to a `Process`, edits mailbox links, or holds an ERTS lock
while awaiting JavaScript.

The Tier-0 capsule runs the identical BEAM files on native OTP 29.0.6 and in the
browser and covers:

- spawn, normal exit, abnormal exit, trapping exits, registered names, and
  process reclamation;
- reductions-based preemption under a CPU-bound process plus a latency-sensitive
  process;
- same-sender ordering, valid many-sender nondeterminism, large messages,
  selective receive, and receive-after;
- links, monitors, demonitor/flush races, down reasons, supervisor restart, and
  application shutdown; and
- zero, equal-deadline, cancelled, long, mass, and completion-versus-timeout
  timers.

Exact semantics use equality; environmental quantities such as timestamp
resolution, late wake latency, and fair-share distributions use tolerances
declared before results are collected. Normalize process IDs and scheduler IDs
only where identity is observationally opaque; do not normalize order or exit
reasons to hide divergence.

Add small systematic interleaving workloads and property-generated sequences
to fixed examples. Concuerror can help enumerate Erlang-level schedules and
produce reproducible failures, but it does not verify ERTS C atomics or browser
Workers.[^concuerror]

## Dirty and async work

Dirty schedulers and an async worker are structurally present even when the
profile admits no dynamic native extensions. Keep them idle except for exact
boot-required work, inventory every job submitted to them, and distinguish the
ERTS async pool from browser Promise operations. Dynamic NIFs/drivers and
arbitrary dirty work remain denied.

If a supposedly excluded operation submits dirty or async work during boot or
Tier 0, the closure is incomplete. Either supply a static audited implementation
with cancellation/teardown semantics or mark the profile blocked; do not proxy
an unknown call through JavaScript.

## In-depth implementation

Expand one dimension at a time: scheduler counts, dirty jobs, run-queue
balancing/work stealing, process priority, priority messages, aliases,
suspended processes, on/off-heap mailbox modes, many-sender contention,
tracing/system messages, millions of timers, and browser lifecycle states.

Qualify foreground, hidden/throttled, machine sleep, freeze/resume, and bfcache
for timer ordering and scheduler progress. If the pthread group cannot safely
survive a state, generation replacement remains correct behavior. Native ERTS
soft-real-time expectations should be reported as measured distributions, not
promised in an environment that can suspend the page.

## Evidence gates

- The target passes the Tier-0 outcome model across repeated seeds and both
  browsers, including systematic interleavings and race sets.
- A CPU-bound workload creates no UI long task and cannot starve a runnable
  latency probe beyond the declared distribution.
- Thread-progress stress does not deadlock while managed/unmanaged runtime
  threads alternate between work and wait.
- Queue saturation, broker cancellation, Worker termination, and timer storms
  neither corrupt signal queues nor accept stale-generation events.
- Traces contain enough sequence, sender/receiver, signal class, scheduler,
  deadline, and generation data to diagnose a mismatch while remaining bounded.

## Principal risks

Thread priorities and affinities can be unavailable or no-ops in browsers.
Background throttling invalidates native latency expectations. Instrumentation
can perturb schedules. A bug in shared wakeup or thread progress can look like
an Erlang deadlock while living below the language. One passing outcome from a
legally nondeterministic race is not semantic equivalence.

## Sources

[^erts-source]: Erlang/OTP Project, [pinned scheduler and process source](../../30-sources/erlang-otp-project-2026-erts-build-runtime-and-source.md).
[^scaling]: Phil Trinder et al., [Scaling Reliably](../../30-sources/trinder-et-al-2017-scaling-reliably-erlang.md).
[^otp-time]: Erlang/OTP Project, [time, timers, testing, and observability](../../30-sources/erlang-otp-project-2026-testing-time-and-runtime-observability.md).
[^concuerror]: Maria Christakis, Alkis Gotovos, and Konstantinos Sagonas, [systematic Erlang concurrency testing](../../30-sources/christakis-et-al-2013-concuerror.md).
