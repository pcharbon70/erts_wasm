---
title: "What is the minimum browser platform contract for upstream ERTS?"
kind: inquiry
created: "2026-09-14"
status: open
tags:
  - architecture
  - browser
  - erlang
  - erts
  - otp
  - porting
  - research-question
  - webassembly
aliases:
  - "Minimum ERTS browser contract inquiry"
---

# What is the minimum browser platform contract for upstream ERTS?

## Question

Can the pinned upstream ERTS interpreter and a version-matched minimal OTP
profile boot, preserve Tier 0 Erlang semantics, remain responsive, and dispose
cleanly using only a small, deny-by-default browser platform contract—without
broad POSIX emulation or a pervasive runtime fork?

## Why this remains open

Source inspection identifies the likely boundary but cannot reveal every
compile-time assumption or runtime dependency. Contemporary ERTS initializes a
broad subsystem graph, requires a real thread implementation, creates multiple
classes of runtime work, loads a nontrivial preload set, and boots through
file-oriented loader concepts. The browser provides Workers, shared Wasm
memory, atomics, clocks, and asynchronous APIs rather than a Unix process.

No ERTS WebAssembly build, boot, semantic comparison, Worker census, memory
profile, or teardown run is present in the corpus.

## Current hypothesis

The smallest credible implementation preserves the upstream interpreter,
loader and code tables, term/process/signal/scheduler machinery, GC and
allocators, atoms, binaries, timers, ETS, essential BIFs, preloads, and enough
matching `kernel` and `stdlib` for applications and supervision.

It adds only:

- a pinned Emscripten configure/build target and same-release native bootstrap;
- an explicit browser system layer for threads, atomics, TLS, clocks, timers,
  poll wakeup, entropy, bounded diagnostics, and fatal exit;
- an immutable manifest-verified release image with virtual root/path/cwd;
- directly supervised Worker ownership and hard generation teardown; and
- bounded request/completion queues to a typed, capability-checked host broker.

JIT, dynamic native loading, distribution, raw sockets, OS processes, shell,
terminal, arbitrary environment/files, mutable code loading, network,
persistence, DOM access, and cryptographic key use remain off by default.

## Competing hypotheses

1. ERTS's Unix assumptions are sufficiently localized that a small new
   `sys`/driver layer plus build fixes can satisfy boot and Tier 0 semantics.
2. Browser pthread scheduling, Worker creation, or main-agent proxying requires
   invasive scheduler changes, making the upstream patch stack too broad.
3. A smaller OTP release profile is possible, but mandatory ERTS startup and
   preload dependencies impose a higher floor than package dependency analysis
   suggests.
4. A queue-and-atomic-wakeup broker is sufficient for browser asynchrony;
   alternatively, a bounded Asyncify or JSPI path may be needed for a small
   number of host calls.
5. The runtime can be hard-disposed only by terminating the whole Worker
   generation, not by relying on graceful ERTS shutdown to join every
   Emscripten thread.

## Experiment matrix

### Gate 0 — target probes

- [ ] Pin OTP, same-release native bootstrap, emsdk, browser, build image, and
  deployment-header revisions.
- [ ] Probe target triples, Autoconf host classification, generated BEAM
  interpreter C, function-pointer signatures, atomics, locks, TLS, condition
  waits, clock APIs, allocator/page APIs, and 32-bit pointer assumptions.
- [ ] Link a pthread Wasm artifact and record the complete import/export list,
  JavaScript glue, Worker assets, initial/maximum memory, and required headers.
- [ ] Show BeamAsm, dynamic NIF/driver loading, process creation, raw sockets,
  and other prohibited authority are absent or deterministically fenced.

### Gate 1 — boot spine

- [ ] Load the exact preloaded modules and one immutable boot script from a
  content-addressed release image.
- [ ] Provide virtual root, path, and current-directory semantics without
  granting ambient browser storage.
- [ ] Reach `init`, start required ERTS system processes, and enter an idle
  scheduler state.
- [ ] Record every Worker/thread creation, owner, wake, idle transition, and
  shutdown hook in both `PROXY_TO_PTHREAD` and outer-runtime-Worker topologies.
- [ ] Demonstrate no ERTS code, blocking wait, or busy loop on the UI agent.

### Gate 2 — semantic minimum

- [ ] Differentially compare the same BEAM tests on pinned native ERTS and
  browser Wasm for terms, arithmetic, exceptions, calls, and interpreted code.
- [ ] Compare process creation, reduction yielding, selective receive, mailbox
  ordering, links, monitors, trapped exits, names, and process death.
- [ ] Compare monotonic time, timers, cancellation, late wake, and clock
  discontinuity behavior.
- [ ] Exercise young/full GC, binaries, literal areas, large mailboxes, ETS
  ownership/heirs, persistent terms, and reclamation after process exit.
- [ ] Boot an application and demonstrate a supervisor restart.
- [ ] Assert deterministic results for every unsupported API in the profile.

### Gate 3 — host boundary and lifecycle

- [ ] Version the broker schema and validate type, size, capability, quota,
  origin, ownership, and runtime generation before allocation or decoding.
- [ ] Test queue saturation, backpressure, timeout, cancellation, duplicate and
  stale completion, malformed payload, and broker/Worker failure.
- [ ] Hard-stop the runtime while idle, CPU-bound, allocating, waiting on a
  timer, and waiting on a host request.
- [ ] Account for and close every Worker, MessagePort, timer, listener, request,
  renderer handle, shared-memory reference, and pthread registry entry.
- [ ] Repeat boot/dispose for a predeclared cycle count and show Worker and
  memory metrics settle without positive slope in Chrome and Firefox.

### Gate 4 — qualified profile

- [ ] Publish the exact ERTS/OTP/Elixir/module/capability compatibility
  manifest and machine-readable unsupported surface.
- [ ] Meet product-approved payload, startup, peak and steady memory,
  responsiveness, latency, and cleanup budgets.
- [ ] Fuzz the loader, BEAM admission, external decoders, broker framing, static
  port adapter, and teardown state transitions under sanitizers where possible.
- [ ] Produce reproducible artifacts, hashes, SBOM, provenance, patch ledger,
  license inventory, and a rehearsed upstream security-update path.

## Measurements to retain

- exact source and toolchain revisions and commands;
- generated and handwritten patch sizes by subsystem;
- Wasm, JavaScript, Worker, boot, and BEAM artifact sizes;
- thread and Worker timelines by runtime generation;
- UI long tasks, idle CPU, wake latency, timer drift, and host-call latency;
- initial, peak, post-GC, and post-disposal memory, including slope across
  cycles;
- native/Wasm semantic deltas and benchmark distributions; and
- every unsupported or negatively tested path.

## Stop conditions

Pause or reject the candidate if boot requires broad POSIX emulation, the
patch stack spreads across common ERTS semantics, a blocking path remains on
the UI agent, Worker ownership is incomplete, external authority cannot be
bounded, Tier 0 semantics diverge, post-disposal resources grow, or product
budgets cannot be met without replacing upstream runtime machinery.

## Resolution criteria

Resolve **yes** only when Gates 0–4 have executable, reviewed evidence for the
pinned profile. Resolve **no** when a stop condition is reproduced and no
small, reviewable platform-layer remedy exists. Keep the inquiry open after a
compile, boot, or UI demonstration alone.

## Related work

- [ERTS architecture and the minimum browser WebAssembly port](../20-notes/erts-architecture-and-minimal-browser-webassembly-port.md)
- [First-party Erlang/OTP ERTS WebAssembly runtime stack](../20-notes/first-party-erlang-otp-erts-webassembly-runtime-stack.md)
- [Minimum ERTS browser-port map](../10-maps/erts-architecture-and-minimal-browser-port.md)
- [ERTS architecture deep-dive journal](../50-journal/2026-09-14-erts-architecture-and-minimal-webassembly-port-deep-dive.md)
